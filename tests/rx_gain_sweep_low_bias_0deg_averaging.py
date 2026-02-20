# -- coding: utf-8 --
"""
Created on Thu Apr 17 19:09:41 2025

@author: silic
"""
version = 'v2'
ant_sel = 0x8
chip_id = 'AC88'
test_condition = 'vdd_2p7_temp_25C_0deg_lowbias00_single_avg_lut'
mode = "single_lut" # single_lut, dual_lut

f = 9.5
f_min = 7
f_max = 13
f_step = 0.25

d1 = 0.1   # delay after setting IQ
d2 = 1   # delay after normalization

import sys
sys.path.append('../../include')

from libs.fd_cmn.instruments.instruments import instruments
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import pandas as pd
import numpy as np
import xlsxwriter as xlsw
import pyvisa
import math
import time
import datetime

gi = int((f-f_min)/f_step)   # gain index
pi = int((f-f_min)/f_step)   # phase index
freq_pts = int((f_max-f_min)/f_step)+1
ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()
#---------------------------SETUP VNA------------------------

instruments = instruments(required_instruments=['vna'])

instruments.vna.init()
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg_freq(start=7e9, stop=13e9, step=250e6)
instruments.vna.cfg_pwr(pwr=-30)

instruments.vna.add_marker(win_id=1, marker_id=1, val=8e9)
instruments.vna.add_marker(win_id=1, marker_id=2, val=10e9)
instruments.vna.add_marker(win_id=1, marker_id=3, val=12e9)

instruments.vna.add_marker(win_id=2, marker_id=1, val=8e9)
instruments.vna.add_marker(win_id=2, marker_id=2, val=10e9)
instruments.vna.add_marker(win_id=2, marker_id=3, val=12e9)

instruments.vna.set_y_axis(win_id=1, ref_level=-30, scale_per_div=5)
instruments.vna.set_y_axis(win_id=2, ref_level=0, scale_per_div=45)

# Averaging
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")


spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

# Initialize xlsx for read
filename = f'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/bench_char/socket/{chip_id}/rx_gain_sweep__{version}__{chip_id}__ant_sel_{ant_sel}__{test_condition}.xlsx'
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
for i in range(0,25,1):
    out_sheet2.write(0,i+6,'Phase Error Deg '+str(freq)+'GHz')
    out_sheet2.write(0,i+32,'Gain Error dB '+str(freq)+'GHz')
    freq+=0.25
    
if version == 'v2':
    # orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_vdd_2p5.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p5_pm2_3_abs_gain_12p5__lowbias__vdd_2p5.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_vdd_2p5.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p5_pm2_3_abs_gain_12p5__lowbias__vdd_2p5.xlsx')
    orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_00___vdd_2p7_with_avg.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_15__lowbias_00__vdd_2p5.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_00___vdd_2p7_with_avg.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_15__lowbias_00__vdd_2p5.xlsx')
else:
    orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

                       
orion_csr.DEVICE_ID.read()
print('device_id = '+hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = '+hex(orion_csr.REVISION.major_rev))
print('minor_revision = '+hex(orion_csr.REVISION.minor_rev))

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('LOW')
orion_hal.set_tr_mask(rx_mask=0xF)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)

orion_hal.set_lut_idx(4,0,0xF)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.write(":SENS:AVER:CLE")
time.sleep(d2)
instruments.vna.norm(win_id=2)
time.sleep(d2)

xls_row=1
for g_idx in range (0,64,1):
    if mode == "dual_lut":
        if g_idx <=31:
            band = '9G'
            orion_hal.set_freq('9G')
            orion_hal.init_rx('LOW')
        else:
            band = "11G"
            orion_hal.set_freq('11G')
            orion_hal.init_rx('LOW')
    else:
        band = '9G'
        orion_hal.set_freq('9G')
        orion_hal.init_rx('LOW')

    orion_hal.set_lut_idx(4,g_idx,0xF)
    orion_hal.stg2_load()
    time.sleep(d1)

    instruments.vna.write(":SENS:AVER:CLE")
    time.sleep(d2)                  # Wait for averaging to complete

    s21_gain_array = np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
    s21_phase_array = np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)
    
    if (g_idx==0):
        ref_s21_gain_array_9G=s21_gain_array
        ref_s21_phase_array_9G=s21_phase_array
    
    ################################################################################################################# 
    ################################################################################################################# 
    i_lsb  = orion_csr.RX0_I_LSB_TEMP0.read()
    q_lsb  = orion_csr.RX0_Q_LSB_TEMP0.read()
    av_lsb = orion_csr.RX0_AV_LSB_TEMP0.read()
    msb    = orion_csr.RX0_MSB_TEMP0.read()

    phase_val_i = ((msb & 0x1) << 8) | (i_lsb & 0xFF)
    phase_val_q = ((msb & 0x2) << 7) | (q_lsb & 0xFF)
    gain_val    = ((msb & 0x1C) << 6) | (av_lsb & 0xFF)

    
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

    print(f'Gain Code: {g_idx}, Target Gain: {(ref_s21_gain_array_9G[pi] + orion_hal.target_gain_dB):.2f}, Observed Gain: {s21_gain_array[pi]:.2f}, Observed Phase: {s21_phase_array[pi]:.2f}')

    # write gain phase data column wise
    phase_error_list = []
    gain_error_list = []
    for freq_idx in np.arange(0, freq_pts, 1):
        out_sheet.write(xls_row, freq_idx+6, s21_gain_array[freq_idx])
        out_sheet.write(xls_row, freq_idx+6+freq_pts+1, s21_phase_array[freq_idx])
        phase_error_deg = orion_hal.calc_phase_wrapped(orion_hal.calc_phase_wrapped(s21_phase_array[freq_idx]-ref_s21_phase_array_9G[freq_idx])-0)
        gain_error_dB = s21_gain_array[freq_idx]-ref_s21_gain_array_9G[freq_idx]-orion_hal.target_gain_dB

        out_sheet2.write(xls_row, freq_idx+6, phase_error_deg)
        out_sheet2.write(xls_row, freq_idx+6+freq_pts+1, gain_error_dB)
    xls_row+=1

instruments.vna.cfg_pwr(pwr=-60)
instruments.vna.write(":OUTP OFF")
out_xls.close()
print(f'\nData Dump File: {filename}')
elapsed = time.time() - start_time
print(f'Elapsed time: {elapsed:.1f} s')
spi.close()


# my_vna.write(":CALC:AVER:STAT ON")
# my_vna.write(":CALC:AVER:COUN 16")
# my_vna.write(":CALC:AVER:CLE")

# s21_gain_array=my_vna.query_ascii_values(':CALC:MEAS1:DATA:FDATA?')
# s21_phase_array=my_vna.query_ascii_values(':CALC:MEAS2:DATA:FDATA?')