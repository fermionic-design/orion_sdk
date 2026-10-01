"""
Generate an RX gain LUT (same xlsx format as final_lut/v2__rx2__gain_lut__*.xlsx) from csv files
written by tests/char/rx_Av_char.py (first file = reference channel).

The LUT has 64 entries, 0.5 dB apart: entry g should give a gain of (gain at entry 0) - 0.5*g dB,
and a phase correction code (signed, -4...3 steps of 2.975 deg) that holds the phase constant.
Entry 0 is Av = av_max.

Knobs
  freq : GHz, nearest measured frequency is used
  algo : 'ref0'...'ref3' - pick the Av whose gain on that channel (index into csv_files) hits each target
         'joint_rms' - pick the Av that minimizes the sum of squared gain errors over all channels
         'joint_max' - pick the Av that minimizes the worst channel's gain error
         (the phase correction code follows the same rule: that channel's, the channels' mean, or midrange)
"""
import os
import re
import numpy as np
import pandas as pd
import openpyxl
from scipy.interpolate import PchipInterpolator

freq = 9.5
algo = 'joint_max'   # 'ref0', 'ref1', 'ref2', 'ref3', 'joint_rms' or 'joint_max'

csv_files = [
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_Av_char__v2__ant_sel_1__vdd_3p3__temp_25C__bias_NOM__iq_[264,464]__av_[2047,16,32,1,0]__2026-10-01_17-12-17.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_Av_char__v2__ant_sel_2__vdd_3p3__temp_25C__bias_NOM__iq_[264,464]__av_[2047,16,32,1,0]__2026-10-01_17-19-11.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_Av_char__v2__ant_sel_4__vdd_3p3__temp_25C__bias_NOM__iq_[264,464]__av_[2047,16,32,1,0]__2026-10-01_17-20-21.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_Av_char__v2__ant_sel_8__vdd_3p3__temp_25C__bias_NOM__iq_[264,464]__av_[2047,16,32,1,0]__2026-10-01_17-21-29.csv',
]
out_dir = r'./logs'

depth = 64            # LUT entries
gain_step = 0.5       # dB per entry
ph_step = 2.975       # deg per phase correction code step
av_max = 2047

wrap = lambda d: (d + 180) % 360 - 180
tag = lambda x: f'{x:g}'.replace('.', 'p')

# ---------------- config parsed from the first file name ----------------
m = re.search(r'rx_Av_char__(v\d+)__ant_sel_(\d+)__vdd_([^_]+)__temp_([^_]+)__bias_([^_]+)__iq_\[(\d+),(\d+)\]__', os.path.basename(csv_files[0]))
if not m:
    raise SystemExit(f'cannot parse version/vdd/temp/bias/iq from {csv_files[0]}')
version, _, vdd, temp, bias, iq_i, iq_q = m.groups()

m_ref = re.fullmatch(r'ref(\d+)', algo)
if m_ref is None and algo not in ('joint_rms', 'joint_max'):
    raise SystemExit("algo must be 'ref0'...'ref3', 'joint_rms' or 'joint_max'")
ref = int(m_ref.group(1)) if m_ref else 0   # reference channel (joint: reported gain column)
if ref >= len(csv_files):
    raise SystemExit(f'{algo}: only {len(csv_files)} csv files given')

# ---------------- gain / phase vs Av for every channel, on all integer codes ----------------
codes = np.arange(av_max + 1)
gain, phase = [], []
for f in csv_files:
    d = pd.read_csv(f).sort_values('Av')
    gcols = [c for c in d.columns if c.startswith('Gain dB')]
    k = int(np.argmin([abs(float(c.split()[-1].replace('GHz', '')) - freq) for c in gcols]))
    ph = d[f'Phase deg {gcols[k].split()[-1]}'].values
    ph = np.degrees(np.unwrap(np.radians(wrap(ph - ph[-1]))))        # phase relative to av_max
    gain.append(PchipInterpolator(d.Av.values, d[gcols[k]].values)(codes))   # gain between measured Av codes is interpolated
    phase.append(PchipInterpolator(d.Av.values, ph)(codes))
gain, phase = np.array(gain), np.array(phase)
print(f'{len(csv_files)} channels, freq {freq:g} GHz, algo {algo}')

rel = gain - gain[:, [av_max]]                      # gain relative to entry 0
target = -gain_step * np.arange(depth)              # target gain per entry
err = rel[:, :, None] - target                      # gain error [channel, Av, entry]

if algo.startswith('ref'):
    av = np.abs(err[ref]).argmin(axis=0)
elif algo == 'joint_rms':
    av = (err ** 2).sum(axis=0).argmin(axis=0)
else:
    av = np.abs(err).max(axis=0).argmin(axis=0)

# ---------------- phase correction code, same rule as ORION_8G_12G_hal.init_lut ----------------
need = -phase[:, av]                                # correction needed to hold the phase at its entry-0 value (deg)
if algo.startswith('ref'):
    need_ref = need[ref]
elif algo == 'joint_rms':
    need_ref = need.mean(axis=0)
else:
    need_ref = (need.min(axis=0) + need.max(axis=0)) / 2
idx = np.round(need_ref / ph_step).astype(int)
lo, hi = idx[:50].min(), idx[:50].max()
shift = 0
if hi > 3:
    shift = 3 - hi                                   # move the range so the top fits
elif lo < -4:
    shift = -4 - lo                                  # move the range so the bottom fits
code = np.clip(idx + shift, -4, 3)
ph_err_col = need_ref + shift * ph_step

# ---------------- report ----------------
gerr = np.array([rel[c, av] - target for c in range(len(csv_files))])
perr = phase[:, av] + code * ph_step
stat = lambda e: (e.std(), np.sqrt(np.mean(e ** 2)), np.abs(e).max())
print(f'\n{"channel":<8}{"gain sd":>9}{"gain rms":>10}{"gain pk":>9}{"phase sd":>10}{"phase rms":>11}{"phase pk":>10}   (dB, deg)')
for c in range(len(csv_files)):
    g, p = stat(gerr[c]), stat(perr[c])
    print(f'{c:<8}{g[0]:9.2f}{g[1]:10.2f}{g[2]:9.2f}{p[0]:10.2f}{p[1]:11.2f}{p[2]:10.2f}')
print(f'worst channel: gain sd {max(stat(e)[0] for e in gerr):.2f} dB, gain pk {max(stat(e)[2] for e in gerr):.2f} dB, '
      f'phase sd {max(stat(e)[0] for e in perr):.2f} deg, phase pk {max(stat(e)[2] for e in perr):.2f} deg')

# ---------------- write xlsx ----------------
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Sheet1'
ws.append(['Av', 'Phase Err Code', 'Gain', 'Phase Err'])
for g in range(depth):
    ws.append([int(av[g]), int(code[g]), float(gain[ref, av[g]]), float(ph_err_col[g])])

name = f'{version}__rx_gain_lut__freq_{tag(freq)}__algo_{algo}__iq_[{iq_i},{iq_q}]__bias_{bias.lower()}__vdd_{vdd}__temp_{temp}.xlsx'
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, name)
wb.save(path)
print(f'\nLUT saved: {os.path.abspath(path)}')
