# -*- coding: utf-8 -*-
"""
Created on Thu May 22 14:36:54 2025

@author: silic
"""
import sys

sys.path.append('../../include')
from libs.fd_cmn.instruments.instruments import instruments
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import datetime
import pandas as pd
import numpy as np
import time
import os
import csv
#--------------------Test details---------------------------------
version = 'v2'
Chip_ID="AB39"
channel="RX3"
supply_voltage="2.5"
parameter="Low_Bias_02"
value=""
freq_list = np.arange(7, 13.25, 0.25)

d1 = 0.1   # delay after setting IQ
d2 = 1   # delay after normalization

pwr_start = -20
pwr_stop  = 6
num_pts   = 261
pwr_step  = (pwr_stop - pwr_start) / (num_pts - 1)

ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()

instruments = instruments(required_instruments=['vna'])
instruments.vna.init()
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg_pwr(pwr=-20)

instruments.vna.set_y_axis(win_id=1, ref_level=-30, scale_per_div=5)
instruments.vna.set_y_axis(win_id=2, ref_level=0, scale_per_div=45)

# Averaging
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 10")

instruments.vna.write(":SENS1:BAND 500")
instruments.vna.write(":SENS:SWE:TYPE POW")
instruments.vna.write(f":SOUR:POW:STAR {pwr_start}")
instruments.vna.write(f":SOUR:POW:STOP {pwr_stop}")
instruments.vna.write(f":SENS:SWE:POIN {num_pts}")
instruments.vna.write(":FORM:DATA ASC")
spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion,orion_lut,spi,version)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))
    
def get_csv_file_handler(directory="."):
    filename = f'../../results/bench_char/AB39/{channel}_p1dB_{parameter}_{Chip_ID}_{supply_voltage}V_25C.csv'
    filepath = os.path.join(directory, filename)

    # Open file in append+read mode; creates it if it doesn't exist
    file = open(filepath, mode='a+', newline='')
    return file

def append_column_data(filepath, column_name, data_list):
    # Step 1: Read existing data
    if os.path.exists(filepath):
        with open(filepath, 'r', newline='') as file:
            reader = csv.reader(file)
            all_rows = list(reader)

        # Get headers and existing rows
        if all_rows:
            headers = all_rows[0]
            rows = all_rows[1:]
        else:
            headers = []
            rows = []
    else:
        headers = []
        rows = []

    # Step 2: Add new column if not present
    if column_name not in headers:
        headers.append(column_name)
        for row in rows:
            row.append("")  # extend existing rows with empty value

    # Step 3: Append data to that column
    col_index = headers.index(column_name)
    max_existing_rows = len(rows)

    for i, val in enumerate(data_list):
        if i < max_existing_rows:
            if len(rows[i]) < len(headers):  # just in case
                rows[i] += [""] * (len(headers) - len(rows[i]))
            rows[i][col_index] = val
        else:
            # new row, fill missing columns with blanks except target
            new_row = [""] * len(headers)
            new_row[col_index] = val
            rows.append(new_row)

    # Step 4: Write everything back
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

loss_df = pd.read_csv('../../results/bench_char/total_path_loss_25C.csv')
loss_dict = dict(zip(loss_df['Freq_GHz'], loss_df['Loss_dB']))

if version == 'v2':
    # orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_00__vdd_2p5.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_20__lowbias_00__vdd_2p5.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_00__vdd_2p5.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_20__lowbias_00__vdd_2p5.xlsx')
    # orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__freq_9p5__nombias__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__freq_9p5__nombias__vdd_2p7.xlsx',
    #                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx')
    orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_vdd_2p5.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p5_pm2_3_abs_gain_12p5__lowbias__vdd_2p5.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx0__gain_lut__9p5GHz__lowbias_vdd_2p5.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p5_pm2_3_abs_gain_12p5__lowbias__vdd_2p5.xlsx')
else:
    orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                           r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('LOW')
orion_hal.set_tr_mask(rx_mask=0xF)
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)

orion_hal.set_lut_idx(4,0, 0xF)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.write(":SENS:AVER:CLE")
time.sleep(d2)

for phase_idx in range(4, 123, 30):
    orion_hal.set_lut_idx(phase_idx,0,0xF)
    orion_hal.stg2_load()
    time.sleep(d1)

    p1dB_input = []
    p1dB_output = []
    s21_gain = []
    for freq in freq_list:
        if (freq<=10.0):
            orion_hal.set_freq('9G')
        else:
            orion_hal.set_freq('11G')

        freq_GHz=freq*1e9
        instruments.vna.write(f":SENS:FREQ:CW {freq_GHz}")
        instruments.vna.write(":SENS:AVER:CLE")
        time.sleep(d2)

        # ---------- Read S21 ----------
        instruments.vna.write(":CALC:PAR:SEL 'CH1_S21_1'")
        gain_dB = np.array(
            instruments.vna.query(":CALC:DATA? FDATA").split(',')
        ).astype(float)
        print(gain_dB)
        loss_at_freq = loss_dict.get(freq, 0)  # default 0 if not found
        small_sig_gain = np.max(gain_dB[0:5])
        s21_gain.append(small_sig_gain - loss_at_freq)
        ind = 0
        for i in range(len(gain_dB)):
            if gain_dB[i] <= (small_sig_gain - 1.0):
                power_in = pwr_start + i * pwr_step
                actual_p1dB = power_in + loss_at_freq*0.5
                gain_at_p1dB = gain_dB[i]
                p1dB_input.append(actual_p1dB)

                p1dB_output.append(actual_p1dB + gain_at_p1dB - loss_at_freq)

                # Display
                instruments.vna.write(":CALC:MARK1:STAT ON")
                instruments.vna.write(f":CALC:MARK1:X {power_in}")

                ind = 1
                break

        if ind == 0:
            power_in = pwr_stop
            actual_p1dB = power_in + loss_at_freq * 0.5
            gain_at_p1dB = small_sig_gain
            p1dB_input.append(actual_p1dB)
            p1dB_output.append(actual_p1dB + gain_at_p1dB - loss_at_freq)
            
    if (phase_idx==4):
        phase="+I-phase"
    elif (phase_idx==34):
        phase="+Q-phase"
    elif (phase_idx==64):
        phase="-I-phase"
    else:
        phase="-Q-phase"
    handler = get_csv_file_handler()
    file_path = handler.name
    handler.close()
    append_column_data(file_path,"Freq_GHz",freq_list)
    append_column_data(file_path, f'in_P1dB_dBm ({phase})', p1dB_input)
    append_column_data(file_path, f'out_P1dB_dBm ({phase})', p1dB_output)
    append_column_data(file_path, f' S21_Gain_dB ({phase})', s21_gain)

instruments.vna.cfg_pwr(pwr=-40)
instruments.vna.write(":OUTP OFF")
elapsed = time.time() - start_time
print(f'Elapsed time: {elapsed:.1f} s')
spi.close()

