# Build a single 64-entry RX gain LUT from a raw 4-channel AV sweep.
#
# Each channel is normalized to its own max gain (the LUT controls relative
# attenuation; absolute channel gains differ), then the four relative curves
# are combined per AV code with a median in dB - robust to a corrupted
# channel tail (e.g. rx2 goes non-monotonic near the end of the sweep).
# AV codes are then picked so consecutive entries are ~0.5 dB apart
# (g_idx 0 = max gain, g_idx 63 = max attenuation, -0.5 dB/idx convention).
#
# Raw data format: one row per AV code, swept from highest AV (max gain) to
# lowest (row 0 = AV N-1, last row = AV 0), one S21 gain column per RX
# channel.

in_file = r'G:\Shared drives\PRJ_BFM\BFM_Ku\Silicon Validation\raw_data\rx_av_sweep\rx_gain_lut.xlsx'
out_file = r'G:\Shared drives\PRJ_BFM\BFM_Ku\Silicon Validation\raw_data\rx_av_sweep\rx_gain_lut_64.xlsx'

n_steps = 64
step_dB = 0.5
step_warn_dB = 0.15   # flag steps that deviate from 0.5 dB by more than this
skip_first = 4        # first rows (highest AV codes) hold invalid data

import pandas as pd
import numpy as np

df = pd.read_excel(in_file)
n_codes = df.shape[0]
print(f'Raw sweep: {n_codes} AV codes, {df.shape[1]} channels, '
      f'skipping AV {n_codes - 1}..{n_codes - skip_first}')

# Rows run from highest AV (max gain) to AV 0 (max attenuation)
raw = df.to_numpy(dtype=float)[skip_first:]
av_axis = np.arange(n_codes - 1 - skip_first, -1, -1)

# Relative attenuation per channel (0 dB at each channel's max gain),
# invalid leading rows excluded
rel = raw - raw.max(axis=0)

# Median across channels per AV code
avg = np.median(rel, axis=1)

# Usable region: from max down to min of the averaged curve; anything after
# the minimum is roll-off/noise and must not be picked
start = int(np.argmax(avg))
stop = int(np.argmin(avg))
print(f'Averaged curve: 0 dB @ AV {av_axis[start]}, '
      f'{avg[stop]:.2f} dB @ AV {av_axis[stop]}')

sel_idx = np.zeros(n_steps, dtype=int)
gains = np.zeros(n_steps)
prev = start
for k in range(n_steps):
    target = avg[start] - step_dB * k
    # Search forward only, so the picked AV codes stay monotonic
    seg = avg[prev:stop + 1]
    idx = prev + int(np.argmin(np.abs(seg - target)))
    sel_idx[k] = idx
    gains[k] = avg[idx]
    prev = idx
av_codes = av_axis[sel_idx]

steps = np.diff(gains)
for b in np.where(np.abs(steps + step_dB) > step_warn_dB)[0]:
    print(f'WARN g_idx {b}->{b + 1}: step {steps[b]:+.3f} dB '
          f'(AV {av_codes[b]} -> {av_codes[b + 1]})')
print(f'Range 0 -> {gains[-1]:.2f} dB, step mean {-steps.mean():.3f} dB, '
      f'worst dev {np.max(np.abs(steps + step_dB)):.3f} dB')

out = pd.DataFrame({'g_idx': np.arange(n_steps),
                    'av': av_codes,
                    'atten_dB': gains,
                    'target_dB': -step_dB * np.arange(n_steps)})
# Per-channel relative attenuation at the chosen codes, for verification
for ch, col in enumerate(df.columns):
    out[f'atten_dB_rx{ch}'] = rel[sel_idx, ch]

out.to_excel(out_file, index=False)
print(f'\nLUT written to: {out_file}')
