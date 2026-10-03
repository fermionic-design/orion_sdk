"""
Core of the 2D phased array beam error model: no globals, no top-level execution, no GUI, so it can be driven
from scripts (phased_array_beam_errors.py, phased_array_error_sweep.py) or from the GUI (gui/phased_array_gui.py).

Geometry: nx x ny elements in the x-y plane, spacing lambda/2 (the pattern does not depend on the frequency, freq
only sets the physical spacing), boresight along z. Direction cosines: u = sin(az) cos(el), v = sin(el).
Array factor: AF(u, v) = sum a_mn exp(j pi ((m - cx) (u - u0) + (n - cy) (v - v0))), computed with a zero padded FFT.

Cases: 'ideal' (floating point), 'quantized' (phase_bits, gain_bits / gain_step_db), 'quantized+rms' (quantized plus random
gain / phase errors whose rms depends on the attenuation state of the element, Monte Carlo).
Optional 4th case 'measured': every element uses the measured gain / phase of the (gain code, phase state) the hardware would be
set to, taken from a rx_Av_iq_sweep.py csv (cfg.measured_csv); deterministic, no random errors.

Pointing error = peak direction found in the pattern - commanded direction (parabolic peak refinement).
Peak sidelobe level = highest point outside the main lobe (the region around the peak that falls monotonically to the
first nulls), in dB below the peak. Sidelobe error = sidelobe level of the case - sidelobe level of the ideal case.
"""
import datetime
import os
import re
import warnings
from collections import deque
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy.ndimage import binary_dilation
from scipy.signal import windows

TAPERS = ('uniform', 'taylor', 'chebyshev', 'hamming', 'hann', 'blackman', 'cosine', 'gaussian')
CASES = ('ideal', 'quantized', 'quantized+rms')   # a 4th case, 'measured', is added when a measured sweep csv is given


@dataclass
class ArrayConfig:
    freq_ghz: float = 9.5
    nx: int = 32                       # elements along x (azimuth)
    ny: int = 32                       # elements along y (elevation)
    taper: str = 'taylor'
    taper_sll_db: float = 30           # taylor / chebyshev
    taper_nbar: int = 4                # taylor
    taper_gauss_sigma: float = 0.4     # gaussian, std as a fraction of the half aperture
    phase_bits: float = 7              # phase states = 2**phase_bits (can be fractional)
    gain_bits: int = 6                 # gain (attenuation) states = 2**gain_bits
    gain_step_db: float = 0.5          # attenuation step, state 0 = no attenuation
    # rms errors vs the attenuation state of the element (interpolated, held outside the table)
    err_att_db: list = field(default_factory=lambda: [0, 5, 10, 15, 20, 25, 30])
    err_gain_rms_db: list = field(default_factory=lambda: [0.5, 1.0, 1.5, 2.0, 1.0, 1.5, 2.0])
    err_phase_rms_deg: list = field(default_factory=lambda: [3, 4, 5, 6, 7, 8, 9])
    nfft: int = 512                    # pattern grid is nfft x nfft over u, v in [-1, 1)
    element_cos_exp: float = 0.0       # element pattern cos(theta)**exp (0 = isotropic)
    measured_csv: str = ''             # rx_Av_iq_sweep.py csv (sweep 'both'): adds the 'measured' case


def steering_list(az_list, el_list):
    """All (az, el) combinations that are in the visible region."""
    return [(az, el) for el in el_list for az in az_list
            if np.sin(np.radians(az)) ** 2 * np.cos(np.radians(el)) ** 2 + np.sin(np.radians(el)) ** 2 < 1]


def taper_window(cfg, n):
    t = cfg.taper
    warnings.filterwarnings('ignore', message='This window is not suitable for spectral analysis')
    if t == 'uniform':
        return np.ones(n)
    if t == 'taylor':
        return windows.taylor(n, nbar=cfg.taper_nbar, sll=cfg.taper_sll_db, norm=False)
    if t == 'chebyshev':
        return windows.chebwin(n, at=cfg.taper_sll_db)
    if t == 'hamming':
        return windows.hamming(n)
    if t == 'hann':
        return windows.hann(n + 2)[1:-1]            # no zero edge elements
    if t == 'blackman':
        return windows.blackman(n + 2)[1:-1]
    if t == 'cosine':
        return windows.cosine(n)
    if t == 'gaussian':
        return windows.gaussian(n, std=cfg.taper_gauss_sigma * (n - 1) / 2)
    raise ValueError(f'unknown taper {t}')


class MeasuredSweep:
    """Measured gain / phase of one element for every (gain code, phase state): the csv of rx_Av_iq_sweep.py with sweep = 'both'.
    Gain is relative to the mean gain at the first gain code, phase is relative to the first gain code / phase state."""

    def __init__(self, csv_path):
        d = pd.read_csv(csv_path)
        g = d.pivot(index='g_idx', columns='p_idx', values='Gain dB').sort_index().sort_index(axis=1)
        p = d.pivot(index='g_idx', columns='p_idx', values='Phase deg').sort_index().sort_index(axis=1)
        if g.isna().any().any() or p.isna().any().any():
            raise ValueError('the sweep csv does not cover every gain code / phase state')
        self.g_codes = g.index.values
        if not np.all(np.diff(self.g_codes) == 1):
            raise ValueError('the gain codes of the sweep csv must be consecutive (g step 1)')
        self.n_states = g.shape[1]                                   # phase states, state s = p_idx - first p_idx
        self.gain_rel_db = (g - g.iloc[0].mean()).values             # [gain code, phase state]
        self.phase_deg = p.values
        self.name = os.path.basename(csv_path)

    def weights(self, phase_deg, att_db, gain_step_db):
        """Complex weights of elements commanded to phase_deg (any shape) and att_db attenuation (dB)."""
        gi = np.clip(np.round(att_db / gain_step_db).astype(int), self.g_codes[0], self.g_codes[-1]) - self.g_codes[0]
        si = np.round((phase_deg % 360) / (360 / self.n_states)).astype(int) % self.n_states
        return 10 ** (self.gain_rel_db[gi, si] / 20) * np.exp(1j * np.radians(self.phase_deg[gi, si]))


class PhasedArray:
    def __init__(self, cfg):
        self.cfg = cfg
        self.cx, self.cy = (cfg.nx - 1) / 2, (cfg.ny - 1) / 2
        self.X, self.Y = np.meshgrid(np.arange(cfg.nx) - self.cx, np.arange(cfg.ny) - self.cy)   # [ny, nx]
        self.ph_step = 360 / 2 ** cfg.phase_bits
        self.max_att = (2 ** cfg.gain_bits - 1) * cfg.gain_step_db
        n = cfg.nfft
        self.u_grid = np.arange(n) * 2 / n - 1
        U, V = np.meshgrid(self.u_grid, self.u_grid)                                              # [v, u]
        self.mask = U ** 2 + V ** 2 < 1
        self.elem = np.where(self.mask, np.sqrt(np.clip(1 - U ** 2 - V ** 2, 0, 1)) ** cfg.element_cos_exp, 0)
        a = np.outer(taper_window(cfg, cfg.ny), taper_window(cfg, cfg.nx))
        self.a_taper = a / a.max()                                                                # strongest element = 0 dB
        self.measured = MeasuredSweep(cfg.measured_csv) if cfg.measured_csv else None
        self.cases = CASES + (('measured',) if self.measured else ())

    # ---------------- element settings ----------------
    def quantized_attenuation(self):
        """Attenuation state (dB) of every element after quantization."""
        c = self.cfg
        return np.clip(np.round(-20 * np.log10(self.a_taper) / c.gain_step_db) * c.gain_step_db, 0, self.max_att)

    def element_weights(self, az_deg, el_deg, case, rng, err=None):
        """Complex element weights for a beam steered to (az, el). err = (att_db, gain_rms_db, phase_rms_deg) overrides the tables."""
        c = self.cfg
        u0 = np.sin(np.radians(az_deg)) * np.cos(np.radians(el_deg))
        v0 = np.sin(np.radians(el_deg))
        phase = -180 * (self.X * u0 + self.Y * v0)                                                # degrees
        if case == 'ideal':
            return self.a_taper * np.exp(1j * np.radians(phase))
        if case == 'measured':                       # measured response of the state the hardware would be set to
            return self.measured.weights(phase, self.quantized_attenuation(), c.gain_step_db)
        phase = np.round((phase % 360) / self.ph_step) * self.ph_step
        att = self.quantized_attenuation()
        amp = 10 ** (-att / 20)
        if case == 'quantized+rms':
            a_pts, g_rms, p_rms = err if err is not None else (c.err_att_db, c.err_gain_rms_db, c.err_phase_rms_deg)
            amp = amp * 10 ** (rng.normal(size=amp.shape) * np.interp(att, a_pts, g_rms) / 20)
            phase = phase + rng.normal(size=amp.shape) * np.interp(att, a_pts, p_rms)
        return amp * np.exp(1j * np.radians(phase))

    # ---------------- pattern ----------------
    def _main_lobe(self, P, i0, j0):
        n = self.cfg.nfft
        ml = np.zeros(P.shape, bool)
        ml[i0, j0] = True
        queue = deque([(i0, j0)])
        while queue:
            i, j = queue.popleft()
            lim = P[i, j] * 1.01
            for ii, jj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= ii < n and 0 <= jj < n and not ml[ii, jj] and self.mask[ii, jj] and P[ii, jj] <= lim:
                    ml[ii, jj] = True
                    queue.append((ii, jj))
        return binary_dilation(ml, iterations=2)

    def analyze(self, w):
        """Pattern metrics of a set of weights: az, el of the peak (deg), sidelobe level (dBc), peak value, pattern P, peak index."""
        n = self.cfg.nfft
        P = np.abs(np.fft.fftshift(np.fft.ifft2(w, s=(n, n)))) * n ** 2 * self.elem                # [v, u]
        i, j = np.unravel_index(np.argmax(P), P.shape)
        di = dj = 0.0
        if 0 < i < n - 1 and 0 < j < n - 1:                                                       # parabolic peak refinement
            d = lambda a, b, c: 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
            di, dj = d(P[i - 1, j], P[i, j], P[i + 1, j]), d(P[i, j - 1], P[i, j], P[i, j + 1])
        u_p, v_p = self.u_grid[j] + dj * 2 / n, self.u_grid[i] + di * 2 / n
        el = np.degrees(np.arcsin(np.clip(v_p, -1, 1)))
        az = np.degrees(np.arcsin(np.clip(u_p / np.cos(np.radians(el)), -1, 1)))
        side = self.mask & ~self._main_lobe(P, i, j)
        sll = 20 * np.log10(P[side].max() / P[i, j])
        return dict(az=az, el=el, sll=sll, peak=P[i, j], P=P, i=i, j=j)

    def cuts(self, P, i, j, peak_ref):
        """Azimuth and elevation cuts (deg, dB relative to peak_ref) through the pattern peak."""
        db = 20 * np.log10(np.maximum(P, 1e-12) / peak_ref)
        cos_el = np.cos(np.arcsin(self.u_grid[i]))
        ok = np.abs(self.u_grid / cos_el) < 1
        col = self.mask[:, j]
        return dict(az_axis=np.degrees(np.arcsin(self.u_grid[ok] / cos_el)), az_db=db[i, ok],
                    el_axis=np.degrees(np.arcsin(self.u_grid[col])), el_db=db[col, j])

    # ---------------- simulations ----------------
    def simulate(self, steers, n_trials=200, seed=1, progress=None):
        """Beam errors for every steering angle and case. progress(done, total) is called after every pattern."""
        rng = np.random.default_rng(seed)
        total = len(steers) * (len(self.cases) - 1 + n_trials)
        done = 0
        data = {}
        for s, (az0, el0) in enumerate(steers):
            for case in self.cases:
                out = []
                for _ in range(n_trials if case == 'quantized+rms' else 1):
                    out.append(self.analyze(self.element_weights(az0, el0, case, rng)))
                    done += 1
                    if progress:
                        progress(done, total)
                ref_peak = data['ideal', s]['peak'][0] if case != 'ideal' else out[0]['peak']
                data[case, s] = dict(az_err=np.array([o['az'] - az0 for o in out]), el_err=np.array([o['el'] - el0 for o in out]),
                                     sll=np.array([o['sll'] for o in out]), peak=np.array([o['peak'] for o in out]),
                                     cuts=self.cuts(out[0]['P'], out[0]['i'], out[0]['j'], ref_peak))
        return BeamResults(list(steers), data, n_trials, self.cases)

    def error_sweep(self, steers, n_trials, seed, phase_rms_deg, gain_rms_db, hold_phase_deg, hold_gain_db, progress=None):
        """Pointing error and sidelobe error vs constant rms gain / phase error (independent of the attenuation state).
        Returns (vs_gain, vs_phase) DataFrames."""
        rng0 = np.random.default_rng(seed)
        ideal_sll = {s: self.analyze(self.element_weights(*s, 'ideal', rng0))['sll'] for s in steers}
        total = (len(phase_rms_deg) + len(gain_rms_db)) * len(steers) * n_trials
        done = 0

        def evaluate(g_rms, p_rms):
            nonlocal done
            rng = np.random.default_rng(seed)
            err = ([0, 100], [g_rms, g_rms], [p_rms, p_rms])
            point, dsll = [], []
            for s in steers:
                for _ in range(n_trials):
                    o = self.analyze(self.element_weights(*s, 'quantized+rms', rng, err))
                    point.append((o['az'] - s[0]) ** 2 + (o['el'] - s[1]) ** 2)
                    dsll.append(o['sll'] - ideal_sll[s])
                    done += 1
                    if progress:
                        progress(done, total)
            return np.sqrt(np.mean(point)), np.mean(dsll)

        vg = [evaluate(g, hold_phase_deg) for g in gain_rms_db]
        vp = [evaluate(hold_gain_db, p) for p in phase_rms_deg]
        cols = ['Pointing error rms (deg)', 'Sidelobe error (dB)']
        vs_gain = pd.DataFrame(vg, columns=cols, index=pd.Index(list(gain_rms_db), name='RMS gain error (dB)')).reset_index()
        vs_phase = pd.DataFrame(vp, columns=cols, index=pd.Index(list(phase_rms_deg), name='RMS phase error (deg)')).reset_index()
        vs_gain['RMS phase error held (deg)'] = hold_phase_deg
        vs_phase['RMS gain error held (dB)'] = hold_gain_db
        return vs_gain, vs_phase

    # ---------------- element maps ----------------
    def element_maps(self, steer_deg):
        """Phase needed to steer steer_deg in azimuth / in elevation, and the ideal / quantized gain of every element."""
        def phase_for(az, el):
            u0, v0 = np.sin(np.radians(az)) * np.cos(np.radians(el)), np.sin(np.radians(el))
            return (-180 * (self.X * u0 + self.Y * v0)) % 360
        return dict(phase_az=phase_for(steer_deg, 0), phase_el=phase_for(0, steer_deg), steer_deg=steer_deg,
                    gain_ideal_db=20 * np.log10(self.a_taper), gain_quant_db=-self.quantized_attenuation())


@dataclass
class BeamResults:
    steers: list
    data: dict          # (case, steer index) -> dict of per-trial arrays and pattern cuts
    n_trials: int
    cases: tuple = CASES

    def table(self):
        """One row per steering angle and case."""
        rows = []
        for s, (az0, el0) in enumerate(self.steers):
            ideal = self.data['ideal', s]
            for case in self.cases:
                r = self.data[case, s]
                row = {'Steer az (deg)': az0, 'Steer el (deg)': el0, 'Case': case}
                for name, e in (('az', r['az_err']), ('el', r['el_err'])):
                    row[f'{name} err mean (deg)'] = e.mean()
                    row[f'{name} err rms (deg)'] = np.sqrt(np.mean(e ** 2))
                    row[f'{name} err p95 (deg)'] = np.percentile(np.abs(e), 95)
                row['SLL mean (dBc)'] = r['sll'].mean()
                row['SLL worst (dBc)'] = r['sll'].max()
                row['SLL error mean (dB)'] = (r['sll'] - ideal['sll']).mean()
                row['Peak loss (dB)'] = (20 * np.log10(r['peak'] / ideal['peak'][0])).mean()
                rows.append(row)
        return pd.DataFrame(rows)

    def trials(self):
        """One row per trial."""
        rows = []
        for s, (az0, el0) in enumerate(self.steers):
            for case in self.cases:
                r = self.data[case, s]
                for k in range(len(r['sll'])):
                    rows.append({'Steer az (deg)': az0, 'Steer el (deg)': el0, 'Case': case, 'Trial': k,
                                 'az err (deg)': r['az_err'][k], 'el err (deg)': r['el_err'][k], 'SLL (dBc)': r['sll'][k],
                                 'Peak (relative to ideal, dB)': 20 * np.log10(r['peak'][k] / self.data['ideal', s]['peak'][0])})
        return pd.DataFrame(rows)

    def cuts_table(self, s):
        """Pattern cuts of steering index s as two DataFrames (azimuth cut, elevation cut), one column per case."""
        az = pd.DataFrame({'Azimuth (deg)': self.data['ideal', s]['cuts']['az_axis']})
        el = pd.DataFrame({'Elevation (deg)': self.data['ideal', s]['cuts']['el_axis']})
        for case in self.cases:
            az[case + ' (dB)'] = self.data[case, s]['cuts']['az_db']
            el[case + ' (dB)'] = self.data[case, s]['cuts']['el_db']
        return az, el


# ---------------- figures (matplotlib Figure objects, nothing is shown here) ----------------
def fig_pattern_cuts(results, s, fig=None, polar=False):
    fig = fig or Figure(figsize=(13, 5))
    az0, el0 = results.steers[s]
    if polar:
        ax = fig.subplots(1, 2, subplot_kw={'projection': 'polar'})
        for case in results.cases:
            c = results.data[case, s]['cuts']
            ax[0].plot(np.radians(c['az_axis']), c['az_db'], label=case)
            ax[1].plot(np.radians(c['el_axis']), c['el_db'], label=case)
        for a, name in zip(ax, ('azimuth cut', 'elevation cut')):
            a.set_theta_zero_location('N')
            a.set_theta_direction(-1)
            a.set_thetamin(-90)                 # fixed half circle so the plots keep the same size for every cut
            a.set_thetamax(90)
            a.set_rlim(-60, 3)
            a.set_rlabel_position(90)
            a.grid(True)
            a.legend(loc='lower left', fontsize=8)
            a.set_title(f'{name} (dB), steered to az {az0:g}, el {el0:g} deg')
        fig.tight_layout()
        return fig
    ax = fig.subplots(1, 2)
    for case in results.cases:
        c = results.data[case, s]['cuts']
        ax[0].plot(c['az_axis'], c['az_db'], label=case)
        ax[1].plot(c['el_axis'], c['el_db'], label=case)
    for a, name, xl in zip(ax, ('azimuth cut', 'elevation cut'), ('Azimuth (deg)', 'Elevation (deg)')):
        a.set_xlabel(xl)
        a.set_ylabel('Relative power (dB)')
        a.set_ylim(-60, 3)
        a.grid(True)
        a.legend()
        a.set_title(f'{name} through the peak, steered to az {az0:g}, el {el0:g} deg')
    fig.tight_layout()
    return fig


def fig_summary(results, fig=None):
    fig = fig or Figure(figsize=(10, 9))
    ax = fig.subplots(3, 1, sharex=True)
    x = np.arange(len(results.steers))
    for k, case in enumerate(results.cases):
        w = 0.8 / len(results.cases)
        off = (k - (len(results.cases) - 1) / 2) * w
        ax[0].bar(x + off, [np.sqrt(np.mean(results.data[case, s]['az_err'] ** 2)) for s in x], w, label=case)
        ax[1].bar(x + off, [np.sqrt(np.mean(results.data[case, s]['el_err'] ** 2)) for s in x], w, label=case)
        ax[2].bar(x + off, [results.data[case, s]['sll'].mean() for s in x], w, label=case)
    ax[0].set_ylabel('Azimuth error rms (deg)')
    ax[1].set_ylabel('Elevation error rms (deg)')
    ax[2].set_ylabel('Peak SLL (dBc)')
    ax[2].set_xticks(x, [f'{a:g},{e:g}' for a, e in results.steers], rotation=60 if len(x) > 8 else 0, fontsize=8)
    ax[2].set_xlabel('Commanded azimuth, elevation (deg)')
    for a in ax:
        a.grid(True, axis='y')
        a.legend(fontsize=8)
    fig.tight_layout()
    return fig


def fig_element_maps(maps, taper_name, gain_step_db, gain_bits, fig=None):
    fig = fig or Figure(figsize=(12, 10))
    ax = fig.subplots(2, 2)
    ny, nx = maps['phase_az'].shape
    cx, cy = (nx - 1) / 2, (ny - 1) / 2
    extent = [-cx - 0.5, cx + 0.5, -cy - 0.5, cy + 0.5]                      # element position in units of lambda/2
    d = maps['steer_deg']
    for a, name, ph in zip(ax[0], (f'Phase for {d:g} deg azimuth steering', f'Phase for {d:g} deg elevation steering'),
                           (maps['phase_az'], maps['phase_el'])):
        im = a.imshow(ph, origin='lower', extent=extent, cmap='twilight', vmin=0, vmax=360)
        a.set_title(name)
        fig.colorbar(im, ax=a, label='Phase (deg)')
    for a, name, g in zip(ax[1], (f'Gain, ideal ({taper_name} taper)', f'Gain, quantized ({gain_step_db:g} dB steps, {gain_bits} bits)'),
                          (maps['gain_ideal_db'], maps['gain_quant_db'])):
        im = a.imshow(g, origin='lower', extent=extent, cmap='viridis', vmin=min(g.min(), -1), vmax=0)
        a.set_title(name)
        fig.colorbar(im, ax=a, label='Relative gain (dB)')
    for a in ax.ravel():
        a.set_xlabel('x element position (lambda/2)')
        a.set_ylabel('y element position (lambda/2)')
    fig.tight_layout()
    return fig


def fig_error_sweep(vs_gain, vs_phase, title, fig=None):
    fig = fig or Figure(figsize=(13, 5))
    ax = fig.subplots(1, 2)
    for a, df, xcol, hold in ((ax[0], vs_gain, 'RMS gain error (dB)', f"phase error {vs_gain['RMS phase error held (deg)'].iloc[0]:g} deg"),
                              (ax[1], vs_phase, 'RMS phase error (deg)', f"gain error {vs_phase['RMS gain error held (dB)'].iloc[0]:g} dB")):
        l1, = a.plot(df[xcol], df['Pointing error rms (deg)'], 'o-', color='tab:blue', label='Pointing error (rms)')
        a.set_xlabel(xcol)
        a.set_ylabel('Pointing error (deg)', color='tab:blue')
        a2 = a.twinx()
        l2, = a2.plot(df[xcol], df['Sidelobe error (dB)'], 's-', color='tab:orange', label='Sidelobe error')
        a2.set_ylabel('Sidelobe error (dB)', color='tab:orange')
        a.grid(True)
        a.legend(handles=[l1, l2], loc='upper left')
        a.set_title(f'{title}, {hold} held', fontsize=10)
    fig.tight_layout()
    return fig


# ---------------- saving ----------------
def _tag(x):
    return f'{x:g}'.replace('.', 'p').replace('-', 'm')


def _range_tag(values):
    values = list(values)
    return f'{_tag(min(values))}to{_tag(max(values))}'


def folder_name(cfg, az_list, el_list, n_trials, extra=''):
    """Sub folder name built from the parameter values, groups separated by __."""
    taper = cfg.taper + (f'{cfg.taper_sll_db:g}dB' if cfg.taper in ('taylor', 'chebyshev') else '')
    name = (f'array_{cfg.nx}x{cfg.ny}__freq_{_tag(cfg.freq_ghz)}GHz__taper_{taper}'
            f'__phase_{_tag(cfg.phase_bits)}b__gain_{cfg.gain_bits}b_{_tag(cfg.gain_step_db)}dB'
            f'__gerr_{_range_tag(cfg.err_gain_rms_db)}dB__perr_{_range_tag(cfg.err_phase_rms_deg)}deg'
            f'__az_{_range_tag(az_list)}_n{len(az_list)}__el_{_range_tag(el_list)}_n{len(el_list)}__trials_{n_trials}{extra}' + ('__measured' if cfg.measured_csv else ''))
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def parameter_table(cfg, extra=None):
    d = asdict(cfg)
    d.update(extra or {})
    return pd.DataFrame({'Parameter': list(d.keys()), 'Value': [str(v) for v in d.values()]})


def save_results(base_dir, cfg, az_list, el_list, n_trials, results=None, maps=None, sweep=None, extra_params=None):
    """Create the parameter-named sub folder under base_dir (a timestamp is added to the name when that folder already exists),
    write results.xlsx and the plots (png) in it.
    sweep = (vs_gain, vs_phase, title). Returns the folder path."""
    folder = os.path.join(base_dir, folder_name(cfg, az_list, el_list, n_trials))
    if os.path.exists(folder):   # never write into an existing folder: add a timestamp to the name
        stamp = f'{folder}__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}'
        folder, k = stamp, 1
        while os.path.exists(folder):
            k += 1
            folder = f'{stamp}_{k}'
    os.makedirs(folder)
    taper = cfg.taper
    with pd.ExcelWriter(os.path.join(folder, 'results.xlsx'), engine='openpyxl') as xw:
        parameter_table(cfg, extra_params).to_excel(xw, sheet_name='Parameters', index=False)
        if results is not None:
            results.table().to_excel(xw, sheet_name='Beam errors', index=False)
            results.trials().to_excel(xw, sheet_name='Trials', index=False)
            for s, (az0, el0) in enumerate(results.steers):
                azc, elc = results.cuts_table(s)
                azc.to_excel(xw, sheet_name=f'Cut az {az0:g},{el0:g}'[:31], index=False)
                elc.to_excel(xw, sheet_name=f'Cut el {az0:g},{el0:g}'[:31], index=False)
            fig_summary(results).savefig(os.path.join(folder, 'summary.png'), dpi=110)
            os.makedirs(os.path.join(folder, 'pattern_cuts'), exist_ok=True)
            for s, (az0, el0) in enumerate(results.steers):
                fig_pattern_cuts(results, s).savefig(os.path.join(folder, 'pattern_cuts', f'cuts_az{az0:g}_el{el0:g}.png'), dpi=100)
        if maps is not None:
            idx = [f'y{k}' for k in range(maps['phase_az'].shape[0])]
            col = [f'x{k}' for k in range(maps['phase_az'].shape[1])]
            for key, sheet in (('phase_az', 'Phase az steer'), ('phase_el', 'Phase el steer'),
                               ('gain_ideal_db', 'Gain ideal (dB)'), ('gain_quant_db', 'Gain quantized (dB)')):
                pd.DataFrame(maps[key], index=idx, columns=col).to_excel(xw, sheet_name=sheet)
            fig_element_maps(maps, taper, cfg.gain_step_db, cfg.gain_bits).savefig(os.path.join(folder, 'element_maps.png'), dpi=110)
        if sweep is not None:
            vs_gain, vs_phase, title = sweep
            vs_gain.to_excel(xw, sheet_name='Sweep vs gain error', index=False)
            vs_phase.to_excel(xw, sheet_name='Sweep vs phase error', index=False)
            fig_error_sweep(vs_gain, vs_phase, title).savefig(os.path.join(folder, 'error_sweep.png'), dpi=110)
    return folder


def progress_bar_printer(label=''):
    """progress(done, total) callback that prints a one line progress bar with ETC."""
    import time
    t0 = time.time()

    def progress(done, total):
        etc = str(datetime.timedelta(seconds=round((time.time() - t0) / done * (total - done))))
        print(f'\r{label}[{"#" * (30 * done // total):<30}] {100 * done // total:3d}%  ({done}/{total})  ETC {etc}', end='', flush=True)
    return progress
