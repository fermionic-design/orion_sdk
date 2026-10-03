"""
Pointing error and sidelobe error of the phased array model versus the rms phase and gain error of the
elements, with the errors independent of the attenuation state.

Uses the array, taper and quantization settings of phased_array_beam_errors.py (edit them there).
  left plot  : pointing error and sidelobe error vs rms gain error  (phase error held at hold_phase_deg)
  right plot : pointing error and sidelobe error vs rms phase error (gain error held at hold_gain_db)
Pointing error = rms over trials and steering angles of sqrt(az error^2 + el error^2).
Sidelobe error = mean over trials and steering angles of (sidelobe level - sidelobe level of the ideal array).
"""
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import phased_array_beam_errors as m

steers = [(0, 0), (30, 0), (0, 30), (30, 30)]   # commanded (azimuth, elevation) in degrees
n_trials = 60                                   # Monte Carlo trials per point and steering angle
seed = 1
phase_rms_deg = np.arange(3, 10.1, 1.0)         # rms phase error sweep
gain_rms_db = np.arange(0.5, 2.51, 0.5)         # rms gain error sweep
hold_phase_deg = 6.5                            # phase error while the gain error is swept
hold_gain_db = 1.5                              # gain error while the phase error is swept

rng = np.random.default_rng(seed)
ideal_sll = {s: m.analyze(m.element_weights(*s, 'ideal', rng))['sll'] for s in steers}
total = (len(phase_rms_deg) + len(gain_rms_db)) * len(steers) * n_trials
done = 0
t_start = time.time()


def evaluate(g_rms, p_rms):
    """(pointing error rms in deg, mean sidelobe error in dB) for constant rms gain / phase errors."""
    global done
    m.err_att_db = [0, 100]
    m.err_gain_rms_db = [g_rms, g_rms]
    m.err_phase_rms_deg = [p_rms, p_rms]
    rng = np.random.default_rng(seed)
    point, dsll = [], []
    for s in steers:
        for _ in range(n_trials):
            o = m.analyze(m.element_weights(*s, 'quantized+rms', rng))
            point.append((o['az'] - s[0]) ** 2 + (o['el'] - s[1]) ** 2)
            dsll.append(o['sll'] - ideal_sll[s])
            done += 1
            eta = str(datetime.timedelta(seconds=round((time.time() - t_start) / done * (total - done))))
            print(f'\r[{"#" * (30 * done // total):<30}] {100 * done // total:3d}%  ({done}/{total})  ETA {eta}', end='', flush=True)
    return np.sqrt(np.mean(point)), np.mean(dsll)


vs_gain = np.array([evaluate(g, hold_phase_deg) for g in gain_rms_db])
vs_phase = np.array([evaluate(hold_gain_db, p) for p in phase_rms_deg])
print('\n')

print(f'{m.nx} x {m.ny} elements, {m.taper} taper, phase {m.phase_bits:g} bits, gain {m.gain_bits} bits x {m.gain_step_db:g} dB')
print(f'\n{"gain rms (dB)":>14}{"pointing (deg)":>16}{"SLL error (dB)":>16}   phase error held at {hold_phase_deg:g} deg')
for x, (p, s) in zip(gain_rms_db, vs_gain):
    print(f'{x:14.2f}{p:16.4f}{s:16.2f}')
print(f'\n{"phase rms (deg)":>14}{"pointing (deg)":>16}{"SLL error (dB)":>16}   gain error held at {hold_gain_db:g} dB')
for x, (p, s) in zip(phase_rms_deg, vs_phase):
    print(f'{x:14.2f}{p:16.4f}{s:16.2f}')

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for a, x, y, xlabel, hold in ((ax[0], gain_rms_db, vs_gain, 'RMS gain error (dB)', f'phase error {hold_phase_deg:g} deg'),
                              (ax[1], phase_rms_deg, vs_phase, 'RMS phase error (deg)', f'gain error {hold_gain_db:g} dB')):
    l1, = a.plot(x, y[:, 0], 'o-', color='tab:blue', label='Pointing error (rms)')
    a.set_xlabel(xlabel)
    a.set_ylabel('Pointing error (deg)', color='tab:blue')
    a2 = a.twinx()
    l2, = a2.plot(x, y[:, 1], 's-', color='tab:orange', label='Sidelobe error')
    a2.set_ylabel('Sidelobe error (dB)', color='tab:orange')
    a.grid(True)
    a.legend(handles=[l1, l2], loc='upper left')
    a.set_title(f'{m.nx}x{m.ny}, {m.taper} taper, {hold} held')
fig.tight_layout()
plt.show()
