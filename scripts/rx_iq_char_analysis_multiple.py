"""
Overlay the highest-gain closed I/Q contour, and the phase along it, from several
csv files written by tests/char/rx_iq_char.py.

usage: python rx_iq_char_analysis_multiple.py [--freq GHz]
Set csv_files below.
"""
import argparse
import os
import numpy as np
import pandas as pd
import contourpy
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

csv_files = [
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_1__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-128,4,128]__2026-09-30_20-46-38.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_2__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-128,4,128]__2026-09-30_19-48-23.csv',
]

parser = argparse.ArgumentParser()
parser.add_argument('--freq', type=float, default=9.5, help='GHz (nearest column is used)')
args = parser.parse_args()

path_len = lambda seg: np.hypot(*np.diff(seg, axis=0).T).sum()

def nearest_col(df, prefix):
    cols = [c for c in df.columns if c.startswith(prefix)]
    ghz = [float(c.split()[-1].replace('GHz', '')) for c in cols]
    k = min(range(len(ghz)), key=lambda n: abs(ghz[n] - args.freq))
    return cols[k], ghz[k]

def largest_contour(csv):
    """Returns (gain level dB, contour (i, q), angle deg, unwrapped phase deg, freq GHz)."""
    df = pd.read_csv(csv)
    gcol, ghz = nearest_col(df, 'Gain dB')
    pcol, _ = nearest_col(df, 'Phase deg')
    gain = df.pivot(index='Q', columns='I', values=gcol)
    phase = df.pivot(index='Q', columns='I', values=pcol)

    # interpolate phase through cos/sin so the +-180 wrap does not corrupt it
    pc = RegularGridInterpolator((phase.index, phase.columns), np.cos(np.radians(phase.values)))
    ps = RegularGridInterpolator((phase.index, phase.columns), np.sin(np.radians(phase.values)))

    # highest-gain contour that closes inside the grid
    gen = contourpy.contour_generator(gain.columns.values, gain.index.values, gain.values)
    span = max(gain.columns.max() - gain.columns.min(), gain.index.max() - gain.index.min())
    for lvl in np.linspace(gain.values.max(), gain.values.min(), 1000):
        loops = [seg for seg in gen.lines(lvl) if len(seg) > 3 and np.allclose(seg[0], seg[-1]) and path_len(seg) > 0.2 * span]
        if loops:
            big = max(loops, key=path_len)
            break
    else:
        raise RuntimeError(f'no closed contour in {csv}')

    i, q = big[:, 0], big[:, 1]
    ph = np.degrees(np.arctan2(ps(np.c_[q, i]), pc(np.c_[q, i])))
    ang = np.degrees(np.arctan2(q, i))
    order = np.argsort(ang)
    return lvl, big, ang[order], np.degrees(np.unwrap(np.radians(ph[order]))), ghz

if not csv_files:
    raise SystemExit('csv_files is empty: add csv paths to the list at the top of the script')

fig, ax = plt.subplots(1, 2, figsize=(14, 6))
for k, csv in enumerate(csv_files):
    lvl, big, ang, ph, ghz = largest_contour(csv)
    label = f'{os.path.splitext(os.path.basename(csv))[0]} ({lvl:.2f} dB)'
    color = plt.cm.tab10(k % 10)
    ax[0].plot(big[:, 0], big[:, 1], color=color, lw=2, label=label)
    ax[1].plot(ang, ph, '.-', color=color, label=label)

ax[0].set_title(f'Highest-gain closed contour @ {ghz:g} GHz')
ax[0].set_xlabel('I code'); ax[0].set_ylabel('Q code'); ax[0].set_aspect('equal'); ax[0].grid(True)
ax[1].set_title('Phase along the contour')
ax[1].set_xlabel('Angle in I/Q plane (deg)'); ax[1].set_ylabel('Phase (deg)'); ax[1].grid(True)
ax[1].legend(fontsize=7)
fig.tight_layout()
plt.show()
