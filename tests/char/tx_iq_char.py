# -- coding: utf-8 --
"""
Loop TX I/Q codes and print S12 gain/phase from the VNA at f_disp.
"""
chip_name = 'chip_55'   # DUT label, prefixed to the file name
version = 'v2'
vdd = '2p7'     # supply voltage, label for the file name only
temp = '25C'    # temperature, label for the file name only
bias_mode = 'preset'     # 'preset': orion_hal.init_tx(bias), 'curr': orion_hal.set_tx_bias(i_curr, q_curr, drv_curr, lna_curr) only (no init_tx)
bias = 'MAX'    # preset mode: TX bias 'MAX', 'NOM', 'LOW', '2W_FEM' or '5W_FEM'
i_curr = 1      # curr mode: TX combiner I tail current, 2-bit (0...3)
q_curr = 1      # curr mode: TX combiner Q tail current, 2-bit (0...3)
drv_curr = 31   # curr mode: TX driver (final_av) current, 5-bit (0...31)
lna_curr = 3    # curr mode: common TX LNA current, 2-bit (0...3)
ant_sel = 0x8   # TX0: 0x1, TX1: 0x2, TX2: 0x4, TX3: 0x8
ant_sel_all = True   # True: hardware calls always get 0xF and ant_sel is only used for the file name; False: ant_sel is applied to the hardware
av = 2047
i_codes = list(range(-252, 253, 4))   # multiples of 4 -> 2 LSBs are 0
q_codes = list(range(-252, 253, 4))   # multiples of 4 -> 2 LSBs are 0

sweep = 'axis'         # 'grid': every (I, Q) of i_codes x q_codes, 'axis': only bands around the I and Q axes
axis_width = 11        # axis mode: band half-width, e.g. for I = 0 sweep Q = -16...+16
axis_step = 1          # axis mode: code step across the band
axis_along_step = 4    # axis mode: code step along the axis (the i_codes / q_codes range is used)

f_min, f_max, f_step = 7, 13, 0.25
f_disp = 9.5   # GHz printed
Pin = -20   # VNA source power in dBm, also in the file name

d1 = 0.1   # delay after setting IQ
d2 = 0.2   # delay after clearing averaging
d_first = 3   # extra delay before the first point, the VNA trace is not valid until its first sweep finishes

import sys
sys.path.append('../../include')

from instruments import instruments
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import numpy as np
import csv
import os
import queue
import threading
import time
import datetime

freq_pts = int((f_max-f_min)/f_step)+1
freqs = f_min + f_step*np.arange(freq_pts)
fi = int(round((f_disp-f_min)/f_step))

instruments = instruments(required_instruments=['vna'])
instruments.vna.init()
instruments.vna.cfg(1, 'S12_GAIN')
instruments.vna.cfg(2, 'S12_PHASE')
instruments.vna.cfg_freq(start=f_min*1e9, stop=f_max*1e9, step=f_step*1e9)
instruments.vna.cfg_pwr(pwr=Pin)
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

hw_ant_sel = 0xF if ant_sel_all else ant_sel   # value passed to every hardware call
ant_tag = f'all_{ant_sel}' if ant_sel_all else f'{ant_sel}'   # file name: all_4 = all TX on, ant_sel only labels the DUT channel

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

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

def iq_code(v):
    return 256 - v if v < 0 else v   # bit 8 = sign, low 8 bits = magnitude

if sweep == 'grid':
    points = [(i, q) for q in q_codes for i in i_codes]
    iq_tag = f'{i_codes[0]},{i_codes[1]-i_codes[0]},{i_codes[-1]}'
else:
    across = range(-axis_width, axis_width + 1, axis_step)
    along_i = range(i_codes[0], i_codes[-1] + 1, axis_along_step)
    along_q = range(q_codes[0], q_codes[-1] + 1, axis_along_step)
    points = [(i, q) for q in across for i in along_i]          # band around the I axis (Q ~ 0)
    points += [(i, q) for q in along_q for i in across]         # band around the Q axis (I ~ 0)
    points = list(dict.fromkeys(points))                        # the two bands overlap near the origin
    iq_tag = f'axis_w{axis_width}_s{axis_step}_a{axis_along_step}'

os.makedirs('./logs', exist_ok=True)
csv_path = f'./logs/{chip_name}__tx_iq_char__{version}__ant_sel_{ant_tag}__vdd_{vdd}__temp_{temp}__bias_{bias_tag}__pin_{Pin}__av_{av}__iq_[{iq_tag}]__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.csv'
rows = queue.Queue()

def csv_writer():
    with open(csv_path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['I', 'Q'] + [f'Gain dB {fr:g}GHz' for fr in freqs] + [f'Phase deg {fr:g}GHz' for fr in freqs])
        while (row := rows.get()) is not None:
            w.writerow(row)
            fh.flush()

writer = threading.Thread(target=csv_writer)
writer.start()

total = len(points)
done = 0
loop_start = time.time()
for i, q in points:
    orion_hal.set_iq_val(iq_code(i), iq_code(q), av, hw_ant_sel)
    orion_hal.stg2_load()
    time.sleep(d1)
    if done == 0:
        time.sleep(d_first)
    instruments.vna.write(":SENS:AVER:CLE")
    time.sleep(d2)

    gain = np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
    phase = np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)
    rows.put([i, q] + gain.tolist() + phase.tolist())
    done += 1
    print(f'\rI = {i:+4d}  |  Q = {q:+4d}  ||  Gain @ {f_disp} GHz = {gain[fi]:7.2f} dB  |  Phase = {phase[fi]:8.2f} deg')
    eta = '--:--:--'
    if 100 * done >= total:   # wait for 1% before estimating
        eta = str(datetime.timedelta(seconds=round((time.time() - loop_start) / done * (total - done))))
    print(f'[{"#" * (30 * done // total):<30}] {100 * done // total:3d}%  ({done}/{total})  ETA {eta}', end='', flush=True)

print()
rows.put(None)
writer.join()
print(f'Data saved to {csv_path}')
instruments.vna.write(":OUTP OFF")
orion_hal.en_data_path(0)   # turn off the BFM so it does not heat up
spi.close()
