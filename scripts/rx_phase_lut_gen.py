"""
Generate an RX phase LUT (same xlsx format as final_lut/v2_rx0_phase_lut_*.xlsx) from
csv files written by tests/char/rx_iq_char.py (first file = reference channel).

The LUT has 121 phase states, 360/121 = 2.975 deg apart, stored as 128 entries:
entry i holds state (i-4) mod 121, so entries 4...124 are the states and the rest wrap around.

Knobs
  freq : GHz, nearest measured frequency is used
  gm   : gain margin in dB - LUT codes need not lie on the gain contour, but the gain at every entry
         must be within +-gm of the contour level (joint: of each channel's own LUT gain level)
  backoff : dB below the highest-gain closed contour (of the reference channel) used as the gain level
  algo : 'ref0'...'ref3' - pick codes whose phase on that channel (index into csv_files) matches each target phase
         'joint_rms' - pick codes that minimize the sum of squared phase errors over all channels
         'joint_max' - pick codes that minimize the worst channel's phase std dev (the spec)
                   (joint algos calibrate out each channel's constant phase offset)
"""
import os
import re
import numpy as np
import pandas as pd
import contourpy
import openpyxl
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree

freq = 9.5
gm = 1.0
backoff = 10    # dB below the highest-gain closed contour used as the LUT gain level
algo = 'joint_max'   # 'ref0', 'ref1', 'ref2', 'ref3', 'joint_rms' or 'joint_max'

csv_files = [
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_1__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-252,4,252]__2026-10-01_12-41-48.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_2__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-252,4,252]__2026-10-01_11-08-39.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_4__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-252,4,252]__2026-10-01_09-42-20.csv',
    r'C:\Users\silic\Github\orion_sdk\tests\char\logs\rx_iq_char__v2__ant_sel_8__vdd_3p3__temp_25C__bias_NOM__av_2047__iq_[-252,4,252]__2026-09-30_22-10-04.csv',
]
out_dir = r'./logs'

states = 121          # phase states per 360 deg
lut_len = 128         # entries in the LUT memory
pad = 4               # entry index of state 0
gain_w = 10           # deg of phase error that one dB of gain deviation is worth when picking codes
ring = 32             # codes: max distance of a LUT entry from the reference contour (keeps picks on the same loop)
iters_max = 100       # joint_max: reweighting passes
iters = 15            # joint algo: offset / code refinement passes

step = 360 / states
wrap = lambda d: (d + 180) % 360 - 180
path_len = lambda seg: np.hypot(*np.diff(seg, axis=0).T).sum()
tag = lambda x: f'{x:g}'.replace('.', 'p')

# ---------------- config parsed from the first file name ----------------
m = re.search(r'rx_iq_char__(v\d+)__ant_sel_(\d+)__vdd_([^_]+)__temp_([^_]+)__bias_([^_]+)__av_(\d+)__', os.path.basename(csv_files[0]))
if not m:
    raise SystemExit(f'cannot parse version/vdd/temp/bias/av from {csv_files[0]}')
version, _, vdd, temp, bias, av = m.groups()


class Sweep:
    def __init__(self, csv):
        df = pd.read_csv(csv)
        gcols = [c for c in df.columns if c.startswith('Gain dB')]
        pcols = [c for c in df.columns if c.startswith('Phase deg')]
        k = int(np.argmin([abs(float(c.split()[-1].replace('GHz', '')) - freq) for c in gcols]))
        self.ghz = float(gcols[k].split()[-1].replace('GHz', ''))
        self.gain = df.pivot(index='Q', columns='I', values=gcols[k])
        phase = df.pivot(index='Q', columns='I', values=pcols[k])
        axes = (phase.index, phase.columns)
        # interpolate phase through cos/sin so the +-180 wrap does not corrupt it
        self._pc = RegularGridInterpolator(axes, np.cos(np.radians(phase.values)))
        self._ps = RegularGridInterpolator(axes, np.sin(np.radians(phase.values)))
        self._g = RegularGridInterpolator(axes, self.gain.values)

    def phase_at(self, i, q):
        return np.degrees(np.arctan2(self._ps(np.c_[q, i]), self._pc(np.c_[q, i])))

    def gain_at(self, i, q):
        return self._g(np.c_[q, i])

    def top_closed_contour(self, backoff=0):
        """Closed contour `backoff` dB below the highest-gain one that closes inside the grid: (level dB, path of (i, q))."""
        g = self.gain
        gen = contourpy.contour_generator(g.columns.values, g.index.values, g.values)
        span = max(g.columns.max() - g.columns.min(), g.index.max() - g.index.min())
        lvl_top = None
        for lvl in np.linspace(g.values.max(), g.values.min(), 1000):
            if lvl_top is not None and lvl > lvl_top - backoff:
                continue
            loops = [s for s in gen.lines(lvl) if len(s) > 3 and np.allclose(s[0], s[-1]) and path_len(s) > 0.2 * span]
            if loops and lvl_top is None:
                lvl_top = lvl   # highest-gain closed contour
                if backoff > 0:
                    continue
            if loops:
                return lvl, max(loops, key=path_len)
        raise RuntimeError('no closed contour')


sweeps = [Sweep(c) for c in csv_files]
m_ref = re.fullmatch(r'ref(\d+)', algo)
if m_ref is None and algo not in ('joint_rms', 'joint_max'):
    raise SystemExit("algo must be 'ref0'...'ref3', 'joint_rms' or 'joint_max'")
ref = int(m_ref.group(1)) if m_ref else 0   # reference channel (joint: initial guess and reported gain/phase)
if ref >= len(csv_files):
    raise SystemExit(f'{algo}: only {len(csv_files)} csv files given')
print(f'{len(sweeps)} channels, freq {sweeps[0].ghz:g} GHz, algo {algo}, gm {gm:g} dB, backoff {backoff:g} dB')

# candidate codes: multiples of 4 that every channel measured
codes = np.arange(-252, 253, 4)
I, Q = [a.ravel() for a in np.meshgrid(codes, codes)]
PH = np.array([s.phase_at(I, Q) for s in sweeps])
G = np.array([s.gain_at(I, Q) for s in sweeps])

# phase targets, in the reference channel's measured phase
target = -180 + step * (np.arange(states) + 1)


def circ_mean(err):
    return np.degrees(np.angle(np.mean(np.exp(1j * np.radians(err)), axis=-1)))


# ---------------- algo 'refN' ----------------
level, contour = sweeps[ref].top_closed_contour(backoff)
near = cKDTree(contour).query(np.c_[I, Q])[0] <= ring   # stay on the reference contour, not on other regions of equal gain
cand = np.where((np.abs(G[ref] - level) <= gm) & near)[0]
if len(cand) == 0:
    raise SystemExit('no codes within gm of the reference contour; increase gm')
sel = np.array([cand[np.argmin(wrap(PH[ref, cand] - t) ** 2 + (gain_w * (G[ref, cand] - level)) ** 2)] for t in target])

# ---------------- algos 'joint_rms' / 'joint_max' ----------------
if algo.startswith('joint'):
    lvl_c = G[:, sel].mean(axis=1)                          # per-channel gain level from the 'ref' LUT
    cand = np.where(np.all(np.abs(G - lvl_c[:, None]) <= gm, axis=0))[0]
    gpen = ((gain_w * (G[:, cand] - lvl_c[:, None])) ** 2).sum(axis=0)
    chan_sd = lambda s_: (lambda e: wrap(e - circ_mean(e)[:, None]).std(axis=1))(wrap(PH[:, s_] - target))
    w = np.ones(len(sweeps))                                # per-channel weights
    best_sel, best_max = sel, chan_sd(sel).max()
    for _ in range(iters if algo == 'joint_rms' else iters_max):
        off = circ_mean(wrap(PH[:, sel] - target))          # per-channel constant phase offset
        sel = np.array([cand[np.argmin((w[:, None] * wrap(PH[:, cand] - off[:, None] - t) ** 2).sum(axis=0) + gpen)] for t in target])
        sd_c = chan_sd(sel)
        if algo == 'joint_max':
            if sd_c.max() < best_max:
                best_sel, best_max = sel, sd_c.max()
            w *= (sd_c / sd_c.mean()) ** 2                  # push weight onto the worst channels
            w /= w.mean()
    if algo == 'joint_max':
        sel = best_sel

# ---------------- report ----------------
err = wrap(PH[:, sel] - target)
off = circ_mean(err)
err0 = wrap(err - off[:, None])
print(f'\n{"channel":<8}{"offset":>9}{"phase sd":>10}{"phase pk":>10}{"gain sd":>9}   (deg, dB; offset removed)')
for c in range(len(sweeps)):
    print(f'{c:<8}{off[c]:9.2f}{err0[c].std():10.2f}{np.abs(err0[c]).max():10.2f}{G[c, sel].std():9.2f}')
sd = err0.std(axis=1)
print(f'max phase sd across channels (spec): {sd.max():.2f} deg (channel {sd.argmax()})')

# ---------------- write xlsx ----------------
enc = lambda v: 256 - v if v < 0 else v   # bit 8 = sign, low 8 bits = magnitude

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Sheet1'
ws.append(['I-Code', 'Q-Code', 'Gain Error'])
for n in range(lut_len):
    k = sel[(n - pad) % states]
    i, q = int(I[k]), int(Q[k])
    r = n + 2
    ws.append([enc(i), enc(q), 0, i, q, float(G[ref, k]), float(PH[ref, k]),
               f'=$G${pad + 2}-G{r}' if n >= pad else None])

extra = ''.join(f'__{k}_{tag(v)}' for k, v, d in (('ring', ring, 32), ('gainw', gain_w, 10)) if v != d)   # only when changed from the default
name = f'{version}__rx_phase_lut__freq_{tag(freq)}__gm_{tag(gm)}__backoff_{tag(backoff)}{extra}__algo_{algo}__av_{av}__bias_{bias.lower()}__vdd_{vdd}__temp_{temp}.xlsx'
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, name)
wb.save(path)
print(f'\nLUT saved: {os.path.abspath(path)}')
