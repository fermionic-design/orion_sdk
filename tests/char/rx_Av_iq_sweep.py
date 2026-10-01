# -- coding: utf-8 --
version = 'v2'
bias = 'NOM'    # RX bias: 'NOM' or 'LOW'
ant_sel = 0x8   # RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8

f_min, f_max, f_step = 7, 13, 0.25
f_mark = 9.5   # GHz: marker and printed values
sweep = 'both'   # 'phase' (p_idx 4...124), 'gain' (g_idx 0...63) or 'both' (gain outer loop, phase inner loop)
g_start, g_stop, g_step = 0, 63, 20   # gain code range (inclusive) and step, used when sweep is 'gain' or 'both'

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
instruments.vna.init()
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg_freq(start=f_min*1e9, stop=f_max*1e9, step=f_step*1e9)
instruments.vna.cfg_pwr(pwr=8)
instruments.vna.add_marker(win_id=1, marker_id=1, val=f_mark*1e9)
instruments.vna.add_marker(win_id=2, marker_id=1, val=f_mark*1e9)
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

orion_hal.init_lut_new(r'C:/Users/silic/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_gain_lut__freq_9p5__algo_joint_max__iq_[264,464]__bias_nom__vdd_3p3__temp_25C.xlsx',
                           r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_phase_lut__freq_9p5__gm_1__backoff_5__algo_joint_max__av_2047__bias_nom__vdd_3p3__temp_25C.xlsx',
                           r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_gain_lut__freq_9p5__algo_joint_max__iq_[264,464]__bias_nom__vdd_3p3__temp_25C.xlsx',
                           r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_phase_lut__freq_9p5__gm_1__backoff_5__algo_joint_max__av_2047__bias_nom__vdd_3p3__temp_25C.xlsx')

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx(bias)
orion_hal.set_tr_mask(rx_mask=ant_sel)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)

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
csv_path = f'./logs/rx_Av_iq_sweep__{version}__ant_sel_{ant_sel}__bias_{bias}__sweep_{sweep}__g_[{g_tag}]__p_[{p_tag}]__freq_{tag(f_mark)}__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.csv'
csv_fh = open(csv_path, 'w', newline='')
csv_out = csv.writer(csv_fh)
csv_out.writerow(['g_idx', 'p_idx', 'Gain dB', 'Phase deg', 'Gain err dB', 'Phase err deg'])

stats = lambda e: f'sd = {np.std(e):.2f}, rms = {np.sqrt(np.mean(np.square(e))):.2f}'
gain_err, phase_err = [], []
for g_idx in g_idxs:
    n0 = len(gain_err)
    for p_idx in p_idxs:
        orion_hal.set_lut_idx(p_idx, g_idx, 0xF)
        orion_hal.stg2_load()
        time.sleep(d1)
        instruments.vna.write(":SENS:AVER:CLE")
        time.sleep(d2)

        gain = float(np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)[fi])
        phase = float(np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)[fi])
        if (g_idx, p_idx) == (g_idxs[0], 4):
            ref_gain, ref_phase = gain, phase   # reference: gain idx 0, phase state 4 after normalization
        g_err = gain - ref_gain + (g_idx - g_idxs[0])*0.5
        ph_err = wrap(phase - ref_phase - (p_idx-4)*step)
        csv_out.writerow([g_idx, p_idx, gain, phase, g_err, ph_err])
        csv_fh.flush()
        gain_err.append(g_err)
        phase_err.append(ph_err)
        print(f'g_idx = {g_idx:2d}  p_idx = {p_idx:3d}  ||  Gain = {gain:7.2f} dB  |  Phase = {phase:8.2f} deg  ||  Gain err = {g_err:+6.2f} dB  |  Phase err = {ph_err:+7.2f} deg')

    if sweep != 'gain':   # in a gain sweep the errors are reported across the gain codes at the end
        this = ('this code: ' + f'phase {stats(phase_err[n0:])} deg, gain {stats(gain_err[n0:])} dB  |  ') if len(p_idxs) > 1 else ''
        print(f'g_idx = {g_idx:2d}  ||  {this}up to this code: phase {stats(phase_err)} deg, gain {stats(gain_err)} dB')

csv_fh.close()
gain_err, phase_err = np.array(gain_err), np.array(phase_err)
print(f'\nPhase error: sd = {phase_err.std():.2f} deg, rms = {np.sqrt(np.mean(phase_err**2)):.2f} deg')
print(f'Gain error:  sd = {gain_err.std():.2f} dB,  rms = {np.sqrt(np.mean(gain_err**2)):.2f} dB')
print(f'Data saved to {csv_path}')

spi.close()

