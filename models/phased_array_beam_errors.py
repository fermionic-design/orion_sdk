"""
Beam pointing error (azimuth / elevation) and sidelobe level of a 2D phased array for three cases:
ideal, quantized, quantized + random gain / phase errors. Script front end of phased_array_core.py
(the GUI is gui/phased_array_gui.py); see phased_array_core.py for the model description.
"""
import matplotlib.pyplot as plt
import phased_array_core as core

# ---------------- inputs ----------------
freq_ghz = 9.5
nx, ny = 32, 32                    # elements along x (azimuth) and y (elevation)
steer_az_deg = [0, 20, 40, 60]     # commanded azimuths  (all combinations with the elevations are run)
steer_el_deg = [0, 20, 40, 60]     # commanded elevations

taper = 'taylor'                   # 'uniform', 'taylor', 'chebyshev', 'hamming', 'hann', 'blackman', 'cosine', 'gaussian'
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

cfg = core.ArrayConfig(freq_ghz=freq_ghz, nx=nx, ny=ny, taper=taper, taper_sll_db=taper_sll_db, taper_nbar=taper_nbar,
                       taper_gauss_sigma=taper_gauss_sigma, phase_bits=phase_bits, gain_bits=gain_bits,
                       gain_step_db=gain_step_db, err_att_db=err_att_db, err_gain_rms_db=err_gain_rms_db,
                       err_phase_rms_deg=err_phase_rms_deg, nfft=nfft, element_cos_exp=element_cos_exp)

if __name__ == '__main__':
    arr = core.PhasedArray(cfg)
    steers = core.steering_list(steer_az_deg, steer_el_deg)
    res = arr.simulate(steers, n_trials, seed, core.progress_bar_printer())
    print('\n')

    lam_mm = 299.792458 / freq_ghz
    print(f'{nx} x {ny} elements, {freq_ghz:g} GHz, spacing lambda/2 = {lam_mm / 2:.2f} mm, taper {taper}'
          + (f' (sll {taper_sll_db:g} dB)' if taper in ('taylor', 'chebyshev') else ''))
    print(f'phase {phase_bits:g} bits ({arr.ph_step:.2f} deg step), gain {gain_bits} bits x {gain_step_db:g} dB '
          f'(max attenuation {arr.max_att:g} dB), {n_trials} Monte Carlo trials for quantized+rms\n')
    print(f'{"steer az,el":<12}{"case":<15}{"az err (deg)":>26}{"el err (deg)":>26}{"SLL dBc":>20}{"SLL err dB":>13}{"peak loss":>11}')
    print(f'{"":<27}{"mean":>9}{"rms":>8}{"p95":>9}{"mean":>9}{"rms":>8}{"p95":>9}{"mean":>10}{"worst":>10}{"mean":>13}{"dB":>11}')
    for _, r in res.table().iterrows():
        row = f'{r["Steer az (deg)"]:>4g},{r["Steer el (deg)"]:<7g}{r["Case"]:<15}'
        for n in ('az', 'el'):
            row += f'{r[n + " err mean (deg)"]:9.3f}{r[n + " err rms (deg)"]:8.3f}{r[n + " err p95 (deg)"]:9.3f}'
        row += f'{r["SLL mean (dBc)"]:10.1f}{r["SLL worst (dBc)"]:10.1f}{r["SLL error mean (dB)"]:13.1f}{r["Peak loss (dB)"]:11.2f}'
        print(row)
        if r['Case'] == 'quantized+rms':
            print()

    if show_plots:
        core.fig_pattern_cuts(res, plot_steer, fig=plt.figure(figsize=(13, 5)))
        core.fig_summary(res, fig=plt.figure(figsize=(10, 9)))
        core.fig_element_maps(arr.element_maps(map_steer_deg), taper, gain_step_db, gain_bits, fig=plt.figure(figsize=(12, 10)))
        plt.show()
