# Description: Characterization of TX IQ mismatch using a VNA.
version = 'v2'
chip_id = 'AD06'
ant_sel = 0x2
# test_condition = 'with_ball'
# Tx0=0x1, Tx1=0x2, Tx2=0x4, Tx3=0x8

log_path = 'logs_20260220'

Av_list = [2047]#, 1023, 511, 255]

I_max = 255
I_min = 0
I_step = -8
I_min_step_threshold = 33

Q_max = 255
Q_min = 0
Q_step = -8
Q_min_step_threshold = 33

f = 10
f_min = 7
f_max = 13
f_step = 0.25

d1 = 0.1    # delay after bfm programming
d2 = 1  # delay after normalization
d3 = 0.6
# Libraries
import sys
sys.path.append('../include')
import time
from libs.fd_cmn.instruments.instruments import instruments
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import matplotlib.pyplot as plt
import numpy as np
import datetime
import xlsxwriter

# Derived Parameters
gi = int((f-f_min)/f_step)   # gain index
pi = int((f-f_min)/f_step)   # phase index
ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()
fname = f'{log_path}/tx_char__{version}__{chip_id}__ant_sel_{ant_sel}__{ts}.xlsx'

# XLS Setup
workbook = xlsxwriter.Workbook(fname)
worksheet = workbook.add_worksheet('iq_sweep')
header = ['Av', 'I', 'Q']
for freq in np.arange(f_min, f_max+f_step, f_step):
    header.append(f'S21 Gain ({freq})')
for freq in np.arange(f_min, f_max + f_step, f_step):
    header.append(f'S21 Phase ({freq})')
worksheet.write_row(0, 0, header)
row = 1

def range_inclusive(x, y, step, min_step_value=None):
    """
    Returns a list from x to y (inclusive) with a given step. If min_step_value is set,
    the step becomes 1 when the loop variable drops below min_step_value.
    """
    result = []
    current = x
    while (step > 0 and current <= y) or (step < 0 and current >= y):
        result.append(current)
        if min_step_value is not None and current < min_step_value:
            current += 1 if step > 0 else -1
        else:
            current += step
    if (step > 0 and result[-1] != y and current > y) or (step < 0 and result[-1] != y and current < y):
        result.append(y)
    return result

# VNA Setup
instruments = instruments(required_instruments=['vna'])

instruments.vna.init()
instruments.vna.cfg(1, 'S12_GAIN')
instruments.vna.cfg(2, 'S12_PHASE')
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
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi)

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
orion_hal.init_tx('MAX')
orion_hal.set_tr_mask(tx_mask=ant_sel)
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

# Normalize
orion_hal.set_iq_val(I=255, Q=0, Av=2047, ant_sel=ant_sel)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.norm(win_id=2)
time.sleep(d2)

# Sweep I for each Av
all_gain_list = []
all_phase_list = []
for idx, Av in enumerate(Av_list):
    gain_list = []
    phase_list = []
    I_list = []
    flag = 0
    for i in range_inclusive(I_max, I_min, I_step, I_min_step_threshold):
        if flag==0:
            instruments.vna.write(":SENS:AVER:STAT OFF")
        orion_hal.set_iq_val(I=i, Q=Q_min, Av=Av, ant_sel=ant_sel)
        orion_hal.stg2_load()
        time.sleep(d1)
        if flag==0:
            instruments.vna.write(":SENS:AVER:STAT ON")
            time.sleep(d3)
            flag = 1
        # instruments.vna.write(":SENS:AVER:CLE")
        # instruments.vna.query("*OPC?")
        s21_gain_arr = instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(",")
        s21_phase_arr = instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(",")
        gain_val = float(s21_gain_arr[gi])
        phase_val = float(s21_phase_arr[pi])
        gain_list.append(gain_val)
        phase_list.append(phase_val)
        I_list.append(i)
        print(f'IQ=({i},{Q_min}), Av={Av} > Gain={gain_val:.2f}, Phase={phase_val:.2f}')
        worksheet.write_row(row, 0, [Av, i, Q_min] + list(map(float,s21_gain_arr)) + list(map(float,s21_phase_arr)))
        row+=1
    all_gain_list.append((I_list, gain_list, idx))
    all_phase_list.append((I_list, phase_list, idx))

# Sweep Q for each Av
all_q_gain_list = []
all_q_phase_list = []
for idx, Av in enumerate(Av_list):
    q_gain_list = []
    q_phase_list = []
    Q_list = []
    flag = 0
    for q in range_inclusive(Q_max, Q_min, Q_step, Q_min_step_threshold):
        if flag==0:
            instruments.vna.write(":SENS:AVER:STAT OFF")
        orion_hal.set_iq_val(I=I_min, Q=q, Av=Av, ant_sel=ant_sel)
        orion_hal.stg2_load()
        time.sleep(d1)
        if flag==0:
            instruments.vna.write(":SENS:AVER:STAT ON")
            # instruments.vna.write(":SENS:AVER:CLE")
            # instruments.vna.query("*OPC?")
            time.sleep(d3)
            flag=1
        s21_gain_arr = instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(",")
        s21_phase_arr = instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(",")
        gain_val = float(s21_gain_arr[gi])
        phase_val = float(s21_phase_arr[pi])
        q_gain_list.append(gain_val)
        q_phase_list.append(phase_val)
        Q_list.append(q)
        print(f'IQ=({I_min},{q}), Av={Av} > Gain={gain_val:.2f}, Phase={phase_val:.2f}')
        worksheet.write_row(row, 0, [Av, I_min, q] + list(map(float,s21_gain_arr)) + list(map(float,s21_phase_arr)))
        row += 1
    all_q_gain_list.append((Q_list, q_gain_list, idx))
    all_q_phase_list.append((Q_list, q_phase_list, idx))

# Plot all results in a single figure with 4 subplots at the end
fig, axs = plt.subplots(2, 2, figsize=(12, 12), sharex=False)
colors = plt.cm.viridis(np.linspace(0, 1, len(Av_list)))
for I_list, gain_list, idx in all_gain_list:
    axs[0, 0].plot(I_list, gain_list, marker='o', color=colors[idx], label=f'Av={Av_list[idx]}')
axs[0, 0].set_ylabel(f'S21 Gain @ {f} GHz (dB)')
axs[0, 0].set_title(f'S21 Gain vs I at {f} GHz')
axs[0, 0].grid(True)
axs[0, 0].legend()
for I_list, phase_list, idx in all_phase_list:
    axs[1, 0].plot(I_list, phase_list, marker='o', color=colors[idx], label=f'Av={Av_list[idx]}')
axs[1, 0].set_xlabel('I')
axs[1, 0].set_ylabel(f'S21 Phase @ {f} GHz (deg)')
axs[1, 0].set_title(f'S21 Phase vs I at {f} GHz')
axs[1, 0].grid(True)
axs[1, 0].legend()
for Q_list, q_gain_list, idx in all_q_gain_list:
    axs[0, 1].plot(Q_list, q_gain_list, marker='o', color=colors[idx], label=f'Av={Av_list[idx]}')
axs[0, 1].set_ylabel(f'S21 Gain @ {f} GHz (dB)')
axs[0, 1].set_title(f'S21 Gain vs Q at {f} GHz')
axs[0, 1].grid(True)
axs[0, 1].legend()
for Q_list, q_phase_list, idx in all_q_phase_list:
    axs[1, 1].plot(Q_list, q_phase_list, marker='o', color=colors[idx], label=f'Av={Av_list[idx]}')
axs[1, 1].set_xlabel('Q')
axs[1, 1].set_ylabel(f'S21 Phase @ {f} GHz (deg)')
axs[1, 1].set_title(f'S21 Phase vs Q at {f} GHz')
axs[1, 1].grid(True)
axs[1, 1].legend()
plt.tight_layout()

end_time = time.time()
print(f'Runtime: {end_time - start_time:.2f} seconds')

plt.show()

instruments.vna.cfg_pwr(pwr=-40)
instruments.vna.write(":OUTP OFF")
workbook.close()
print(f'\nData Dump File: {fname}')
