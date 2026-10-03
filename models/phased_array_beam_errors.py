"""
Beam pointing error (azimuth / elevation) and sidelobe level of a 2D phased array, for three cases:
  ideal         : floating point phase and gain
  quantized     : phase and gain rounded to the available states (phase_bits, gain_bits / gain_step_db)
  quantized+rms : quantized, plus random gain (dB) and phase (deg) errors whose rms depends on the gain
                  (attenuation) state of the element, Monte Carlo over n_trials

Geometry: nx x ny elements in the x-y plane, spacing lambda/2 (so the pattern does not depend on the
frequency; freq only sets the physical spacing that is printed), boresight along z.
Direction cosines: u = sin(az) cos(el), v = sin(el).
Array factor: AF(u, v) = sum a_mn exp(j pi ((m - cx) (u - u0) + (n - cy) (v - v0))), computed with a zero padded FFT.

Pointing error = peak direction found in the pattern - commanded direction (parabolic peak refinement).
Peak sidelobe level = highest point outside the main lobe, in dB below the peak. The main lobe is the
region around the peak that falls monotonically down to the first nulls.
Sidelobe error = sidelobe level of the case - sidelobe level of the ideal case at the same steering.
"""
import datetime
import time
from collections import deque
import numpy as np
from scipy.ndimage import binary_dilation
from scipy.signal import windows

# ---------------- inputs ----------------
freq_ghz = 9.5
nx, ny = 32, 32                    # elements along x (azimuth) and y (elevation)
steer_az_deg = [0, 20, 40, 60]     # commanded azimuths  (all combinations with the elevations are run)
steer_el_deg = [0, 20, 40, 60]     # commanded elevations

taper = 'taylor'                  # 'uniform', 'taylor', 'chebyshev', 'hamming', 'hann', 'blackman', 'cosine', 'gaussian'
taper_sll_db = 30                  # sidelobe level for taylor / chebyshev
taper_nbar = 4                     # taylor
taper_gauss_sigma = 0.4            # gaussian, std as a fraction of the half aperture

phase_bits = 7                     # phase states = 2**phase_bits (can be fractional, e.g. np.log2(121))
gain_bits = 6                      # gain (attenuation) states = 2**gain_bits
gain_step_db = 0.5                 # attenuation step; state 0 = no attenuation

# rms errors vs the attenuation state of the element (interpolated, held outside the table)
err_att_db = [0, 5, 10, 15, 20, 25, 30]                 # attenuation (dB)
err_gain_rms_db = [0.5, 1.0, 1.5, 2.0, 1.0, 1.5, 2.0]   # rms gain error (dB) at those attenuations
err_phase_rms_deg = [3, 4, 5, 6, 7, 8, 9]               # rms phase error (deg) at those attenuations
n_trials = 200                                          # Monte Carlo trials for the quantized+rms case
seed = 1

nfft = 512                         # pattern grid is nfft x nfft over u, v in [-1, 1)
element_cos_exp = 0.0              # element pattern cos(theta)**exp (0 = isotropic)
show_plots = True
plot_steer = 0                     # index (in the steering list) of the steering shown in the pattern cuts
map_steer_deg = 30                 # steering angle used for the element phase maps (azimuth-only and elevation-only)

CASES = ('ideal', 'quantized', 'quantized+rms')

# ---------------- setup ----------------
cx, cy = (nx - 1) / 2, (ny - 1) / 2
X, Y = np.meshgrid(np.arange(nx) - cx, np.arange(ny) - cy)           # [ny, nx]
ph_step = 360 / 2 ** phase_bits
max_att = (2 ** gain_bits - 1) * gain_step_db
u_grid = np.arange(nfft) * 2 / nfft - 1
U, V = np.meshgrid(u_grid, u_grid)                                   # [v, u]
mask = U ** 2 + V ** 2 < 1
elem = np.where(mask, np.sqrt(np.clip(1 - U ** 2 - V ** 2, 0, 1)) ** element_cos_exp, 0)


def window(n):
    if taper == 'uniform':
        return np.ones(n)
    if taper == 'taylor':
        return windows.taylor(n, nbar=taper_nbar, sll=taper_sll_db, norm=False)
    if taper == 'chebyshev':
        return windows.chebwin(n, at=taper_sll_db)
    if taper == 'hamming':
        return windows.hamming(n)
    if taper == 'hann':
        return windows.hann(n + 2)[1:-1]            # no zero edge elements
    if taper == 'blackman':
        return windows.blackman(n + 2)[1:-1]
    if taper == 'cosine':
        return windows.cosine(n)
    if taper == 'gaussian':
        return windows.gaussian(n, std=taper_gauss_sigma * (n - 1) / 2)
    raise SystemExit(f'unknown taper {taper}')


a_taper = np.outer(window(ny), window(nx))
a_taper /= a_taper.max()                                              # strongest element = no attenuation


def element_weights(az_deg, el_deg, case, rng):
    u0 = np.sin(np.radians(az_deg)) * np.cos(np.radians(el_deg))
    v0 = np.sin(np.radians(el_deg))
    phase = -180 * (X * u0 + Y * v0)                                  # degrees, steers the beam to (u0, v0)
    amp = a_taper
    if case == 'ideal':
        return amp * np.exp(1j * np.radians(phase))
    phase = np.round((phase % 360) / ph_step) * ph_step
    att = np.clip(np.round(-20 * np.log10(amp) / gain_step_db) * gain_step_db, 0, max_att)
    amp = 10 ** (-att / 20)
    if case == 'quantized+rms':
        amp = amp * 10 ** (rng.normal(size=amp.shape) * np.interp(att, err_att_db, err_gain_rms_db) / 20)
        phase = phase + rng.normal(size=amp.shape) * np.interp(att, err_att_db, err_phase_rms_deg)
    return amp * np.exp(1j * np.radians(phase))


def main_lobe(P, i0, j0):
    """Region around the peak that decreases away from it (4-connected), slightly dilated."""
    ml = np.zeros(P.shape, bool)
    ml[i0, j0] = True
    queue = deque([(i0, j0)])
    while queue:
        i, j = queue.popleft()
        lim = P[i, j] * 1.01
        for ii, jj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= ii < nfft and 0 <= jj < nfft and not ml[ii, jj] and mask[ii, jj] and P[ii, jj] <= lim:
                ml[ii, jj] = True
                queue.append((ii, jj))
    return binary_dilation(ml, iterations=2)


def analyze(w):
    P = np.abs(np.fft.fftshift(np.fft.ifft2(w, s=(nfft, nfft)))) * nfft ** 2 * elem   # [v, u]
    i, j = np.unravel_index(np.argmax(P), P.shape)
    di = dj = 0.0
    if 0 < i < nfft - 1 and 0 < j < nfft - 1:                                         # parabolic peak refinement
        d = lambda a, b, c: 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
        di, dj = d(P[i - 1, j], P[i, j], P[i + 1, j]), d(P[i, j - 1], P[i, j], P[i, j + 1])
    u_p, v_p = u_grid[j] + dj * 2 / nfft, u_grid[i] + di * 2 / nfft
    el = np.degrees(np.arcsin(np.clip(v_p, -1, 1)))
    az = np.degrees(np.arcsin(np.clip(u_p / np.cos(np.radians(el)), -1, 1)))
    side = mask & ~main_lobe(P, i, j)
    sll = 20 * np.log10(P[side].max() / P[i, j])
    return dict(az=az, el=el, sll=sll, peak=P[i, j], P=P, i=i, j=j)


# ---------------- run ----------------
steers = [(az, el) for el in steer_el_deg for az in steer_az_deg
          if np.sin(np.radians(az)) ** 2 * np.cos(np.radians(el)) ** 2 + np.sin(np.radians(el)) ** 2 < 1]
rng = np.random.default_rng(seed)
res = {}   # (case, steer index) -> dict of arrays over trials
total = len(steers) * (len(CASES) - 1 + n_trials)   # patterns to compute
done = 0
t_start = time.time()
for s, (az0, el0) in enumerate(steers):
    for case in CASES:
        trials = n_trials if case == 'quantized+rms' else 1
        out = []
        for _ in range(trials):
            out.append(analyze(element_weights(az0, el0, case, rng)))
            done += 1
            eta = str(datetime.timedelta(seconds=round((time.time() - t_start) / done * (total - done))))
            print(f'\r[{"#" * (30 * done // total):<30}] {100 * done // total:3d}%  ({done}/{total})  ETA {eta}', end='', flush=True)
        res[case, s] = dict(az_err=np.array([o['az'] - az0 for o in out]), el_err=np.array([o['el'] - el0 for o in out]),
                            sll=np.array([o['sll'] for o in out]), peak=np.array([o['peak'] for o in out]), first=out[0])

print('\n')

# ---------------- report ----------------
lam_mm = 299.792458 / freq_ghz
print(f'{nx} x {ny} elements, {freq_ghz:g} GHz, spacing lambda/2 = {lam_mm / 2:.2f} mm, taper {taper}'
      + (f' (sll {taper_sll_db:g} dB)' if taper in ('taylor', 'chebyshev') else ''))
print(f'phase {phase_bits:g} bits ({ph_step:.2f} deg step), gain {gain_bits} bits x {gain_step_db:g} dB (max attenuation {max_att:g} dB), '
      f'{n_trials} Monte Carlo trials for quantized+rms\n')
print(f'{"steer az,el":<12}{"case":<15}{"az err (deg)":>26}{"el err (deg)":>26}{"SLL dBc":>20}{"SLL err dB":>13}{"peak loss":>11}')
print(f'{"":<27}{"mean":>9}{"rms":>8}{"p95":>9}{"mean":>9}{"rms":>8}{"p95":>9}{"mean":>10}{"worst":>10}{"mean":>13}{"dB":>11}')
for s, (az0, el0) in enumerate(steers):
    ideal = res['ideal', s]
    for case in CASES:
        r = res[case, s]
        row = f'{az0:>4g},{el0:<7g}{case:<15}'
        for e in (r['az_err'], r['el_err']):
            row += f'{e.mean():9.3f}{np.sqrt(np.mean(e ** 2)):8.3f}{np.percentile(np.abs(e), 95):9.3f}'
        row += f'{r["sll"].mean():10.1f}{r["sll"].max():10.1f}{(r["sll"] - ideal["sll"]).mean():13.1f}'
        row += f'{(20 * np.log10(r["peak"] / ideal["peak"])).mean():11.2f}'
        print(row)
    print()

# ---------------- plots ----------------
if show_plots:
    import matplotlib.pyplot as plt
    az0, el0 = steers[plot_steer]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for case in CASES:
        o = res[case, plot_steer]['first']
        P = 20 * np.log10(np.maximum(o['P'], 1e-12) / res['ideal', plot_steer]['peak'])
        cut_u, cut_v = P[o['i'], :], P[:, o['j']]                      # through the peak
        v_row = u_grid[o['i']]
        az_axis = np.degrees(np.arcsin(np.clip(u_grid / np.cos(np.arcsin(v_row)), -1, 1)))
        ok = np.abs(u_grid / np.cos(np.arcsin(v_row))) < 1
        ax[0].plot(az_axis[ok], cut_u[ok], label=case)
        ax[1].plot(np.degrees(np.arcsin(u_grid[mask[:, o['j']]])), cut_v[mask[:, o['j']]], label=case)
    ax[0].set_xlabel('Azimuth (deg)'); ax[1].set_xlabel('Elevation (deg)')
    for a, t in zip(ax, ('azimuth cut', 'elevation cut')):
        a.set_ylabel('Relative power (dB)'); a.set_ylim(-60, 3); a.grid(True); a.legend()
        a.set_title(f'{t} through the peak, steered to az {az0:g}, el {el0:g} deg ({taper})')
    fig.tight_layout()

    fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    x = np.arange(len(steers))
    for k, case in enumerate(CASES):
        off = (k - 1) * 0.25
        ax[0].bar(x + off, [np.sqrt(np.mean(res[case, s]['az_err'] ** 2)) for s in x], 0.25, label=case)
        ax[1].bar(x + off, [np.sqrt(np.mean(res[case, s]['el_err'] ** 2)) for s in x], 0.25, label=case)
        ax[2].bar(x + off, [res[case, s]['sll'].mean() for s in x], 0.25, label=case)
    ax[0].set_ylabel('Azimuth error rms (deg)'); ax[1].set_ylabel('Elevation error rms (deg)'); ax[2].set_ylabel('Peak SLL (dBc)')
    ax[2].set_xticks(x, [f'{a:g},{e:g}' for a, e in steers]); ax[2].set_xlabel('Commanded azimuth, elevation (deg)')
    for a in ax:
        a.grid(True, axis='y'); a.legend(fontsize=8)
    fig.tight_layout()

    # element maps: phase needed to steer map_steer_deg in azimuth / in elevation, and the gain of every element
    extent = [-cx - 0.5, cx + 0.5, -cy - 0.5, cy + 0.5]   # element position in units of the spacing (lambda/2)
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))
    for a, (name, az_s, el_s) in zip(ax[0], ((f'Phase for {map_steer_deg:g} deg azimuth steering', map_steer_deg, 0),
                                             (f'Phase for {map_steer_deg:g} deg elevation steering', 0, map_steer_deg))):
        u0, v0 = np.sin(np.radians(az_s)) * np.cos(np.radians(el_s)), np.sin(np.radians(el_s))
        im = a.imshow((-180 * (X * u0 + Y * v0)) % 360, origin='lower', extent=extent, cmap='twilight', vmin=0, vmax=360)
        a.set_title(name)
        fig.colorbar(im, ax=a, label='Phase (deg)')
    att_q = np.clip(np.round(-20 * np.log10(a_taper) / gain_step_db) * gain_step_db, 0, max_att)
    for a, (name, g) in zip(ax[1], ((f'Gain, ideal ({taper} taper)', 20 * np.log10(a_taper)),
                                    (f'Gain, quantized ({gain_step_db:g} dB steps, {gain_bits} bits)', -att_q))):
        im = a.imshow(g, origin='lower', extent=extent, cmap='viridis', vmin=min(g.min(), -1), vmax=0)
        a.set_title(name)
        fig.colorbar(im, ax=a, label='Relative gain (dB)')
    for a in ax.ravel():
        a.set_xlabel('x element position (lambda/2)')
        a.set_ylabel('y element position (lambda/2)')
    fig.tight_layout()
    plt.show()
