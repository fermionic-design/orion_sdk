"""
Generate a TX phase LUT (same xlsx format as final_lut/v2__tx_phase_lut__*.xlsx) from fine I/Q data: for every channel a
full-grid csv (tx_iq_char.py, I/Q step 4) and an optional axis-band csv (tx_iq_char.py sweep = 'axis', I/Q step 1 near the
I and Q axes). Only measured points are used (nothing is interpolated); a channel's measured points are the union of its
two csvs, and the LUT codes are picked among the (I, Q) points measured on every channel.

The LUT has 121 phase states, 360/121 = 2.975 deg apart, stored as 128 entries:
entry i holds state (i-4) mod 121, so entries 4...124 are the states and the rest wrap around.
The TX has no gain or phase correction, so the 'Gain Error' column is always 0; the gain variation over the states
is reported (gain sd / range) but cannot be corrected, it is limited by the gain margin gm.

Algorithm: 'joint_max' (minimize the worst channel's phase std dev; gain of every channel stays within gm dB of its own
level), then the codes are re-picked with state 0 as the phase reference of every channel and the per-channel mean error
driven to zero. The sweep measures phase error relative to state 0, so a state-0 code that is off from the average of the
other states shows up as an average error on every other state; anchoring on state 0 and shifting the targets until the
mean is zero removes it.

With a single channel the LUT is optimal for that channel only; give one csv pair per TX channel (the first is the
reference) to get a LUT that is shared by all of them.

Knobs
  freq  : GHz, nearest measured frequency is used
  gm    : gain margin in dB - the gain of every channel at every entry must be within +-gm of that channel's own level
  backoff : dB below the highest-gain closed contour (of the reference channel) used as the gain level
  suffix  : appended to the file name
"""
import os
import re
import numpy as np
import pandas as pd
import contourpy
import openpyxl
from scipy.spatial import cKDTree

freq = 11.5
gm = 1.0
backoff = 0    # dB below the highest-gain closed contour used as the LUT gain level

D = r"C:\Users\silic\Github\orion_sdk\tests\char\logs" + "\\"
csv_files = [   # grid and axis csv of every channel; the first channel is the reference (gain level, initial picks)
    D + "chip_55__tx_iq_char__v2__ant_sel_all_1__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[axis_w11_s1_a4]__2026-11-04_11-32-39.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_1__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[-252,4,252]__2026-11-04_10-03-50.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_2__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[axis_w11_s1_a4]__2026-11-04_20-15-36.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_2__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[-252,4,252]__2026-11-04_22-04-08.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_8__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[axis_w11_s1_a4]__2026-11-05_11-29-04.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_8__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[-252,4,252]__2026-11-05_12-12-07.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_4__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[axis_w11_s1_a4]__2026-11-05_10-33-14.csv",
    D + "chip_55__tx_iq_char__v2__ant_sel_all_4__vdd_2p7__temp_25C__bias_MAX__pin_10__av_2047__iq_[-252,4,252]__2026-11-05_17-09-54.csv",
]


out_dir = r'./logs'
suffix = 'chip_55_tx0'     # optional custom suffix for the file name

states = 121          # phase states per 360 deg
lut_len = 128         # entries in the LUT memory
pad = 4               # entry index of state 0
gain_w = 10           # deg of phase error that one dB of gain deviation is worth when picking codes
ring = 32             # codes: max distance of a reference pick from the reference contour (keeps picks on the same loop)
iters_joint = 100     # joint_max: reweighting passes
iters_anchor = 20     # channel reweighting passes per state-0 candidate
n_anchor = 6          # best state-0 codes that get the reweighting + swap polish
stride_i0 = 8         # every this many candidate codes is tried as state 0
start_deg = 45        # state 0 (phase code 0) is taken at this angle in the I/Q plane, away from the I and Q axes where phase changes fastest
                      # per code (the LUT is rotated so it starts there); None: state 0 can be anywhere on the contour
start_tol_deg = 10    # state-0 codes must be within +- this many degrees of start_deg
max_i0 = 600          # most state-0 codes tried when start_deg is set
mean_w = 1500         # cost of 1 deg of mean error (one channel) in the swap polish; large -> the mean is driven to ~0
polish_k = 200        # swap polish: alternative codes tried per state (the lowest cost ones)
polish_sweeps = 12

step = 360 / states
wrap = lambda d: (d + 180) % 360 - 180
path_len = lambda seg: np.hypot(*np.diff(seg, axis=0).T).sum()
tag = lambda x: f'{x:g}'.replace('.', 'p')
circ_mean = lambda e: np.degrees(np.angle(np.mean(np.exp(1j * np.radians(e)), axis=-1)))

# ---------------- config parsed from the first file name ----------------
m = re.search(r'tx_iq_char__(v\d+)__ant_sel_(?:all_)?(\d+)__vdd_([^_]+)__temp_([^_]+)__bias_(.+?)__pin_(-?\d+(?:\.\d+)?)__av_(\d+)__', os.path.basename(csv_files[0]))
if not m:
    raise SystemExit(f'cannot parse version/vdd/temp/bias/av from {csv_files[0]}')
version, _, vdd, temp, bias, pin, av = m.groups()


def load(csv):
    df = pd.read_csv(csv)
    gcols = [c for c in df.columns if c.startswith('Gain dB')]
    pcols = [c for c in df.columns if c.startswith('Phase deg')]
    k = int(np.argmin([abs(float(c.split()[-1].replace('GHz', '')) - freq) for c in gcols]))
    d = pd.DataFrame({'I': df.I, 'Q': df.Q, 'g': df[gcols[k]], 'p': df[pcols[k]]})
    far = d[(d.I.abs() > 60) | (d.Q.abs() > 60)]
    if (far.g < -40).mean() > 0.1:   # away from the null at the origin the gain is never this low
        raise SystemExit(f'{os.path.basename(csv)}: {(far.g < -40).mean():.0%} of the points are below -40 dB (no signal?), re-measure or remove it')
    return d


def top_closed_contour(grid):
    """Closed contour `backoff` dB below the highest-gain one that closes inside the grid: (level dB, path of (i, q))."""
    g = grid.pivot(index='Q', columns='I', values='g')
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


# ---------------- channels: grid + axis csv per (chip, ant) ----------------
chan = {}
for f in csv_files:
    mm = re.search(r'(chip_\d+)__tx_iq_char__.*?__ant_sel_(?:all_)?(\d+)__.*?__iq_\[([^\]]*)\]__', os.path.basename(f))
    if not mm:
        raise SystemExit(f'cannot parse chip / ant_sel / iq from {f}')
    chan.setdefault((mm[1], int(mm[2])), {})['axis' if mm[3].startswith('axis') else 'grid'] = f
names = [f'{c[-2:]} ant {a}' for c, a in chan]
for n, v in zip(names, chan.values()):
    if 'grid' not in v:
        raise SystemExit(f'{n}: no full-grid csv')
    if 'axis' not in v:
        print(f'warning: {n} has no axis csv, the axis-only codes are not candidates')

grid0 = load(next(iter(chan.values()))['grid'])
meas = []
for v in chan.values():
    df = pd.concat([load(v['grid'])] + ([load(v['axis'])] if 'axis' in v else []))
    meas.append(df.drop_duplicates(['I', 'Q']).set_index(['I', 'Q']))
common = meas[0].index
for mdf in meas[1:]:
    common = common.intersection(mdf.index)
I = common.get_level_values('I').values
Q = common.get_level_values('Q').values
G = np.array([mdf.loc[common, 'g'].values for mdf in meas])
PH = np.array([mdf.loc[common, 'p'].values for mdf in meas])
C = len(names)
print(f'{C} channels {names}, {len(common)} codes measured on every channel, freq {freq:g} GHz, gm {gm:g} dB, backoff {backoff:g} dB')

target = -180 + step * (np.arange(states) + 1)

# ---------------- reference picks (algo 'ref0') ----------------
level, contour = top_closed_contour(grid0)
near = cKDTree(contour).query(np.c_[I, Q])[0] <= ring   # stay on the reference contour, not on other regions of equal gain
cand0 = np.where((np.abs(G[0] - level) <= gm) & near)[0]
if len(cand0) == 0:
    raise SystemExit('no codes within gm of the reference contour; increase gm')
sel = np.array([cand0[np.argmin(wrap(PH[0, cand0] - t) ** 2 + (gain_w * (G[0, cand0] - level)) ** 2)] for t in target])

# ---------------- gain-constrained candidates ----------------
lvl_c = G[:, sel].mean(axis=1)                              # per-channel gain level from the reference picks
cand = np.where(np.all(np.abs(G - lvl_c[:, None]) <= gm, axis=0))[0]
if len(cand) == 0:
    spread = np.abs(G[:, cand0] - lvl_c[:, None]).max(axis=1)
    raise SystemExit(f'no code is within gm = {gm:g} dB of every channel\'s own gain level; worst gain spread per channel '
                     f'{dict(zip(names, spread.round(2)))}, increase gm or remove a channel')
gpen = ((gain_w * (G[:, cand] - lvl_c[:, None])) ** 2).sum(axis=0)
Pc = PH[:, cand]
print(f'reference gain level {level:.2f} dB, {len(cand)} candidate codes')


def cost_of(off, w):
    """[state, candidate] cost: weighted squared phase error against the targets shifted by each channel's offset + gain penalty."""
    cost = np.tile(gpen, (states, 1))
    for c in range(C):
        cost += w[c] * wrap(Pc[c][None, :] - off[c] - target[:, None]) ** 2
    return cost


# ---------------- joint_max (offsets calibrated out) ----------------
chan_sd = lambda s_: (lambda e: wrap(e - circ_mean(e)[:, None]).std(axis=1))(wrap(PH[:, s_] - target))
w = np.ones(C)
best_sel, best_max = sel, chan_sd(sel).max()
for _ in range(iters_joint):
    off = circ_mean(wrap(PH[:, sel] - target))
    sel = cand[np.argmin(cost_of(off, w), axis=1)]
    sd_c = chan_sd(sel)
    if sd_c.max() < best_max:
        best_sel, best_max = sel, sd_c.max()
    w *= (sd_c / sd_c.mean()) ** 2
    w /= w.mean()
sel = best_sel
sel_joint = sel.copy()
print(f'joint_max: worst channel phase sd {best_max:.2f} deg (offset removed)')


# ---------------- re-pick with state 0 as the phase reference, mean error driven to zero ----------------
def pred_err(s_):   # phase error relative to state 0, as the p_idx sweep measures it: [channel, state]
    return wrap(PH[:, s_] - PH[:, [s_[0]]] - step * np.arange(states))


def polish(sel, off, w):
    """Swap codes state by state (state 0 stays) so that every channel's mean error relative to state 0 goes to ~0,
    at the smallest increase of the phase cost: state k may take any of its polish_k cheapest codes."""
    sel = sel.copy()
    i0 = sel[0]
    cost = cost_of(off, w)
    ph_rel = PH[:, i0]
    pos = {c: n for n, c in enumerate(cand)}
    cur = np.array([pos[c] for c in sel])
    err = lambda idx, k: wrap(Pc[:, idx] - ph_rel[:, None] - step * k)   # [channel, ...] error relative to state 0 at state k
    e = wrap(Pc[:, cur] - ph_rel[:, None] - step * np.arange(states))   # [channel, state]
    mean = e.mean(axis=1)
    rng = np.random.default_rng(0)
    for _ in range(polish_sweeps):
        for k in rng.permutation(np.arange(1, states)):
            idx = np.unique(np.r_[np.argpartition(cost[k], polish_k)[:polish_k], cur[k]])
            e_new = err(idx, k)                                         # [channel, candidate]
            mean_new = mean[:, None] + (e_new - e[:, [k]]) / states
            j = cost[k, idx] + mean_w * (mean_new ** 2).sum(axis=0)
            b = np.argmin(j)
            mean, e[:, k], cur[k] = mean_new[:, b], e_new[:, b], idx[b]
        if np.abs(mean).max() < 0.01:
            break
    return cand[cur]


def anchored(i0, w=None):
    """Codes for all states with state 0 = code i0. The phase comb is rooted at state 0 of every channel (the target of
    state k is that channel's own state-0 phase + k * 360/121), so the error is exactly what the sweep measures
    (relative to state 0). Returns (codes, rms per channel, mean per channel)."""
    base = wrap(PH[:, i0] - target[0])
    sel = cand[np.argmin(cost_of(base, np.ones(C) if w is None else w), axis=1)]
    sel[0] = i0
    e = pred_err(sel)
    return sel, np.sqrt(np.mean(e ** 2, axis=1)), e.mean(axis=1)


score = lambda rms, mean: rms.max() + 3 * np.abs(mean).max()   # worst channel rms, with the mean error weighted up

# state 0 can be any code on the contour (the sweep only sees phase relative to it), and its codes set every channel's mean
# error: try many, keep the best few, then reweight the channels and swap codes to bring the means down
if start_deg is None:
    pool = cand[::stride_i0]
else:
    near_start = np.abs(wrap(np.degrees(np.arctan2(Q[cand], I[cand])) - start_deg)) <= start_tol_deg
    if not near_start.any():
        raise SystemExit(f'no candidate code within {start_tol_deg:g} deg of {start_deg:g} deg in the I/Q plane; increase start_tol_deg or gm')
    pool = cand[near_start]
    pool = pool[::int(np.ceil(len(pool) / max_i0))]
first = [anchored(i0) + (i0,) for i0 in pool]
first.sort(key=lambda r: score(r[1], r[2]))
best = None
for sel0, _, _, i0 in first[:n_anchor]:
    base = wrap(PH[:, i0] - target[0])
    w = np.ones(C)
    sel_t = sel0
    for _ in range(iters_anchor):                                   # reweight channels to equalize their rms
        sel_t, rms, mean = anchored(i0, w)
        w *= (rms / rms.mean()) ** 2
        w /= w.mean()
    sel_p = polish(sel_t, base, w)
    e = pred_err(sel_p)
    rms, mean = np.sqrt(np.mean(e ** 2, axis=1)), e.mean(axis=1)
    if best is None or score(rms, mean) < best[0]:
        best = (score(rms, mean), sel_p)
sel = best[1]
e = pred_err(sel)
print(f'state 0 at ({I[sel[0]]}, {Q[sel[0]]}), {np.degrees(np.arctan2(Q[sel[0]], I[sel[0]])):.0f} deg in the I/Q plane')
print(f'state 0 anchored ({len(pool)} state-0 codes tried): worst channel rms {np.sqrt(np.mean(e ** 2, axis=1)).max():.2f} deg, '
      f'|mean| {np.abs(e.mean(axis=1)).max():.2f} deg')

# ---------------- report ----------------
e = pred_err(sel)
print(f'\n{len(set(sel))} unique codes of {states}')
rel = G[:, sel] - G[:, [sel[0]]]   # gain at each state relative to state 0 (not correctable on the TX)
print(f'{"channel":<10}{"sd":>6}{"rms":>7}{"peak":>7}{"mean":>8}{"gain dB":>9}{"gain sd":>9}{"gain pp":>9}   '
      f'(deg, dB; phase error relative to state 0, as the sweep measures it; gain pp = max - min over the states)')
for c, n in enumerate(names):
    print(f'{n:<10}{e[c].std():6.2f}{np.sqrt(np.mean(e[c] ** 2)):7.2f}{np.abs(e[c]).max():7.2f}{e[c].mean():+8.3f}'
          f'{G[c, sel].mean():9.2f}{G[c, sel].std():9.2f}{np.ptp(rel[c]):9.2f}')
print(f'worst channel: sd {e.std(axis=1).max():.2f} deg (spec), rms {np.sqrt(np.mean(e ** 2, axis=1)).max():.2f} deg, '
      f'|mean| {np.abs(e.mean(axis=1)).max():.3f} deg')

# ---------------- write xlsx ----------------
enc = lambda v: 256 - v if v < 0 else v   # bit 8 = sign, low 8 bits = magnitude

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Sheet1'
ws.append(['I-Code', 'Q-Code', 'Gain Error'])
for n in range(lut_len):
    k = sel[(n - pad) % states]
    i, q = int(I[k]), int(Q[k])
    ws.append([enc(i), enc(q), 0, i, q, float(G[0, k]), float(PH[0, k])])

name = f'{version}__tx_phase_lut__freq_{tag(freq)}__gm_{tag(gm)}__backoff_{tag(backoff)}__algo_joint_max__av_{av}__bias_{bias.lower()}__pin_{pin}__vdd_{vdd}__temp_{temp}' + (f'__{suffix.strip(" _")}' if suffix.strip(' _') else '') + '.xlsx'
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, name)
wb.save(path)
print(f'\nLUT saved: {os.path.abspath(path)}')
