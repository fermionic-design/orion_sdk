# -- coding: utf-8 --
"""
Loop the TX gain code (Av) at a fixed I/Q and print S12 gain/phase from the VNA at f_disp.
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
# (I, Q) codes, -255...255. An Av sweep runs for each pair.
# iq_pairs = [(248, 4), (136, 136), (1, 220), (-196, 196), (-248, -2), (-120, -120), (0, -224), (204, -204)]
iq_pairs = [(248, 4)]   # None: pick n_phase_pairs (I, Q) pairs, evenly spaced in phase, from phase_lut
# phase_lut = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__tx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_max__pin_10__vdd_2p7__temp_25C__chip_55_tx0.xlsx'   # TX phase LUT xlsx (used if iq_pairs is None)
# n_phase_pairs = 8   # number of phase states picked from phase_lut, 360 / n_phase_pairs deg apart (45 deg for 8)

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
Pin = -20   # VNA source power in dBm, also in the file name

d1 = 0.1   # delay after setting Av
d2 = 0.2   # delay after clearing averaging
d_first = 3   # extra delay before the first point of each sweep, the VNA trace is not valid until its first sweep finishes

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
import openpyxl

if iq_pairs is None:
    # phase LUT: 121 phase states (entries pad...pad+120, one per 360/121 deg), signed (I, Q) stored in the I-Code / Q-Code columns
    # (layout copied from the RX phase LUT; check it matches the TX LUT before using)
    states, pad = 121, 4
    decode = lambda c: 256 - c if c >= 256 else c   # I-Code / Q-Code: bit 8 = sign, negative v is stored as 256 - v
    lut_rows = list(openpyxl.load_workbook(phase_lut)['Sheet1'].iter_rows(min_row=2, values_only=True))
    iq_pairs = []
    for k in range(n_phase_pairs):
        row = lut_rows[pad + int(round(k * states / n_phase_pairs))]
        iq_pairs.append((decode(row[0]), decode(row[1])))
    print(f'iq_pairs from {os.path.basename(phase_lut)}: {iq_pairs}')

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

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

hw_ant_sel = 0xF if ant_sel_all else ant_sel   # value passed to every hardware call
ant_tag = f'all_{ant_sel}' if ant_sel_all else f'{ant_sel}'   # file name: all_15 = all TX on, ant_sel only labels the DUT channel

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

os.makedirs('./logs', exist_ok=True)

for pair_n, (i_code, q_code) in enumerate(iq_pairs, 1):
    print(f'\n--- I/Q pair {pair_n}/{len(iq_pairs)}: I = {i_code}, Q = {q_code} ---')
    csv_path = f'./logs/{chip_name}__tx_Av_char__{version}__ant_sel_{ant_tag}__vdd_{vdd}__temp_{temp}__bias_{bias_tag}__pin_{Pin}__iq_[{i_code},{q_code}]__av_[{av_max},{av_step},{av_switch},{av_fine_step},0]__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.csv'
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
        orion_hal.set_iq_val(iq_code(i_code), iq_code(q_code), av, hw_ant_sel)
        orion_hal.stg2_load()
        time.sleep(d1)
        if done == 0:
            time.sleep(d_first)
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
orion_hal.en_data_path(0)   # turn off the BFM so it does not heat up
spi.close()
