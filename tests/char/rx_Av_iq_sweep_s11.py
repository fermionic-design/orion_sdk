# -- coding: utf-8 --
version = 'v2'
bias = 'NOM'    # RX bias: 'NOM' or 'LOW'
ant_sel = 0x1   # RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8

f_min, f_max, f_step = 7, 13, 0.25
f_mark = 9.5   # GHz: marker and printed values
show_rms = 1   # 1: print rms along with sd in the error stats, 0: sd only
sweep = 'phase'   # 'phase' (p_idx 4...124), 'gain' (g_idx 0...63) or 'both' (gain outer loop, phase inner loop)
g_start, g_stop, g_step = 0, 63, 10   # gain code range (inclusive) and step, used when sweep is 'gain' or 'both'
lut_switch = 30 # gain codes above this use the 2nd RX LUT (set_freq('11G'))
lut2_backoff_db = 5   # backoff of the 2nd LUT: after the switch the programmed gain index is reduced by backoff/0.5 steps

gain_lut = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_gain_lut__freq_9p5__algo_joint_max__iq_[264,464]__bias_nom__vdd_3p3__temp_25C.xlsx'   # RX gain LUT (phase correction codes = 0)

ph_lut = '0dB'   # '0dB', '5dB', or 'switch' (switch LUTs at lut_switch gain code)
ph_lut_0dB = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_nom__vdd_3p3__temp_25C__chip_[51,52,53,54].xlsx'
ph_lut_5db = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_phase_lut__freq_9p5__gm_1__backoff_5__algo_joint_max__av_2047__bias_nom__vdd_3p3__temp_25C.xlsx'

d1 = 0.1
d2 = 0.2   # delay after clearing averaging

import sys
sys.path.append('../../include')

from instruments import instruments
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import numpy as np
import csv
import datetime
import os
import time

instruments = instruments(required_instruments=['vna'])
instruments.vna.init(num_win=4)
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg(3, 'S11_GAIN')    # S11 magnitude (dB)
instruments.vna.cfg(4, 'S11_PHASE')   # S11 phase (deg)
instruments.vna.cfg_freq(start=f_min*1e9, stop=f_max*1e9, step=f_step*1e9)
instruments.vna.cfg_pwr(pwr=-40)
instruments.vna.add_marker(win_id=1, marker_id=1, val=f_mark*1e9)
instruments.vna.add_marker(win_id=2, marker_id=1, val=f_mark*1e9)
instruments.vna.add_marker(win_id=3, marker_id=1, val=f_mark*1e9)
instruments.vna.add_marker(win_id=4, marker_id=1, val=f_mark*1e9)
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

lut1, lut2 = {'0dB': (ph_lut_0dB, ph_lut_0dB),
             '5dB': (ph_lut_5db, ph_lut_5db),
             'switch': (ph_lut_0dB, ph_lut_5db)}[ph_lut]   # phase LUTs for the 1st (9G) and 2nd (11G) RX LUT

orion_hal.init_lut_new(r'C:/Users/silic/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           gain_lut,
                           lut1,
                           gain_lut,
                           lut2)

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx(bias)
orion_hal.set_tr_mask(rx_mask=ant_sel)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)
# orion_hal.dac_cfg(pa_sel=ant_sel, lna_sel=ant_sel, LNA0=19)

orion_hal.set_lut_idx(4,0, 0xF)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.write(":SENS:AVER:CLE")
time.sleep(d2)
instruments.vna.norm(win_id=2)

fi = int(round((f_mark-f_min)/f_step))
step = 360/121   # deg per LUT state
wrap = lambda d: (d + 180) % 360 - 180

p_idxs = range(4, 125) if sweep in ('phase', 'both') else [4]
g_idxs = range(g_start, g_stop + 1, g_step) if sweep in ('gain', 'both') else [0]

tag = lambda x: f'{x:g}'.replace('.', 'p')
g_tag = f'{g_idxs[0]}' if len(g_idxs) == 1 else f'{g_idxs[0]},{g_step},{g_idxs[-1]}'
p_tag = f'{p_idxs[0]}' if len(p_idxs) == 1 else f'{p_idxs[0]},1,{p_idxs[-1]}'
os.makedirs('./logs', exist_ok=True)
csv_path = f'./logs/rx_Av_iq_sweep_s11__{version}__ant_sel_{ant_sel}__bias_{bias}__sweep_{sweep}__g_[{g_tag}]__p_[{p_tag}]__freq_{tag(f_mark)}__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.csv'
csv_fh = open(csv_path, 'w', newline='')
csv_out = csv.writer(csv_fh)
csv_out.writerow(['g_idx', 'p_idx', 'Gain dB', 'Phase deg', 'Gain err dB', 'Phase err deg', 'g_prog',
                  'S11 dB', 'S11 phase deg', 'S11 dB chg', 'S11 phase chg deg'])

rms = lambda e: f', rms = {np.sqrt(np.mean(np.square(e))):.2f}' if show_rms else ''
stats = lambda e: f'sd = {np.std(e):.2f}{rms(e)}'
gain_err, phase_err = [], []
s11_chg, s11_ph_chg = [], []   # S11 change relative to the reference state (gain idx 0, phase state 4)
for g_idx in g_idxs:
    n0 = len(gain_err)
    g_prog = g_idx   # gain index actually programmed
    if ph_lut == 'switch' and g_idx > lut_switch:   # switch to the 2nd LUT
        orion_hal.set_freq('11G')
        g_prog = max(g_idx - int(round(lut2_backoff_db / 0.5)), 0)
    for p_idx in p_idxs:
        orion_hal.set_lut_idx(p_idx, g_prog, 0xF)
        orion_hal.stg2_load()
        time.sleep(d1)
        instruments.vna.write(":SENS:AVER:CLE")
        time.sleep(d2)

        gain = float(np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)[fi])
        phase = float(np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)[fi])
        s11 = float(np.array(instruments.vna.query(':CALC:MEAS3:DATA:FDATA?').strip().split(","), dtype=float)[fi])
        s11_ph = float(np.array(instruments.vna.query(':CALC:MEAS4:DATA:FDATA?').strip().split(","), dtype=float)[fi])
        if (g_idx, p_idx) == (g_idxs[0], 4):
            ref_gain, ref_phase = gain, phase   # reference: gain idx 0, phase state 4 after normalization
            ref_s11, ref_s11_ph = s11, s11_ph   # S11 is not normalized, so its reference is the first point
        g_err = gain - ref_gain + (g_idx - g_idxs[0])*0.5
        ph_err = wrap(phase - ref_phase - (p_idx-4)*step)
        s11_d = s11 - ref_s11
        s11_ph_d = wrap(s11_ph - ref_s11_ph)
        csv_out.writerow([g_idx, p_idx, gain, phase, g_err, ph_err, g_prog, s11, s11_ph, s11_d, s11_ph_d])
        csv_fh.flush()
        gain_err.append(g_err)
        phase_err.append(ph_err)
        s11_chg.append(s11_d)
        s11_ph_chg.append(s11_ph_d)
        print(f'g_idx = {g_idx:2d} (prog {g_prog:2d})  p_idx = {p_idx:3d}  ||  Gain = {gain:7.2f} dB  |  Phase = {phase:8.2f} deg  ||  Gain err = {g_err:+6.2f} dB  |  Phase err = {ph_err:+7.2f} deg  ||  S11 = {s11:7.2f} dB ({s11_d:+6.2f})  |  S11 phase = {s11_ph:8.2f} deg ({s11_ph_d:+7.2f})')

    if sweep != 'gain':   # in a gain sweep the errors are reported across the gain codes at the end
        this = ('this code: ' + f'phase {stats(phase_err[n0:])} deg, gain {stats(gain_err[n0:])} dB  |  ') if len(p_idxs) > 1 else ''
        print(f'g_idx = {g_idx:2d}  ||  {this}up to this code: phase {stats(phase_err)} deg, gain {stats(gain_err)} dB')
        print(f'g_idx = {g_idx:2d}  ||  S11 change: mag {stats(s11_chg[n0:])} dB, phase {stats(s11_ph_chg[n0:])} deg')

csv_fh.close()
gain_err, phase_err = np.array(gain_err), np.array(phase_err)
s11_chg, s11_ph_chg = np.array(s11_chg), np.array(s11_ph_chg)
print(f'\nPhase error: sd = {phase_err.std():.2f}{rms(phase_err)} deg')
print(f'Gain error:  sd = {gain_err.std():.2f}{rms(gain_err)} dB')
print(f'S11 mag change:   sd = {s11_chg.std():.2f}{rms(s11_chg)} dB, min {s11_chg.min():+.2f}, max {s11_chg.max():+.2f}')
print(f'S11 phase change: sd = {s11_ph_chg.std():.2f}{rms(s11_ph_chg)} deg, min {s11_ph_chg.min():+.2f}, max {s11_ph_chg.max():+.2f}')
print(f'Data saved to {csv_path}')

spi.close()

