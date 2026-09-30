"""
Plot gain contours vs I/Q from a csv written by tests/char/rx_iq_char.py, and
show how phase changes while moving along each constant-gain contour.

usage: python rx_iq_char_analysis.py [csv_path] [--freq GHz] [--levels N]
Without a path (argument or csv_path variable) the newest csv in tests/char/logs is used.
"""
import argparse
import glob
import os
import numpy as np
import contourpy
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

# csv_path = r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_2__vdd_2p7__temp_25C__bias_NOM__av_2047__2026-09-30_19-24-12.csv'   # set to a csv path, or None to use the newest csv in tests/char/logs
csv_path = None

parser = argparse.ArgumentParser()
parser.add_argument('csv', nargs='?')
parser.add_argument('--freq', type=float, default=9.5, help='GHz (nearest column is used)')
parser.add_argument('--levels', type=int, default=20, help='number of constant-gain contours')
args = parser.parse_args()

args.csv = args.csv or csv_path
if args.csv is None:
    logs = os.path.join(os.path.dirname(__file__), '..', 'tests', 'char', 'logs', '*.csv')
    args.csv = max(glob.glob(logs), key=os.path.getmtime)
print(f'Reading {args.csv}')
df = pd.read_csv(args.csv)

def nearest_col(prefix):
    cols = [c for c in df.columns if c.startswith(prefix)]
    ghz = [float(c.split()[-1].replace('GHz', '')) for c in cols]
    k = min(range(len(ghz)), key=lambda n: abs(ghz[n] - args.freq))
    return cols[k], ghz[k]

gcol, ghz = nearest_col('Gain dB')
pcol, _ = nearest_col('Phase deg')
gain = df.pivot(index='Q', columns='I', values=gcol)
phase = df.pivot(index='Q', columns='I', values=pcol)

# interpolate phase through cos/sin so the +-180 wrap does not corrupt it
pc = RegularGridInterpolator((phase.index, phase.columns), np.cos(np.radians(phase.values)))
ps = RegularGridInterpolator((phase.index, phase.columns), np.sin(np.radians(phase.values)))
phase_at = lambda i, q: np.degrees(np.arctan2(ps(np.c_[q, i]), pc(np.c_[q, i])))

levels = np.linspace(gain.values.min(), gain.values.max(), args.levels + 2)[1:-1]

fig, ax = plt.subplots(1, 2, figsize=(14, 6))
cs = ax[0].contourf(gain.columns, gain.index, gain.values, levels=20, cmap='Greys', alpha=0.5)
fig.colorbar(cs, ax=ax[0], label='Gain dB')
lines = ax[0].contour(gain.columns, gain.index, gain.values, levels=levels, colors='none')

path_len = lambda seg: np.hypot(*np.diff(seg, axis=0).T).sum()
paths = [(lvl, seg) for lvl, segs in zip(lines.levels, lines.allsegs) for seg in segs if len(seg) > 1]
# scan levels finely (independent of --levels) for the highest-gain contour that closes inside the grid
gen = contourpy.contour_generator(gain.columns.values, gain.index.values, gain.values)
span = max(gain.columns.max() - gain.columns.min(), gain.index.max() - gain.index.min())
big_lvl, big = None, None
for lvl in np.linspace(gain.values.max(), gain.values.min(), 1000):
    loops = [seg for seg in gen.lines(lvl) if len(seg) > 3 and np.allclose(seg[0], seg[-1]) and path_len(seg) > 0.2 * span]
    if loops:
        big_lvl, big = lvl, max(loops, key=path_len)
        break

for lvl, seg in paths:
    if seg is not big:
        ax[0].plot(seg[:, 0], seg[:, 1], color='tab:blue', lw=0.8, alpha=0.6)
ax[0].plot(big[:, 0], big[:, 1], color='tab:red', lw=2.5, label=f'{big_lvl:.2f} dB (highest closed)')
ax[0].legend(loc='upper right')

i, q = big[:, 0], big[:, 1]
ang = np.degrees(np.arctan2(q, i))
order = np.argsort(ang)
ph = phase_at(i, q)
ax[1].plot(ang[order], np.degrees(np.unwrap(np.radians(ph[order]))), '.-', color='tab:red')
ax[0].set_title(f'Constant-gain contours @ {ghz:g} GHz')
ax[0].set_xlabel('I code'); ax[0].set_ylabel('Q code'); ax[0].set_aspect('equal')

ax[1].set_title(f'Phase along the highest-gain closed contour ({big_lvl:.2f} dB)')
ax[1].set_xlabel('Angle in I/Q plane (deg)'); ax[1].set_ylabel('Phase (deg)')
ax[1].grid(True)

fig.suptitle(os.path.basename(args.csv), fontsize=9)
fig.tight_layout()
plt.show()
