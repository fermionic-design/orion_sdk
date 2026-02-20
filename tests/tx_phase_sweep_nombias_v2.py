version = 'v2'
ant_sel = 0x2
chip_id = 'AC58'
test_condition = 'vdd_2p7_temp_25C_nombias'

f = 9.5
f_min = 7
f_max = 13
f_step = 0.25

d1 = 0.1   # delay after setting IQ
d2 = 1   # delay after normalization

import sys
sys.path.append('../../include')

from libs.fd_cmn.instruments.instruments import instruments
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import pandas as pd
import numpy as np
import xlsxwriter as xlsw
import datetime
import pyvisa
import math
import time

# Derived Parameters
gi = int((f-f_min)/f_step)   # gain index
pi = int((f-f_min)/f_step)   # phase index
freq_pts = int((f_max-f_min)/f_step)+1
ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()

# VNA Setup
instruments = instruments(required_instruments=['vna'])
instruments.vna.init()
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg_freq(start=7e9, stop=13e9, step=250e6)
instruments.vna.cfg_pwr(pwr=10)

instruments.vna.add_marker(win_id=1, marker_id=1, val=8e9)
instruments.vna.add_marker(win_id=1, marker_id=2, val=10e9)
instruments.vna.add_marker(win_id=1, marker_id=3, val=12e9)

instruments.vna.add_marker(win_id=2, marker_id=1, val=8e9)
instruments.vna.add_marker(win_id=2, marker_id=2, val=10e9)
instruments.vna.add_marker(win_id=2, marker_id=3, val=12e9)

instruments.vna.set_y_axis(win_id=1, ref_level=0, scale_per_div=5)
instruments.vna.set_y_axis(win_id=2, ref_level=0, scale_per_div=45)

# Averaging
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

# Orion Setup
spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                       r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__tx_phase_lut__freq_8p5__gm_0p5__pm_1p5__pm2_3__abs_gain_7p5__nom__vdd_2p7.xlsx',
                       # r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__tx_phase_lut__freq_9p5__gm_0p5__pm_1p5__pm2_3__abs_gain_6p5__low__vdd_2p5.xlsx',
                       r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/v2__rx_gain_lut__nom_bias__9p5GHz.xlsx',
                       r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/v2__phase_lut_freq_9p5_gm_1_pm_1p4.xlsx',
                       r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/v2__rx_gain_lut__nom_bias__9p5GHz.xlsx',
                       r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/v2__phase_lut_freq_9p5_gm_1_pm_1p4.xlsx')

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
orion_hal.init_tx('MAX')
orion_hal.set_tr_mask(tx_mask=ant_sel)
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

# Normalize
orion_hal.set_lut_idx(4,0,ant_sel)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.write(":SENS:AVER:CLE")          # Clear averaging
instruments.vna.query("*OPC?")
instruments.vna.norm(win_id=2)
time.sleep(d2)

# Initialize xlsx for read
filename = f'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/bench_char/dummy/tx_char__{version}__{chip_id}__ant_sel_{ant_sel}__{test_condition}__{ts}.xlsx'
out_xls = xlsw.Workbook(filename)

out_sheet = out_xls.add_worksheet()
out_sheet.write(0,0,'Gain-Code')
out_sheet.write(0,1,'I-Code')
out_sheet.write(0,2,'Q-Code')
out_sheet.write(0,3,'Target Atten')
out_sheet.write(0,4,'Target Phase')

freq=7
for i in range(0,freq_pts,1):
    out_sheet.write(0,i+6,'S21 Gain dB '+str(freq)+'GHz')
    out_sheet.write(0,i+6+freq_pts+1,'S21 Phase Deg '+str(freq)+'GHz')
    freq+=0.25

out_sheet2 = out_xls.add_worksheet()
out_sheet2.write(0,0,'Gain-Code')
out_sheet2.write(0,1,'I-Code')
out_sheet2.write(0,2,'Q-Code')
out_sheet2.write(0,3,'Target Atten')
out_sheet2.write(0,4,'Target Phase')

freq=7
for i in range(0,freq_pts,1):
    out_sheet2.write(0,i+6,'Phase Error Deg '+str(freq)+'GHz')
    out_sheet2.write(0,i+6+freq_pts+1,'Gain Error dB '+str(freq)+'GHz')
    freq+=0.25


xls_row=1
for p_idx in range (4,125,1):
    orion_hal.set_lut_idx(p_idx,0,ant_sel)
    orion_hal.stg2_load()
    time.sleep(d1)
    instruments.vna.write(":SENS:AVER:CLE")
    time.sleep(d1)
    instruments.vna.query("*OPC?")
    s21_gain_array=np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
    s21_phase_array=np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)

    if (p_idx==4):
        ref_s21_gain_array_10G=s21_gain_array
        ref_s21_phase_array_10G=s21_phase_array

    out_sheet.write(xls_row, 0, orion_hal.gain_val)
    out_sheet.write(xls_row, 1, orion_hal.phase_val_i)
    out_sheet.write(xls_row, 2, orion_hal.phase_val_q)
    out_sheet.write(xls_row, 3, orion_hal.target_gain_dB)
    out_sheet.write(xls_row, 4, orion_hal.target_phase_deg)

    out_sheet2.write(xls_row, 0, orion_hal.gain_val)
    out_sheet2.write(xls_row, 1, orion_hal.phase_val_i)
    out_sheet2.write(xls_row, 2, orion_hal.phase_val_q)
    out_sheet2.write(xls_row, 3, orion_hal.target_gain_dB)
    out_sheet2.write(xls_row, 4, orion_hal.target_phase_deg)

    # print 10GHz value
    print(f'Phase Code: {p_idx}, Target Phase: {orion_hal.target_phase_deg:.2f}, Observed Phase: {float(s21_phase_array[pi]):.2f}, Observed Gain dB: {float(s21_gain_array[pi]):.2f}')

    # write gain phase data column wise
    for freq_idx in np.arange(0, freq_pts, 1):
        out_sheet.write(xls_row, freq_idx+6, s21_gain_array[freq_idx])
        out_sheet.write(xls_row, freq_idx+6+freq_pts+1, s21_phase_array[freq_idx])

        phase_error_deg=orion_hal.calc_phase_wrapped(orion_hal.calc_phase_wrapped(s21_phase_array[freq_idx]-ref_s21_phase_array_10G[freq_idx])-orion_hal.target_phase_deg)
        gain_error_dB=s21_gain_array[freq_idx]-ref_s21_gain_array_10G[freq_idx]-orion_hal.target_gain_dB

        if (freq_idx==pi):
            print('10GHz Phase Error in Deg: ', phase_error_deg)
            print('10GHz Gain Error in dB: ', gain_error_dB)

        out_sheet2.write(xls_row, freq_idx+6, phase_error_deg)
        out_sheet2.write(xls_row, freq_idx+6+freq_pts+1, gain_error_dB)
    xls_row+=1

instruments.vna.cfg_pwr(pwr=-40)
instruments.vna.write(":OUTP OFF")
out_xls.close()
print(f'\nData Dump File: {filename}')
elapsed = time.time() - start_time
print(f'Elapsed time: {elapsed:.1f} s')
spi.close()

