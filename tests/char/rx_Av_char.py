# -- coding: utf-8 --
"""
Loop the RX gain code (Av) at a fixed I/Q and print S21 gain/phase from the VNA at f_disp.
"""
version = 'v2'
vdd = '3p3'     # supply voltage, label for the file name only
temp = '25C'    # temperature, label for the file name only
bias = 'NOM'    # RX bias: 'NOM' or 'LOW'
ant_sel = 0x8   # RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8
i_code = 264    # fixed I code, -255...255
q_code = 464      # fixed Q code, -255...255
av_max = 2047
av_step = 16       # step while av > av_switch
av_switch = 32
av_fine_step = 1   # step once av <= av_switch
av_codes = []      # sweep from av_max down to 0
av = av_max
while av >= 0:
    av_codes.append(av)
    av -= av_step if av > av_switch else av_fine_step

f_min, f_max, f_step = 7, 13, 0.25
f_disp = 9.5   # GHz printed

d1 = 0.1   # delay after setting Av
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
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg_freq(start=f_min*1e9, stop=f_max*1e9, step=f_step*1e9)
instruments.vna.cfg_pwr(pwr=8)
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx(bias)
orion_hal.set_tr_mask(rx_mask=ant_sel)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)

def iq_code(v):
    return 256 - v if v < 0 else v   # bit 8 = sign, low 8 bits = magnitude

os.makedirs('./logs', exist_ok=True)
csv_path = f'./logs/rx_Av_char__{version}__ant_sel_{ant_sel}__vdd_{vdd}__temp_{temp}__bias_{bias}__iq_[{i_code},{q_code}]__av_[{av_max},{av_step},{av_switch},{av_fine_step},0]__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.csv'
rows = queue.Queue()

def csv_writer():
    with open(csv_path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Av'] + [f'Gain dB {fr:g}GHz' for fr in freqs] + [f'Phase deg {fr:g}GHz' for fr in freqs])
        while (row := rows.get()) is not None:
            w.writerow(row)
            fh.flush()

writer = threading.Thread(target=csv_writer)
writer.start()

total = len(av_codes)
done = 0
loop_start = time.time()
for av in av_codes:
    orion_hal.set_iq_val(iq_code(i_code), iq_code(q_code), av, ant_sel)
    orion_hal.stg2_load()
    time.sleep(d1)
    instruments.vna.write(":SENS:AVER:CLE")
    time.sleep(d2)

    gain = np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
    phase = np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)
    rows.put([av] + gain.tolist() + phase.tolist())
    done += 1
    print(f'\rAv = {av:4d}  ||  Gain @ {f_disp} GHz = {gain[fi]:7.2f} dB  |  Phase = {phase[fi]:8.2f} deg')
    eta = '--:--:--'
    if 100 * done >= total:   # wait for 1% before estimating
        eta = str(datetime.timedelta(seconds=round((time.time() - loop_start) / done * (total - done))))
    print(f'[{"#" * (30 * done // total):<30}] {100 * done // total:3d}%  ({done}/{total})  ETA {eta}', end='', flush=True)

print()
rows.put(None)
writer.join()
print(f'Data saved to {csv_path}')
instruments.vna.write(":OUTP OFF")
spi.close()
