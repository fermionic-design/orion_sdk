version = 'v2'
ant_sel = 0x4 # Antenna selection for RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8
chip_id = 'trial'
test_condition = 'vdd_2p7_temp_25C_nombias_0dbm_single_lut'

f = 9.5
f_min = 7
f_max = 13
f_step = 0.25

d1 = 0.1   # delay after setting IQ
d2 = 0.2   # delay after normalization

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
instruments.vna.cfg_pwr(pwr=-20)

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
instruments.vna.write(":SENS:AVER:COUN 64")

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

# Initialize xlsx for read
filename = f'C:/Users/silic/OneDrive/Documents/GitHub/orion/ate/ate_20260311/sweep_results/rx_phase_sweep__{version}__{chip_id}__ant_sel_{ant_sel}__{test_condition}.xlsx'
out_xls = xlsw.Workbook(filename)

#################################################################################################################
#################################################################################################################

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
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__freq_9p5__nombias__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__freq_9p5__nombias__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx')
    # orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx')
    orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_LUT_9.5_pm_1.2_norm_gain_-2_gm_0.4_nombias33_avg_new2.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_LUT_9.5_pm_1.2_norm_gain_-2_gm_0.4_nombias33_avg_new2.xlsx')
else:
    orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/raw_v1__rx0__gain_lut__11p5GHz__lowbias_vdd_2p7.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/v1_rx0_phase_lut_freq_11p5_gm_0p5_pm_1p5_pm2_5_abs_gain_10p5.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/raw_v1__rx0__gain_lut__11p5GHz__lowbias_vdd_2p7.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/v1_rx0_phase_lut_freq_11p5_gm_0p5_pm_1p5_pm2_5_abs_gain_10p5.xlsx')
                       
orion_csr.DEVICE_ID.read()
print('device_id = '+hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = '+hex(orion_csr.REVISION.major_rev))
print('minor_revision = '+hex(orion_csr.REVISION.minor_rev))

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('NOM')
orion_hal.set_tr_mask(rx_mask=0xF)
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
time.sleep(d2)

phase_err_all = [[] for _ in range(freq_pts)]
gain_err_all  = [[] for _ in range(freq_pts)]

# Frequency indices for f-0.5G, f, f+0.5G
offset_steps = int(0.5 / f_step)

freq_targets = {
    f"{f-0.5:.2f}GHz": pi - offset_steps,
    f"{f:.2f}GHz": pi,
    f"{f+0.5:.2f}GHz": pi + offset_steps
}

# Edge protection
freq_targets = {
    k: v for k, v in freq_targets.items()
    if 0 <= v < freq_pts
}

phase_err_store = {k: [] for k in freq_targets}
gain_err_store  = {k: [] for k in freq_targets}

xls_row=1
for g_idx in range(0, 1, 1):
    for p_idx in range (4,125,1):
        orion_hal.set_lut_idx(p_idx,g_idx,0xF)
        orion_hal.stg2_load()
        time.sleep(d1)
        instruments.vna.write(":SENS:AVER:CLE")
        time.sleep(d2)
        s21_gain_array = np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
        s21_phase_array = np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)

        if (p_idx==4):
            ref_s21_gain_array_9G=s21_gain_array
            ref_s21_phase_array_9G=s21_phase_array

        print('Setting Gain Code: ', orion_hal.gain_code[0])
        print('Setting I-Phase Code: ', orion_hal.i_code[p_idx])
        print('Setting Q-Phase Code: ', orion_hal.q_code[p_idx])
        print('Target Atten dB: ', orion_hal.target_gain_dB)
        print('Target Relative Phase: ', orion_hal.target_phase_deg)

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

        print(f'Phase Code: {p_idx}, Target Phase: {orion_hal.target_phase_deg:.2f}, Observed Phase: {s21_phase_array[pi]:.2f}, Observed Gain dB: {s21_gain_array[pi]:.2f}')

        # write gain phase data column wise
        for freq_idx in np.arange(0, freq_pts, 1):
            out_sheet.write(xls_row, freq_idx+6, s21_gain_array[freq_idx])
            out_sheet.write(xls_row, freq_idx+6+freq_pts+1, s21_phase_array[freq_idx])

            phase_error_deg=orion_hal.calc_phase_wrapped(orion_hal.calc_phase_wrapped(s21_phase_array[freq_idx]-ref_s21_phase_array_9G[freq_idx])-orion_hal.target_phase_deg)
            gain_error_dB=s21_gain_array[freq_idx]-ref_s21_gain_array_9G[freq_idx]-orion_hal.target_gain_dB
            
            # Store for DI (all frequencies)
            phase_err_all[freq_idx].append(phase_error_deg)
            gain_err_all[freq_idx].append(gain_error_dB)
            
            # Store for final summary (3 frequencies)
            for label, idx_target in freq_targets.items():
                if freq_idx == idx_target:
                    phase_err_store[label].append(phase_error_deg)
                    gain_err_store[label].append(gain_error_dB)
                    
            if (freq_idx==pi):
                print(f"{f} GHz Phase Error (deg): {phase_error_deg}")
                print(f"{f} GHz Gain Error in dB: {gain_error_dB}")

            out_sheet2.write(xls_row, freq_idx+6, phase_error_deg)
            out_sheet2.write(xls_row, freq_idx+6+freq_pts+1, gain_error_dB)
        xls_row+=1

summary_start_row = xls_row  # directly below sweep data

phase_col_offset = 6
gain_col_offset  = 6 + freq_pts + 1

# Write frequency header
freq_val = f_min
for idx in range(freq_pts):
    out_sheet2.write(summary_start_row, phase_col_offset + idx, freq_val)
    out_sheet2.write(summary_start_row, gain_col_offset + idx, freq_val)
    freq_val += f_step

metrics = ["std", "avg", "rms", "peak"]

for m_idx, metric in enumerate(metrics):

    row = summary_start_row + 1 + m_idx

    out_sheet2.write(row, 5, metric)
    out_sheet2.write(row, gain_col_offset - 1, metric)

    for freq_idx in range(freq_pts):

        phase_arr = np.array(phase_err_all[freq_idx])
        gain_arr  = np.array(gain_err_all[freq_idx])

        if metric == "std":
            phase_val = np.std(phase_arr)
            gain_val  = np.std(gain_arr)

        elif metric == "avg":
            phase_val = np.mean(phase_arr)
            gain_val  = np.mean(gain_arr)

        elif metric == "rms":
            phase_val = np.sqrt(np.mean(phase_arr)**2 + np.std(phase_arr)**2)
            gain_val  = np.sqrt(np.mean(gain_arr)**2  + np.std(gain_arr)**2)

        elif metric == "peak":
            phase_val = max(np.max(phase_arr), abs(np.min(phase_arr)))
            gain_val  = max(np.max(gain_arr),  abs(np.min(gain_arr)))

        out_sheet2.write(row, phase_col_offset + freq_idx, phase_val)
        out_sheet2.write(row, gain_col_offset + freq_idx, gain_val)

print("\n================ FINAL ERROR SUMMARY ================\n")

for label in freq_targets:

    phase_arr = np.array(phase_err_store[label])
    gain_arr  = np.array(gain_err_store[label])

    rms_phase = np.sqrt(np.mean(phase_arr**2))
    peak_phase = np.max(np.abs(phase_arr))

    rms_gain = np.sqrt(np.mean(gain_arr**2))
    peak_gain = np.max(np.abs(gain_arr))

    print(f"Frequency: {label}")
    if rms_phase > 2.975:
        print(f"  \033[1;31mRMS Phase Error FAILED: {rms_phase:.3f} deg\033[0m")
    else:
        print(f"  RMS Phase Error  : {rms_phase:.3f} deg")
    print(f"  Peak Phase Error : {peak_phase:.3f} deg")
    print(f"  RMS Gain Error   : {rms_gain:.3f} dB")
    print(f"  Peak Gain Error  : {peak_gain:.3f} dB")
    print("-----------------------------------------------------")

print("\n=====================================================\n")

instruments.vna.cfg_pwr(pwr=-40)
instruments.vna.write(":OUTP OFF")
out_xls.close()
print(f'\nData Dump File: {filename}')
elapsed = time.time() - start_time
print(f'Elapsed time: {elapsed:.1f} s')
spi.close()

