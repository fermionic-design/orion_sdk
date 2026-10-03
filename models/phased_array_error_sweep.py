"""
Pointing error and sidelobe error of the phased array model versus the rms phase and gain error of the
elements, with the errors independent of the attenuation state. Script front end of phased_array_core.py.

Uses the array, taper and quantization settings of phased_array_beam_errors.py (edit them there).
  left plot  : pointing error and sidelobe error vs rms gain error  (phase error held at hold_phase_deg)
  right plot : pointing error and sidelobe error vs rms phase error (gain error held at hold_gain_db)
Pointing error = rms over trials and steering angles of sqrt(az error^2 + el error^2).
Sidelobe error = mean over trials and steering angles of (sidelobe level - sidelobe level of the ideal array).
"""
import numpy as np
import matplotlib.pyplot as plt
import phased_array_core as core
from phased_array_beam_errors import cfg

steers = [(0, 0), (30, 0), (0, 30), (30, 30)]   # commanded (azimuth, elevation) in degrees
n_trials = 60                                   # Monte Carlo trials per point and steering angle
seed = 1
phase_rms_deg = np.arange(3, 10.1, 1.0)         # rms phase error sweep
gain_rms_db = np.arange(0.5, 2.51, 0.5)         # rms gain error sweep
hold_phase_deg = 6.5                            # phase error while the gain error is swept
hold_gain_db = 1.5                              # gain error while the phase error is swept

if __name__ == '__main__':
    arr = core.PhasedArray(cfg)
    vs_gain, vs_phase = arr.error_sweep(steers, n_trials, seed, phase_rms_deg, gain_rms_db, hold_phase_deg, hold_gain_db,
                                        core.progress_bar_printer())
    print('\n')
    print(f'{cfg.nx} x {cfg.ny} elements, {cfg.taper} taper, phase {cfg.phase_bits:g} bits, gain {cfg.gain_bits} bits x {cfg.gain_step_db:g} dB')
    print(f'\nphase error held at {hold_phase_deg:g} deg\n{vs_gain.iloc[:, :3].to_string(index=False)}')
    print(f'\ngain error held at {hold_gain_db:g} dB\n{vs_phase.iloc[:, :3].to_string(index=False)}')
    core.fig_error_sweep(vs_gain, vs_phase, f'{cfg.nx}x{cfg.ny}, {cfg.taper} taper', fig=plt.figure(figsize=(13, 5)))
    plt.show()
