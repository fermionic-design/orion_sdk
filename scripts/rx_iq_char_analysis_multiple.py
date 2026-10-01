"""
Overlay a closed I/Q gain contour (backoff_db below the highest-gain one), and the phase along it, from several
csv files written by tests/char/rx_iq_char.py.

It also builds a phase LUT (lut_depth entries, 360/lut_depth deg apart) on that contour of
the first file and evaluates the same I/Q codes on the other files to estimate the phase error.

usage: python rx_iq_char_analysis_multiple.py [--freq GHz]
Set csv_files below (first file = LUT reference).
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
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_4__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-128,4,128]__2026-09-30_21-10-35.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_8__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-128,4,128]__2026-09-30_21-40-56.csv',
]

lut_depth = 121   # LUT entries, 360/121 = 2.975 deg apart
backoff_db = 10    # use the closed contour this many dB below each file's highest-gain closed contour (0 = highest)

parser = argparse.ArgumentParser()
parser.add_argument('--freq', type=float, default=9.5, help='GHz (nearest column is used)')
args = parser.parse_args()

path_len = lambda seg: np.hypot(*np.diff(seg, axis=0).T).sum()
wrap = lambda d: (d + 180) % 360 - 180

def nearest_col(df, prefix):
    cols = [c for c in df.columns if c.startswith(prefix)]
    ghz = [float(c.split()[-1].replace('GHz', '')) for c in cols]
    k = min(range(len(ghz)), key=lambda n: abs(ghz[n] - args.freq))
    return cols[k], ghz[k]

class Sweep:
    def __init__(self, csv):
        self.name = os.path.splitext(os.path.basename(csv))[0]
        df = pd.read_csv(csv)
        gcol, self.ghz = nearest_col(df, 'Gain dB')
        pcol, _ = nearest_col(df, 'Phase deg')
        self.gain = df.pivot(index='Q', columns='I', values=gcol)
        phase = df.pivot(index='Q', columns='I', values=pcol)
        # interpolate phase through cos/sin so the +-180 wrap does not corrupt it
        axes = (phase.index, phase.columns)
        self._pc = RegularGridInterpolator(axes, np.cos(np.radians(phase.values)))
        self._ps = RegularGridInterpolator(axes, np.sin(np.radians(phase.values)))
        self._g = RegularGridInterpolator(axes, self.gain.values)

    def phase_at(self, i, q):
        return np.degrees(np.arctan2(self._ps(np.c_[q, i]), self._pc(np.c_[q, i])))

    def gain_at(self, i, q):
        return self._g(np.c_[q, i])

    def largest_contour(self):
        """Highest-gain contour that closes inside the grid: (level dB, closed path of (i, q))."""
        g = self.gain
        gen = contourpy.contour_generator(g.columns.values, g.index.values, g.values)
        span = max(g.columns.max() - g.columns.min(), g.index.max() - g.index.min())
        lvl_max = None
        for lvl in np.linspace(g.values.max(), g.values.min(), 1000):
            if lvl_max is not None and lvl > lvl_max - backoff_db:
                continue
            loops = [s for s in gen.lines(lvl) if len(s) > 3 and np.allclose(s[0], s[-1]) and path_len(s) > 0.2 * span]
            if loops and lvl_max is None:
                lvl_max = lvl   # highest-gain closed contour
                if backoff_db > 0:
                    continue
            if loops:
                return lvl, max(loops, key=path_len)
        raise RuntimeError(f'no closed contour in {self.name}')

if not csv_files:
    raise SystemExit('csv_files is empty: add csv paths to the list at the top of the script')

sweeps = [Sweep(c) for c in csv_files]

# ---------------- overlay of contour + phase ----------------
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
contours = []
for k, sw in enumerate(sweeps):
    lvl, path = sw.largest_contour()
    contours.append(path)
    i, q = path[:, 0], path[:, 1]
    ang = np.degrees(np.arctan2(q, i))
    order = np.argsort(ang)
    ph = np.degrees(np.unwrap(np.radians(sw.phase_at(i, q)[order])))
    label = f'{sw.name} ({lvl:.2f} dB)'
    color = plt.cm.tab10(k % 10)
    ax[0].plot(i, q, color=color, lw=2, label=label)
    ax[1].plot(ang[order], ph, '.-', color=color, label=label)

ax[0].set_title(f'Closed contour {backoff_db:g} dB below the highest @ {sweeps[0].ghz:g} GHz')
ax[0].set_xlabel('I code'); ax[0].set_ylabel('Q code'); ax[0].set_aspect('equal'); ax[0].grid(True)
ax[1].set_title('Phase along the contour')
ax[1].set_xlabel('Angle in I/Q plane (deg)'); ax[1].set_ylabel('Phase (deg)'); ax[1].grid(True)
ax[1].legend(fontsize=7)
fig.tight_layout()

# ---------------- LUT on the first file, evaluated on the others ----------------
ref = sweeps[0]
path = contours[0][:-1]   # drop the duplicated closing point
i, q = path[:, 0], path[:, 1]
ph = np.degrees(np.unwrap(np.radians(ref.phase_at(i, q))))   # phase along the loop
sign = 1 if ph[-1] >= ph[0] else -1
if np.any(np.diff(sign * ph) <= 0):
    print('WARNING: phase is not monotonic along the reference contour; LUT points may be off')
order = np.argsort(sign * ph)
step = 360 / lut_depth
target = ph[0] + sign * step * np.arange(lut_depth)   # LUT phase targets (deg)
lut_i = np.interp(sign * target, sign * ph[order], i[order])
lut_q = np.interp(sign * target, sign * ph[order], q[order])

# use only measured codes: pick the grid point near each interpolated spot whose reference phase is closest to the target
gstep = ref.gain.columns[1] - ref.gain.columns[0]
nb = np.arange(-2, 3) * gstep
for n in range(lut_depth):
    ci, cq = [a.ravel() for a in np.meshgrid(np.round(lut_i[n] / gstep) * gstep + nb, np.round(lut_q[n] / gstep) * gstep + nb)]
    ok = (np.abs(ci) <= ref.gain.columns.max()) & (np.abs(cq) <= ref.gain.index.max())
    ci, cq = ci[ok], cq[ok]
    b = np.argmin(np.abs(wrap(ref.phase_at(ci, cq) - wrap(target[n]))))
    lut_i[n], lut_q[n] = ci[b], cq[b]
print(f'\nLUT: {lut_depth} entries, {step:.3f} deg apart, built on {ref.name}')
print(f'{"file":<40}{"raw rms":>9}{"raw pk":>8}{"offset":>9}{"rms":>7}{"pk":>7}   gain sd   (deg; rms/pk are after removing the offset)')

fig2, ax2 = plt.subplots(figsize=(10, 5))
err_std = {}
for k, sw in enumerate(sweeps[1:], start=1):
    err = wrap(sw.phase_at(lut_i, lut_q) - wrap(target))                   # error vs LUT target
    offset = np.degrees(np.angle(np.mean(np.exp(1j * np.radians(err)))))   # constant phase offset
    err0 = wrap(err - offset)
    g = sw.gain_at(lut_i, lut_q)
    print(f'{sw.name:<40}{np.sqrt(np.mean(err**2)):9.2f}{np.abs(err).max():8.2f}{offset:9.2f}'
          f'{np.sqrt(np.mean(err0**2)):7.2f}{np.abs(err0).max():7.2f}{g.std():9.2f}')
    err_std[sw.name] = err0.std()
    ax2.plot(np.arange(lut_depth), err0, '.-', color=plt.cm.tab10(k % 10), label=f'{sw.name} (offset {offset:.1f} deg removed)')

    fig3, ax3 = plt.subplots(figsize=(8, 7))
    ax3.plot(path[:, 0], path[:, 1], color='gray', lw=0.8)
    lim = np.abs(err0).max()
    sc = ax3.scatter(lut_i, lut_q, c=err0, cmap='coolwarm', vmin=-lim, vmax=lim, s=40, zorder=3)
    for n in range(0, lut_depth, 10):
        ax3.annotate(str(n), (lut_i[n], lut_q[n]), fontsize=7, xytext=(3, 3), textcoords='offset points')
    fig3.colorbar(sc, ax=ax3, label='Phase error (deg)')
    ax3.set_title(f'LUT points on {ref.name[-30:]} contour, colored by error on {sw.name[-30:]}', fontsize=8)
    ax3.set_xlabel('I code'); ax3.set_ylabel('Q code'); ax3.set_aspect('equal'); ax3.grid(True)
    fig3.tight_layout()
ax2.set_title(f'Phase error of the {lut_depth}-entry LUT from {ref.name}')
ax2.set_xlabel('LUT index'); ax2.set_ylabel('Phase error (deg)'); ax2.grid(True); ax2.legend(fontsize=7)
fig2.tight_layout()

print('\nPhase error STDDEV (deg), offset removed:')
for name, sd in err_std.items():
    print(f'  {sd:6.2f}  {name}')
plt.show()
