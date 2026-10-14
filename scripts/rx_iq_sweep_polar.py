"""
Polar plots of a csv written by tests/char/rx_Av_iq_sweep.py: radius = gain (dB), angle = phase (deg).
  circles : one trace per gain code (a circle of varying radius as the phase index sweeps)
  spokes  : one trace per phase angle (every 45 deg) with the gain code varying along it
  phase_err : (not polar) phase error vs phase index, one line per gain code

Phase is always taken relative to phase code 0 (p_idx 4) of the same gain code: every circle starts at 0 deg and the
phase error is the deviation from the ideal 360/121 deg per phase index, as in rx_Av_iq_sweep.py. This is recomputed
from the 'Phase deg' column, so csvs written with the older reference (gain code 0 only) plot the same way.

usage: python rx_iq_sweep_polar.py [csv_path]
Without a path (argument or csv_path variable) the newest rx_Av_iq_sweep or rx_Av_iq_sweep_s11 csv in tests/char/logs is used.
"""
import argparse
import glob
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

csv_path = None   # set to a csv path, or None to use the newest csv in tests/char/logs
plots = ('circles', 'spokes', 'phase_err')   # which plots to draw
spoke_deg = 45                  # angle between spokes (smaller = more spokes)

parser = argparse.ArgumentParser()
parser.add_argument('csv', nargs='?')
args = parser.parse_args()

args.csv = args.csv or csv_path
if args.csv is None:
    logs = os.path.join(os.path.dirname(__file__), '..', 'tests', 'char', 'logs', 'rx_Av_iq_sweep*__*.csv')
    args.csv = max(glob.glob(logs), key=os.path.getmtime)
print(f'Reading {args.csv}')
df = pd.read_csv(args.csv)

p_step = 360 / 121   # deg per phase index; p_idx 4 is 0 deg
wrap = lambda d: (d + 180) % 360 - 180
if df.p_idx.nunique() > 1:   # a phase sweep: reference every gain code to its own phase code 0
    ref = df[df.p_idx == 4].set_index('g_idx')['Phase deg']
    df['Phase deg'] = wrap(df['Phase deg'] - df.g_idx.map(ref))
    df['Phase err deg'] = wrap(df['Phase deg'] - (df.p_idx - 4) * p_step)
else:
    print('single phase code in this csv: phase left as measured')

lo, hi = df['Gain dB'].min(), df['Gain dB'].max()
rlim = (np.floor(lo - 2), np.ceil(hi + 1))
name = os.path.basename(args.csv)

def polar_axes(title):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='polar')
    ax.set_rlim(*rlim)
    ax.set_rlabel_position(135)
    ax.set_title(f'{title}\n{name}', fontsize=8, pad=18)
    return ax

if 'circles' in plots:
    ax = polar_axes('RX gain (radius, dB) vs phase (angle), one circle per gain code')
    g_codes = sorted(df.g_idx.unique())
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(g_codes)))
    for g, color in zip(g_codes, colors):
        d = df[df.g_idx == g].sort_values('p_idx')
        theta = np.radians(np.r_[d['Phase deg'].values, d['Phase deg'].values[0]])   # close the loop
        r = np.r_[d['Gain dB'].values, d['Gain dB'].values[0]]
        ax.plot(theta, r, color=color, lw=1.0, marker='o', ms=3, label=f'g_idx {g}')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0), fontsize=8)

if 'spokes' in plots:
    ax = polar_axes(f'RX gain (radius, dB) vs phase (angle), one spoke every {spoke_deg} deg, gain code varying')
    ax.set_thetagrids(np.arange(0, 360, spoke_deg), fontsize=7)
    angles = np.arange(0, 360, spoke_deg)
    many = len(angles) > 12   # with many spokes: color by angle, small markers, no legend (the angle grid labels them)
    markers = ['+', 'x', '*', 's', 'o', '^', 'v', 'D']
    for k, ang in enumerate(angles):
        p = 4 + int(round(ang / p_step))
        d = df[df.p_idx == p].sort_values('g_idx')
        if d.empty:
            print(f'no data for {ang} deg (p_idx {p})')
            continue
        style = dict(color=plt.cm.hsv(ang / 360), marker='o', ms=3) if many else dict(marker=markers[k % len(markers)], ms=5)
        ax.plot(np.radians(d['Phase deg'].values), d['Gain dB'].values, lw=1.0 if many else 1.2,
                label=f'{ang:g} Degrees (p_idx {p})', **style)
    if not many:
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0), fontsize=8)

if 'phase_err' in plots:
    fig, ax = plt.subplots(figsize=(10, 5))
    g_codes = sorted(df.g_idx.unique())
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(g_codes)))
    for g, color in zip(g_codes, colors):
        d = df[df.g_idx == g].sort_values('p_idx')
        ax.plot(d.p_idx, d['Phase err deg'], color=color, lw=1.2, label=f'g_idx {g}')
    ax.axhline(0, color='k', lw=0.6)
    ax.set_xlabel('Phase index')
    ax.set_ylabel('Phase error (deg)')
    ax.set_title(f'Phase error vs phase index, one line per gain code\n{name}', fontsize=8)
    ax.grid(True)
    ax.legend(fontsize=8)
    fig.tight_layout()

plt.tight_layout()
plt.show()
