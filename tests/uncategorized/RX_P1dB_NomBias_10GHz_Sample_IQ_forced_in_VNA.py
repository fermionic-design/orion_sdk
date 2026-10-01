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
import pyvisa
#--------------------Test details---------------------------------
version = 'v2'
Chip_ID="AB41"
ant_sel= 0x1
supply_voltage="2.7"
temp = '25C'
# parameter="Low_Bias_02"
value=""
freq_list = np.arange(7, 13.25, 0.25)
iq_list = [{'I': 255, 'Q': 0}, {'I': 0, 'Q': 255}, {'I': 511, 'Q': 0}, {'I': 0, 'Q': 511}]
d1 = 0.1   # delay after setting IQ
d2 = 1   # delay after normalization
d3 = 0.5
pwr_start = -20
pwr_stop  = 6
num_pts   = 261
pwr_step  = (pwr_stop - pwr_start) / (num_pts - 1)

ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()


rm = pyvisa.ResourceManager()
my_supply = rm.open_resource('USB0::0x1AB1::0x0E11::DP8F251700261::INSTR')
print('SUPPLY: ',my_supply.query('*IDN?'))

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

def read_dc_power(power_supply):

    current = float(power_supply.query("MEAS:CURR?"))
    time.sleep(d3)
    voltage = float(power_supply.query("MEAS:VOLT?"))
    time.sleep(d3)

    power = voltage * current
    return current, power

def get_csv_file_handler(i_curr, q_curr, directory="."):
    filename = (
        f'../../results/bench_char/{Chip_ID}/ant_sel_{ant_sel}_RX_P1dB_Ic{i_curr}_Qc{q_curr}_{Chip_ID}_{supply_voltage}V_{temp}.csv')
    filepath = os.path.join(directory, filename)

    # Open file in append+read mode; creates it if it doesn't exist
    file = open(filepath, mode='a+', newline='')
    return file
# def get_csv_file_handler(directory="."):
#     filename = f'../../results/bench_char/{Chip_ID}/{channel}_p1dB_{parameter}_{Chip_ID}_{supply_voltage}V_25C.csv'
#     filepath = os.path.join(directory, filename)
#
#     # Open file in append+read mode; creates it if it doesn't exist
#     file = open(filepath, mode='a+', newline='')
#     return file

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

def iq_label(I, Q):
    return f"I{I}_Q{Q}"

loss_df = pd.read_csv('../../results/bench_char/total_path_loss_25C.csv')
loss_dict = dict(zip(loss_df['Freq_GHz'], loss_df['Loss_dB']))

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
# orion_hal.init_rx('LOW')
orion_hal.set_tr_mask(rx_mask=0xF)
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)

orion_hal.set_iq_val(I=255, Q=0, Av=2047, ant_sel=ant_sel)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.write(":SENS:AVER:CLE")
time.sleep(d2)

i_curr_list = range(4)
q_curr_list = range(4)

for i_curr in i_curr_list:
    for q_curr in q_curr_list:
        print(f"\n🔁 RX Bias: Icurr={i_curr}, Qcurr={q_curr}")

        orion_hal.set_rx_cmb_icurr(i_curr, 0xF)
        orion_hal.set_rx_cmb_qcurr(q_curr, 0xF)
        time.sleep(d1)

        handler = get_csv_file_handler(i_curr, q_curr)
        file_path = handler.name
        handler.close()
        append_column_data(file_path, "Freq_GHz", freq_list)
        dc_current, dc_power = read_dc_power(my_supply)
        append_column_data(
            file_path,
            "DC_Current_A",
            [dc_current] * len(freq_list)
        )

        append_column_data(
            file_path,
            "DC_Power_W",
            [dc_power] * len(freq_list)
        )
        for iq in iq_list:
            i_code = iq['I']
            q_code = iq['Q']
            print(f"▶ @ Ic={i_curr}, Qc={q_curr}, Av={2047}, I={i_code}, Q={q_code}")
            phase = iq_label(i_code, q_code)
            orion_hal.set_iq_val(I=i_code, Q=q_code, Av=2047, ant_sel=ant_sel)
            orion_hal.stg2_load()
            time.sleep(d1)

            p1dB_input = []
            p1dB_output = []
            s21_gain = []
            for freq in freq_list:
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

            append_column_data(file_path, f'in_P1dB_dBm ({phase})', p1dB_input)
            append_column_data(file_path, f'out_P1dB_dBm ({phase})', p1dB_output)
            append_column_data(file_path, f' S21_Gain_dB ({phase})', s21_gain)

instruments.vna.cfg_pwr(pwr=-40)
instruments.vna.write(":OUTP OFF")
elapsed = time.time() - start_time
print(f'Elapsed time: {elapsed:.1f} s')
spi.close()

