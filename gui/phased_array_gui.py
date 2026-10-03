"""
GUI for the 2D phased array beam error model (phased_array_core.py).

  Run beam errors : pointing error and sidelobe level for the ideal / quantized / quantized+rms cases
  Element maps    : phase needed for azimuth / elevation steering and the ideal / quantized element gains
  Run error sweep : pointing error and sidelobe error vs constant rms gain / phase error
  Save...         : choose a folder, a sub folder named after the parameter values is created in it with
                    results.xlsx (all generated data) and the plots (png)

usage: python gui/phased_array_gui.py
"""
import datetime
import os
import queue
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models'))   # phased_array_core.py
import phased_array_core as core

# (key, label, default) per group; ('taper' is a drop down)
GROUPS = [
    ('Array', [('freq_ghz', 'Frequency (GHz)', '9.5'), ('nx', 'Elements x (azimuth)', '32'), ('ny', 'Elements y (elevation)', '32')]),
    ('Taper', [('taper', 'Taper', 'taylor'), ('taper_sll_db', 'Sidelobe level, dB (taylor, chebyshev)', '30'),
               ('taper_nbar', 'nbar (taylor)', '4'), ('taper_gauss_sigma', 'Sigma (gaussian)', '0.4')]),
    ('Quantization', [('phase_bits', 'Phase bits', '7'), ('gain_bits', 'Gain bits', '6'), ('gain_step_db', 'Gain step (dB)', '0.5')]),
    ('Errors vs attenuation (quantized+rms case)',
     [('err_att_db', 'Attenuation (dB)', '0, 5, 10, 15, 20, 25, 30'),
      ('err_gain_rms_db', 'RMS gain error (dB)', '0.5, 1, 1.5, 2, 1, 1.5, 2'),
      ('err_phase_rms_deg', 'RMS phase error (deg)', '3, 4, 5, 6, 7, 8, 9')]),
    ('Beam error simulation', [('steer_az', 'Steering azimuths (deg)', '0, 20, 40, 60'), ('steer_el', 'Steering elevations (deg)', '0, 20, 40, 60'),
                               ('n_trials', 'Monte Carlo trials', '200'), ('seed', 'Random seed', '1'),
                               ('nfft', 'FFT size', '512'), ('element_cos_exp', 'Element cos exponent', '0')]),
    ('Measured sweep (4th mode, optional)', [('measured_csv', 'rx_Av_iq_sweep csv', '')]),
    ('Element maps', [('map_steer', 'Steering angle (deg)', '30')]),
    ('Error sweep', [('sw_az', 'Steering azimuths (deg)', '0, 30'), ('sw_el', 'Steering elevations (deg)', '0, 30'),
                     ('sw_trials', 'Trials per point', '60'), ('sw_phase', 'Phase rms: start, stop, step (deg)', '3, 10, 1'),
                     ('sw_gain', 'Gain rms: start, stop, step (dB)', '0.5, 2.5, 0.5'),
                     ('hold_phase', 'Phase rms while gain swept (deg)', '6.5'), ('hold_gain', 'Gain rms while phase swept (dB)', '1.5')]),
]


def parse_list(text, cast=float):
    return [cast(x) for x in re.split(r'[,\s;]+', text.strip()) if x]


def parse_range(text):
    start, stop, step = parse_list(text)
    return np.arange(start, stop + step / 2, step)


class PlotTab(ttk.Frame):
    """A matplotlib figure with a toolbar. show(builder) clears the figure and lets builder(fig) draw on it."""

    def __init__(self, parent, figsize=(8, 6)):
        super().__init__(parent)
        self.fig = Figure(figsize=figsize)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        NavigationToolbar2Tk(self.canvas, self).update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def show(self, builder):
        self.fig.clear()
        builder(self.fig)
        self.canvas.draw()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Phased array beam error analysis')
        self.geometry('1500x900')
        self.vars = {}
        self.cfg = self.arr = self.results = self.maps = self.sweep = None
        self.run_info = {}                      # parameters of the last runs, for the folder name and the Parameters sheet
        self.messages = queue.Queue()
        self.busy = False
        self._build_params()
        self._build_results()
        self.after(100, self._poll)

    # ---------------- layout ----------------
    def _build_params(self):
        left = ttk.Frame(self, width=432)
        left.pack(side='left', fill='y', padx=6, pady=6)
        canvas = tk.Canvas(left, width=432, highlightthickness=0)
        scroll = ttk.Scrollbar(left, orient='vertical', command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=scroll.set)
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(-1 * (e.delta // 120), 'units'))
        for title, fields in GROUPS:
            box = ttk.LabelFrame(inner, text=title)
            box.pack(fill='x', padx=4, pady=4)
            for r, (key, label, default) in enumerate(fields):
                ttk.Label(box, text=label).grid(row=r, column=0, sticky='w', padx=4, pady=1)
                var = tk.StringVar(value=default)
                self.vars[key] = var
                if key == 'taper':
                    ttk.Combobox(box, textvariable=var, values=core.TAPERS, state='readonly', width=26).grid(row=r, column=1, padx=4, pady=1)
                else:
                    ttk.Entry(box, textvariable=var, width=30).grid(row=r, column=1, padx=4, pady=1)
            if title.startswith('Measured sweep'):
                row = ttk.Frame(box)
                row.grid(row=len(fields), column=0, columnspan=2, sticky='w', padx=4, pady=2)
                ttk.Button(row, text='Browse...', command=self.browse_measured).pack(side='left')
                ttk.Button(row, text='Clear', command=lambda: self.vars['measured_csv'].set('')).pack(side='left', padx=4)
        bottom = ttk.Frame(left)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='top', fill='both', expand=True)
        bottom.pack(side='bottom', fill='x', pady=6)
        self.buttons = []
        for text, cmd in (('Run beam errors', self.run_beam), ('Element maps', self.run_maps), ('Run error sweep', self.run_sweep),
                          ('Run all', self.run_all), ('Save...', self.save)):
            b = ttk.Button(bottom, text=text, command=cmd)
            b.pack(fill='x', padx=4, pady=2)
            self.buttons.append(b)
        self.progress = ttk.Progressbar(bottom, mode='determinate', maximum=100)
        self.progress.pack(fill='x', padx=4, pady=(6, 2))
        self.status = tk.StringVar(value='Ready')
        ttk.Label(bottom, textvariable=self.status, wraplength=408).pack(fill='x', padx=4)

    def _build_results(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side='right', fill='both', expand=True, padx=6, pady=6)
        table_tab = ttk.Frame(self.tabs)
        self.tree = ttk.Treeview(table_tab, show='headings')
        ys = ttk.Scrollbar(table_tab, orient='vertical', command=self.tree.yview)
        xs = ttk.Scrollbar(table_tab, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side='right', fill='y')
        xs.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)
        self.tabs.add(table_tab, text='Beam errors')
        cuts_tab = ttk.Frame(self.tabs)
        top = ttk.Frame(cuts_tab)
        top.pack(fill='x')
        top.columnconfigure(1, weight=1)
        self.cut_axes = {}                      # 'az' / 'el' -> dict(values, scale, label)
        for r, (key, text) in enumerate((('az', 'Azimuth'), ('el', 'Elevation'))):
            ttk.Label(top, text=text + ':').grid(row=r, column=0, sticky='w', padx=4, pady=2)
            scale = ttk.Scale(top, from_=0, to=0, orient='horizontal', command=lambda v, k=key: self._on_cut_slider(k, v))
            scale.grid(row=r, column=1, sticky='ew', padx=4)
            label = ttk.Label(top, text='-', width=10)
            label.grid(row=r, column=2, padx=4)
            self.cut_axes[key] = dict(values=[], scale=scale, label=label)
        self.cut_polar = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text='Polar plot', variable=self.cut_polar, command=self._draw_cuts).grid(row=2, column=0, columnspan=2, sticky='w', padx=4)
        self.cut_note = ttk.Label(top, text='')
        self.cut_note.grid(row=3, column=0, columnspan=3, sticky='w', padx=4)
        self.cuts_plot = PlotTab(cuts_tab)
        self.cuts_plot.pack(fill='both', expand=True)
        self.tabs.add(cuts_tab, text='Pattern cuts')
        self.summary_plot = PlotTab(self.tabs)
        self.tabs.add(self.summary_plot, text='Summary')
        self.maps_plot = PlotTab(self.tabs)
        self.tabs.add(self.maps_plot, text='Element maps')
        self.sweep_plot = PlotTab(self.tabs)
        self.tabs.add(self.sweep_plot, text='Error sweep')

    # ---------------- parameters ----------------
    def browse_measured(self):
        path = filedialog.askopenfilename(title='Measured sweep csv (rx_Av_iq_sweep.py, sweep both)', filetypes=[('csv', '*.csv'), ('all files', '*.*')])
        if path:
            self.vars['measured_csv'].set(path)

    def read_cfg(self):
        v = {k: x.get() for k, x in self.vars.items()}
        return core.ArrayConfig(
            freq_ghz=float(v['freq_ghz']), nx=int(v['nx']), ny=int(v['ny']), taper=v['taper'], taper_sll_db=float(v['taper_sll_db']),
            taper_nbar=int(v['taper_nbar']), taper_gauss_sigma=float(v['taper_gauss_sigma']), phase_bits=float(v['phase_bits']),
            gain_bits=int(v['gain_bits']), gain_step_db=float(v['gain_step_db']), err_att_db=parse_list(v['err_att_db']),
            err_gain_rms_db=parse_list(v['err_gain_rms_db']), err_phase_rms_deg=parse_list(v['err_phase_rms_deg']),
            nfft=int(v['nfft']), element_cos_exp=float(v['element_cos_exp']), measured_csv=v['measured_csv'].strip())

    def _prepare(self):
        """Read the parameters and (re)build the array. Returns False when a value is invalid."""
        try:
            cfg = self.read_cfg()
            if not (len(cfg.err_att_db) == len(cfg.err_gain_rms_db) == len(cfg.err_phase_rms_deg)):
                raise ValueError('the three error table lists must have the same length')
            self.cfg, self.arr = cfg, core.PhasedArray(cfg)
            return True
        except Exception as e:
            messagebox.showerror('Invalid parameters', str(e))
            return False

    # ---------------- running (worker thread + progress) ----------------
    def _set_busy(self, busy):
        self.busy = busy
        for b in self.buttons:
            b.state(['disabled'] if busy else ['!disabled'])

    def _async(self, work, done, label, sync=False):
        """Run work(progress) in a thread and call done(result) in the GUI thread. sync=True runs inline (used by tests)."""
        if sync:
            done(work(lambda d, t: None))
            return
        self._set_busy(True)
        self.status.set(label)
        self.progress['value'] = 0
        self.t_start = time.time()

        def target():
            try:
                self.messages.put(('done', done, work(lambda d, t: self.messages.put(('progress', d, t)))))
            except Exception as e:
                self.messages.put(('error', e))
        threading.Thread(target=target, daemon=True).start()

    def _poll(self):
        last_progress = None
        try:
            while True:
                msg = self.messages.get_nowait()
                if msg[0] == 'progress':
                    last_progress = msg
                elif msg[0] == 'done':
                    self._set_busy(False)
                    self.progress['value'] = 100
                    self.status.set('Done')
                    msg[1](msg[2])
                elif msg[0] == 'error':
                    self._set_busy(False)
                    self.status.set('Error')
                    messagebox.showerror('Error', str(msg[1]))
        except queue.Empty:
            pass
        if last_progress:
            done, total = last_progress[1], last_progress[2]
            etc = datetime.timedelta(seconds=round((time.time() - self.t_start) / done * (total - done)))
            self.progress['value'] = 100 * done / total
            self.status.set(f'{100 * done // total}%  ({done} / {total} patterns)   ETC {etc}')
        self.after(100, self._poll)

    # ---------------- actions ----------------
    def run_beam(self, sync=False, then=None):
        if not self._prepare():
            return
        try:
            az, el = parse_list(self.vars['steer_az'].get()), parse_list(self.vars['steer_el'].get())
            n_trials, seed = int(self.vars['n_trials'].get()), int(self.vars['seed'].get())
        except ValueError as e:
            messagebox.showerror('Invalid parameters', str(e))
            return
        steers = core.steering_list(az, el)
        arr = self.arr
        self.run_info.update(az_list=az, el_list=el, n_trials=n_trials, cfg=self.cfg)

        def done(res):
            self.results = res
            self._fill_table(res.table())
            self._setup_cut_sliders(res)
            self._draw_cuts()
            self.summary_plot.show(lambda fig: core.fig_summary(res, fig=fig))
            if then:
                then()
        self._async(lambda cb: arr.simulate(steers, n_trials, seed, cb), done, 'Running beam errors...', sync)

    def run_maps(self, sync=False, then=None):
        if not self._prepare():
            return
        try:
            deg = float(self.vars['map_steer'].get())
        except ValueError as e:
            messagebox.showerror('Invalid parameters', str(e))
            return
        self.maps = self.arr.element_maps(deg)
        c = self.cfg
        self.run_info['maps_cfg'] = c
        self.maps_plot.show(lambda fig: core.fig_element_maps(self.maps, c.taper, c.gain_step_db, c.gain_bits, fig=fig))
        self.status.set('Element maps done')
        if then:
            then()

    def run_sweep(self, sync=False, then=None):
        if not self._prepare():
            return
        try:
            steers = core.steering_list(parse_list(self.vars['sw_az'].get()), parse_list(self.vars['sw_el'].get()))
            n, seed = int(self.vars['sw_trials'].get()), int(self.vars['seed'].get())
            phase, gain = parse_range(self.vars['sw_phase'].get()), parse_range(self.vars['sw_gain'].get())
            hp, hg = float(self.vars['hold_phase'].get()), float(self.vars['hold_gain'].get())
        except ValueError as e:
            messagebox.showerror('Invalid parameters', str(e))
            return
        c = self.cfg
        arr = self.arr
        title = f'{c.nx}x{c.ny}, {c.taper} taper'
        self.run_info['sweep_cfg'] = c
        self.run_info['sweep'] = dict(steers=steers, trials=n, phase=[float(x) for x in phase], gain=[float(x) for x in gain], hold_phase=hp, hold_gain=hg)

        def done(res):
            self.sweep = (res[0], res[1], title)
            self.sweep_plot.show(lambda fig: core.fig_error_sweep(res[0], res[1], title, fig=fig))
            if then:
                then()
        self._async(lambda cb: arr.error_sweep(steers, n, seed, phase, gain, hp, hg, cb), done, 'Running error sweep...', sync)

    def run_all(self):
        self.run_beam(then=lambda: self.run_maps(then=self.run_sweep))

    def _fill_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col != 'Case' else 120, anchor='center')
        for _, row in df.iterrows():
            self.tree.insert('', 'end', values=[f'{x:.4f}' if isinstance(x, float) else x for x in row])

    def _setup_cut_sliders(self, res):
        """The sliders step through the simulated azimuths / elevations."""
        for i, key in enumerate(('az', 'el')):      # set both value lists first: moving a slider triggers a redraw
            self.cut_axes[key]['values'] = sorted({s[i] for s in res.steers})
        for key in ('az', 'el'):
            ax = self.cut_axes[key]
            ax['scale'].configure(to=max(len(ax['values']) - 1, 0))
            ax['scale'].set(0)
            ax['label'].configure(text=f"{ax['values'][0]:g} deg")

    def _cut_index(self):
        """Index into results.steers for the slider positions, or None when that combination was not simulated."""
        pick = []
        for key in ('az', 'el'):
            ax = self.cut_axes[key]
            pick.append(ax['values'][min(int(round(float(ax['scale'].get()))), len(ax['values']) - 1)])
        try:
            return self.results.steers.index(tuple(pick))
        except ValueError:
            return None

    def _on_cut_slider(self, key, value):
        ax = self.cut_axes[key]
        if not ax['values']:
            return
        i = min(int(round(float(value))), len(ax['values']) - 1)
        ax['label'].configure(text=f"{ax['values'][i]:g} deg")
        if abs(float(value) - i) > 1e-9:
            ax['scale'].set(i)                  # snap to the simulated value (re-enters this callback)
            return
        self._draw_cuts()

    def _draw_cuts(self):
        if self.results is None or not all(self.cut_axes[k]['values'] for k in ('az', 'el')):
            return
        s = self._cut_index()
        if s is None:
            self.cut_note.configure(text='This azimuth / elevation combination is outside the visible region (not simulated).')
            return
        self.cut_note.configure(text='')
        self.cuts_plot.show(lambda fig: core.fig_pattern_cuts(self.results, s, fig=fig, polar=self.cut_polar.get()))

    # ---------------- save ----------------
    def save(self, base_dir=None):
        if self.results is None and self.maps is None and self.sweep is None:
            messagebox.showinfo('Nothing to save', 'Run at least one analysis first.')
            return
        base_dir = base_dir or filedialog.askdirectory(title='Choose the folder to save into')
        if not base_dir:
            return
        info = self.run_info
        cfg = info.get('cfg') or info.get('maps_cfg') or info.get('sweep_cfg') or self.cfg
        extra = {}
        if self.results is not None:
            extra.update(steering_azimuths=info['az_list'], steering_elevations=info['el_list'], n_trials=info['n_trials'])
        if self.maps is not None:
            extra['element map steering (deg)'] = self.maps['steer_deg']
        if self.sweep is not None:
            extra.update({f'sweep {k}': v for k, v in info['sweep'].items()})
        az = info.get('az_list', parse_list(self.vars['steer_az'].get()))
        el = info.get('el_list', parse_list(self.vars['steer_el'].get()))
        try:
            folder = core.save_results(base_dir, cfg, az, el, info.get('n_trials', int(self.vars['n_trials'].get())),
                                       self.results, self.maps, self.sweep, extra)
        except Exception as e:
            messagebox.showerror('Save failed', str(e))
            return None
        renamed = os.path.basename(folder) != core.folder_name(cfg, az, el, info.get('n_trials', int(self.vars['n_trials'].get())))
        if renamed:
            self.status.set(f'Saved to {folder} (timestamp added: the folder already existed)')
            messagebox.showwarning('Saved - folder name changed', 'A folder with this name ALREADY EXISTED, so a TIMESTAMP WAS ADDED to the '
                                   f'name. results.xlsx and the plots are in:\n\n{folder}')
        else:
            self.status.set(f'Saved to {folder}')
            messagebox.showinfo('Saved', f'Saved results.xlsx and the plots in:\n{folder}')
        return folder


if __name__ == '__main__':
    App().mainloop()
