"""
Generate a TX gain LUT (same xlsx format as final_lut/v2__tx__gain_lut__*.xlsx) from csv files
written by tests/char/tx_Av_char.py (first file = reference channel).

The LUT has 64 entries, 0.5 dB apart: entry g should give a gain of (gain at entry 0) - 0.5*g dB.
Entry 0 is Av = av_max. The TX has no gain or phase correction, so the 'Phase Err Code' and 'Phase Err' columns are 0.

Knobs
  freq : GHz, nearest measured frequency is used
  max_code : last LUT entry that is generated from the data; entries above it repeat entry max_code (None: use all entries)
  algo : 'ref0'...'ref3' - pick the Av whose gain on that channel (index into csv_files) hits each target
         'joint_rms' - pick the Av that minimizes the sum of squared gain errors over all channels
         'joint_max' - pick the Av that minimizes the worst channel's gain error
         (every csv is a channel: give one csv per antenna, all at the same I/Q and Pin)
"""
import os
import re
import numpy as np
import pandas as pd
import openpyxl
from scipy.interpolate import PchipInterpolator

freq = 9.5
algo = 'joint_max'   # 'ref0', 'ref1', 'ref2', 'ref3', 'joint_rms' or 'joint_max'
max_code = None      # None: all 64 entries are generated from the data

csv_files = [   # one csv per antenna (channel), same I/Q and Pin; the first is the reference
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\chip_55__tx_Av_char__v2__ant_sel_all_8__vdd_2p7__temp_25C__bias_MAX__pin_-20__iq_[248,4]__av_[2047,16,32,1,0]__2026-11-06_12-23-21.csv',
]

out_dir = r'./logs'

depth = 64            # LUT entries
gain_step = 0.5       # dB per entry
av_max = 2047         # gain is normalized to this Av (entry 0); points with a -200 dB VNA error value are dropped

tag = lambda x: f'{x:g}'.replace('.', 'p')

# ---------------- config parsed from the file names ----------------
chips = sorted({re.match(r'chip_(\d+)__', os.path.basename(f)).group(1) for f in csv_files if os.path.basename(f).startswith('chip_')})
pat = r'(?:(chip_\d+)__)?tx_Av_char__(v\d+)__ant_sel_(?:all_)?(\d+)__vdd_([^_]+)__temp_([^_]+)__bias_(.+?)__pin_(-?\d+(?:\.\d+)?)__iq_\[(-?\d+),(-?\d+)\]__'
m = re.search(pat, os.path.basename(csv_files[0]))
if not m:
    raise SystemExit(f'cannot parse version/vdd/temp/bias/pin/iq from {csv_files[0]}')
chip, version, _, vdd, temp, bias, pin, iq_i, iq_q = m.groups()
if len(chips) > 1:
    chip = 'chips_' + '_'.join(chips)   # LUT covers several chips, all listed
iqs = {re.search(pat, os.path.basename(f)).group(8, 9) for f in csv_files}
iq_tag = f'[{iq_i},{iq_q}]' if len(iqs) == 1 else f'multi_{len(iqs)}'   # csvs at different I/Q states

m_ref = re.fullmatch(r'ref(\d+)', algo)
if m_ref is None and algo not in ('joint_rms', 'joint_max'):
    raise SystemExit("algo must be 'ref0'...'ref3', 'joint_rms' or 'joint_max'")
ref = int(m_ref.group(1)) if m_ref else 0   # reference channel (joint: reported gain column)
if ref >= len(csv_files):
    raise SystemExit(f'{algo}: only {len(csv_files)} csv files given')

# ---------------- gain vs Av for every channel, on all integer codes ----------------
codes = np.arange(av_max + 1)
gain = []
for f in csv_files:
    d = pd.read_csv(f).sort_values('Av')
    d = d[(d.Av <= av_max) & (d.filter(like='Gain dB').min(axis=1) > -150)]   # drop Av > av_max and VNA error points
    gcols = [c for c in d.columns if c.startswith('Gain dB')]
    k = int(np.argmin([abs(float(c.split()[-1].replace('GHz', '')) - freq) for c in gcols]))
    gain.append(PchipInterpolator(d.Av.values, d[gcols[k]].values)(codes))   # gain between measured Av codes is interpolated
gain = np.array(gain)
print(f'{len(csv_files)} channels, freq {freq:g} GHz, algo {algo}')

rel = gain - gain[:, [av_max]]                      # gain relative to entry 0
target = -gain_step * np.arange(depth)              # target gain per entry
err = rel[:, :, None] - target                      # gain error [channel, Av, entry]

# the measured gain turns back up below some Av (the low-Av hump): only search the monotonic region above the highest such turning point
av_lo = max(int(codes[1:][np.argmin(g[1:])]) for g in gain)
print(f'Av search range: {av_lo}...{av_max}')
sl = slice(av_lo, None)

if algo.startswith('ref'):
    av = np.abs(err[ref][sl]).argmin(axis=0) + av_lo
elif algo == 'joint_rms':
    av = (err[:, sl] ** 2).sum(axis=0).argmin(axis=0) + av_lo
else:
    av = np.abs(err[:, sl]).max(axis=0).argmin(axis=0) + av_lo
if max_code is not None:
    av[max_code + 1:] = av[max_code]   # past max_code duplicate the last generated entry

# ---------------- report ----------------
n_gen = depth if max_code is None else max_code + 1   # entries generated from the data
gerr = np.array([rel[c, av] - target for c in range(len(csv_files))])[:, :n_gen]   # stats only over the generated entries, not the duplicated ones
stat = lambda e: (e.std(), np.sqrt(np.mean(e ** 2)), np.abs(e).max())
print(f'\n{"channel":<8}{"gain sd":>9}{"gain rms":>10}{"gain pk":>9}   (dB)')
for c in range(len(csv_files)):
    g = stat(gerr[c])
    print(f'{c:<8}{g[0]:9.2f}{g[1]:10.2f}{g[2]:9.2f}')
print(f'worst channel: gain sd {max(stat(e)[0] for e in gerr):.2f} dB, gain pk {max(stat(e)[2] for e in gerr):.2f} dB')

# ---------------- write xlsx ----------------
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Sheet1'
ws.append(['Gain Code', 'Phase Err Code', 'Gain', 'Phase Err'])
for g in range(depth):
    ws.append([int(av[g]), 0, float(gain[ref, av[g]]), 0])   # no phase correction on the TX

name = f'{chip + "__" if chip else ""}{len(csv_files)}ch__{version}__tx_gain_lut__freq_{tag(freq)}__algo_{algo}__iq_{iq_tag}__bias_{bias.lower()}__pin_{pin}__vdd_{vdd}__temp_{temp}' + (f'__max_code_{max_code}' if max_code is not None else '') + '.xlsx'
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, name)
wb.save(path)
print(f'\nLUT saved: {os.path.abspath(path)}')
