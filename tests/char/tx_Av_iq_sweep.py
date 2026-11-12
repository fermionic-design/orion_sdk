# -- coding: utf-8 --
"""
TX counterpart of rx_Av_iq_sweep_s11 (without the S11 measurement): sweep the TX LUT gain code (g_idx) and/or phase code (p_idx) with orion_hal.set_lut_idx
and log S12 gain/phase over frequency.
"""
chip_name = 'chip_58'   # DUT label, prefixed to the file name
version = 'v2'
vdd = '2p7'     # supply voltage, label for the file name only
temp = '25C'    # temperature, label for the file name only
bias_mode = 'preset'     # 'preset': orion_hal.init_tx(bias), 'curr': orion_hal.set_tx_bias(i_curr, q_curr, drv_curr, lna_curr) only (no init_tx)
bias = 'MAX'    # preset mode: TX bias 'MAX', 'NOM', 'LOW', '2W_FEM' or '5W_FEM'
i_curr = 3      # curr mode: TX combiner I tail current, 2-bit (0...3)
q_curr = 3      # curr mode: TX combiner Q tail current, 2-bit (0...3)
drv_curr = 31   # curr mode: TX driver (final_av) current, 5-bit (0...31)
lna_curr = 3    # curr mode: common TX LNA current, 2-bit (0...3)
ant_sel = 0x1 # TX0: 0x1, TX1: 0x2, TX2: 0x4, TX3: 0x8
ant_sel_all = True   # True: hardware calls always get 0xF and ant_sel is only used for the file name; False: ant_sel is applied to the hardware

f_min, f_max, f_step = 7, 13, 0.25
f_mark = 11.5   # GHz: marker and printed values
Pin = 10     # VNA source power in dBm, also in the file name
show_rms = 1   # 1: print rms along with sd in the error stats, 0: sd only
sweep = 'phase'   # 'phase' (p_idx 4...124), 'gain' (g_idx 0...63) or 'both' (gain outer loop, phase inner loop)
g_start, g_stop, g_step = 0, 63, 1   # gain code range (inclusive) and step, used when sweep is 'gain' or 'both'
g_fixed = 0   # gain code held while sweep is 'phase'

tx_gain_lut = r'C:\Users\silic\Github\orion_sdk\scripts\logs\chip_55__4ch__v2__tx_gain_lut__freq_9p5__algo_joint_max__iq_[172,-180]__bias_max__pin_10__vdd_2p7__temp_25C.xlsx'
# tx_phase_lut = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__tx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_max__pin_10__vdd_2p7__temp_25C__chip_55_tx0.xlsx'
tx_phase_lut = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__tx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_max__pin_10__vdd_2p7__temp_25C__chip55__ant_0123.xlsx'
rx_gain_lut = r'../../final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx'    # RX LUTs are only loaded because init_lut_new needs them
rx_phase_lut = r'../../final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx'

d1 = 0.1
d2 = 0.2   # delay after clearing averaging
d_settle = 1.0   # s: before each phase code loop the first phase code is set and held this long, without a measurement
d_first = 3      # extra delay before the very first point, the VNA trace is not valid until its first sweep finishes

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
import openpyxl

instruments = instruments(required_instruments=['vna'])
instruments.vna.init()
instruments.vna.cfg(1, 'S12_GAIN')
instruments.vna.cfg(2, 'S12_PHASE')
instruments.vna.cfg_freq(start=f_min*1e9, stop=f_max*1e9, step=f_step*1e9)
instruments.vna.cfg_pwr(pwr=Pin)
for w in (1, 2):
    instruments.vna.add_marker(win_id=w, marker_id=1, val=f_mark*1e9)
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

spi.cfg_logging(log_en=0)
orion_hal.init_lut_new(tx_gain_lut, tx_phase_lut, rx_gain_lut, rx_phase_lut, rx_gain_lut, rx_phase_lut)
spi.cfg_logging(log_en=0)
hw_ant_sel = 0xF if ant_sel_all else ant_sel   # value passed to every hardware call
ant_tag = f'all_{ant_sel}' if ant_sel_all else f'{ant_sel}'   # file name: all_4 = all TX on, ant_sel only labels the DUT channel
# spi.dump_regs(start_addr=0, end_addr=255, path='./logs/reg_dump_before_configuring_p_id_4.csv')
orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
if bias_mode == 'preset':
    orion_hal.init_tx(bias, ant_sel=hw_ant_sel)
    bias_tag = bias
else:
    orion_hal.set_tx_bias(i_curr, q_curr, drv_curr, lna_curr, hw_ant_sel)
    bias_tag = f'i{i_curr}_q{q_curr}_d{drv_curr}_l{lna_curr}'
orion_hal.set_tr_mask(tx_mask=hw_ant_sel)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

orion_hal.set_lut_idx(4, 0, hw_ant_sel)
orion_hal.stg2_load()
# spi.dump_regs(start_addr=0, end_addr=255, path='./logs/reg_dump_after_configuring_p_id_4.csv')
time.sleep(d1 + d_first)
instruments.vna.write(":SENS:AVER:CLE")
time.sleep(d2)
instruments.vna.norm(win_id=2)

fi = int(round((f_mark-f_min)/f_step))
freqs = f_min + f_step*np.arange(int(round((f_max-f_min)/f_step)) + 1)   # GHz, one entry per VNA point
trace = lambda m: np.array(instruments.vna.query(f':CALC:MEAS{m}:DATA:FDATA?').strip().split(","), dtype=float)
step = 360/121   # deg per LUT state
wrap = lambda d: (d + 180) % 360 - 180

# I/Q codes of each phase state, from the TX phase LUT (LUT row = p_idx); bit 8 = sign, negative v is stored as 256 - v
iq_dec = lambda c: 256 - c if c >= 256 else c
lut_rows = list(openpyxl.load_workbook(tx_phase_lut)['Sheet1'].iter_rows(min_row=2, values_only=True))
iq_of = lambda p: (iq_dec(int(lut_rows[p][0])), iq_dec(int(lut_rows[p][1])))

p_idxs = range(4, 125) if sweep in ('phase', 'both') else [4]
g_idxs = range(g_start, g_stop + 1, g_step) if sweep in ('gain', 'both') else [g_fixed if sweep == 'phase' else 0]

tag = lambda x: f'{x:g}'.replace('.', 'p')
g_tag = f'{g_idxs[0]}' if len(g_idxs) == 1 else f'{g_idxs[0]},{g_step},{g_idxs[-1]}'
p_tag = f'{p_idxs[0]}' if len(p_idxs) == 1 else f'{p_idxs[0]},1,{p_idxs[-1]}'
os.makedirs('./logs', exist_ok=True)
csv_path = f'./logs/{chip_name}__tx_Av_iq_sweep__{version}__ant_sel_{ant_tag}__vdd_{vdd}__temp_{temp}__bias_{bias_tag}__pin_{Pin}__sweep_{sweep}__g_[{g_tag}]__p_[{p_tag}]__freq_[{tag(f_min)},{tag(f_step)},{tag(f_max)}]__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.csv'
csv_fh = open(csv_path, 'w', newline='')
csv_out = csv.writer(csv_fh)
csv_out.writerow(['Freq GHz', 'g_idx', 'p_idx', 'I', 'Q', 'Gain dB', 'Phase deg', 'Gain err dB', 'Phase err deg'])

rms = lambda e: f', rms = {np.sqrt(np.mean(np.square(e))):.2f}' if show_rms else ''
stats = lambda e: f'sd = {np.std(e):.2f}{rms(e)}'
gain_err, phase_err = [], []
for g_idx in g_idxs:
    n0 = len(gain_err)
    orion_hal.set_lut_idx(p_idxs[0], g_idx, hw_ant_sel)   # settle on the first phase code, no measurement
    orion_hal.stg2_load()
    time.sleep(d_settle)
    for p_idx in p_idxs:
        orion_hal.set_lut_idx(p_idx, g_idx, hw_ant_sel)
        orion_hal.stg2_load()
        time.sleep(d1)
        instruments.vna.write(":SENS:AVER:CLE")
        time.sleep(d2)

        gain_t, phase_t = (trace(m) for m in (1, 2))   # full traces, f_min...f_max
        if len(gain_t) != len(freqs):
            raise RuntimeError(f'VNA returned {len(gain_t)} points, expected {len(freqs)} ({f_min}...{f_max} GHz, step {f_step})')
        if (g_idx, p_idx) == (g_idxs[0], 4):
            ref_gain_t, ref_phase_t = gain_t, phase_t   # reference: first gain idx, phase state 4 after normalization, per frequency
        if p_idx == 4 and sweep != 'gain':
            ref_phase_t = phase_t   # phase error is relative to phase code 0 (p_idx 4) of the same gain code
        g_err_t = gain_t - ref_gain_t + (g_idx - g_idxs[0])*0.5
        ph_err_t = wrap(phase_t - ref_phase_t - (p_idx-4)*step)
        i_val, q_val = iq_of(p_idx)
        csv_out.writerows([f'{freqs[k]:g}', g_idx, p_idx, i_val, q_val, gain_t[k], phase_t[k], g_err_t[k], ph_err_t[k]] for k in range(len(freqs)))
        csv_fh.flush()
        # console and the error stats are for the marker frequency f_mark
        gain, phase = gain_t[fi], phase_t[fi]
        g_err, ph_err = g_err_t[fi], ph_err_t[fi]
        gain_err.append(g_err)
        phase_err.append(ph_err)
        print(f'g_idx = {g_idx:2d}  p_idx = {p_idx:3d}  (I = {i_val:4d}, Q = {q_val:4d})  ||  Gain = {gain:7.2f} dB  |  Phase = {phase:8.2f} deg  ||  Gain err = {g_err:+6.2f} dB  |  Phase err = {ph_err:+7.2f} deg')

    if sweep != 'gain':   # in a gain sweep the errors are reported across the gain codes at the end
        this = ('this code: ' + f'phase {stats(phase_err[n0:])} deg, gain {stats(gain_err[n0:])} dB  |  ') if len(p_idxs) > 1 else ''
        print(f'g_idx = {g_idx:2d}  ||  {this}up to this code: phase {stats(phase_err)} deg, gain {stats(gain_err)} dB')

csv_fh.close()
gain_err, phase_err = np.array(gain_err), np.array(phase_err)
print(f'\nPhase error: sd = {phase_err.std():.2f}{rms(phase_err)} deg')
print(f'Gain error:  sd = {gain_err.std():.2f}{rms(gain_err)} dB')
print(f'Data saved to {csv_path}')

instruments.vna.write(":OUTP OFF")
orion_hal.en_data_path(0)   # turn off the BFM so it does not heat up
spi.close()
