# -- coding: utf-8 --
"""
Phase of all 4 channels (RX0...RX3 or TX0...TX3) vs temperature, at one phase code + gain code.

The same p_idx / g_idx is set through the LUT (set_lut_idx) on every channel. The channels are
measured one at a time: only that channel is enabled in the TR mask, then S21 (RX) / S12 (TX)
gain and phase are read from the VNA at f_disp (9.5 GHz).

One run = one temperature: set the chamber, set temp below, press run. All 4 channels are measured once,
one row is added to the Excel and the script ends.
reset = 'yes': the run starts a new Excel.
reset = 'no' : the row is added to the newest Excel of the same chip / path / p_idx / g_idx.

Excel columns: Temp (C), RX0...RX3 phase (deg) at f_disp.
"""
chip_name = 'chip_53'   # chip ID, printed and saved with the results
version = 'v2'
vdd = '2p7'     # supply voltage, label for the file name only
path = 'rx'     # 'rx': RX0...RX3 (VNA S21), 'tx': TX0...TX3 (VNA S12)

p_idx = 4       # phase code (4...124), 360/121 = 2.975 deg / code
g_idx = 0       # gain code (0...63), 0.5 dB / code

temp = 30          # C, chamber temperature for this run (change by hand before each run)
reset = 'no'       # 'yes': start a new Excel, 'no': add this run's row to the newest Excel

pause_between_ch = False   # True: wait for Enter before each channel (to move the VNA cable)

rx_mode = 'dual_lut'   # 'single_lut': '9G' LUT (NOM bias) for every g_idx, 'dual_lut': g_idx <= rx_lut_switch -> '9G' LUT + NOM bias, else '11G' LUT + low bias
rx_lut_switch = 31     # dual_lut: last g_idx that uses the NOM-bias LUT
rx_low_i, rx_low_q = 0, 1   # dual_lut low-bias RX combiner I / Q tail currents, must match the rx_f2 LUTs (bias_i0_q1)
tx_bias = 'MAX'        # TX bias preset: 'MAX', 'NOM', 'LOW', '2W_FEM' or '5W_FEM'

lut_dir = r'C:\Users\silic\Downloads\9.5LUTs'
lut_files = dict(   # 9.5 GHz LUTs; rx_f1 = freq_id '9G' (NOM bias), rx_f2 = freq_id '11G' (low bias i0_q1)
    tx_gain     = rf'{lut_dir}\chip_55__4ch__v2__tx_gain_lut__freq_9p5__algo_joint_max__iq_[172,-180]__bias_max__pin_10__vdd_2p7__temp_25C.xlsx',
    tx_phase    = rf'{lut_dir}\v2__tx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_max__pin_10__vdd_2p7__temp_25C__chip55__ant_0123.xlsx',
    rx_f1_gain  = rf'{lut_dir}\chip_55__4ch__v2__rx_gain_lut__freq_9p5__algo_joint_max__iq_[248,4]__bias_nom__vdd_2p7__temp_25C__max_code_41.xlsx',
    rx_f1_phase = rf'{lut_dir}\v2__rx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_nom__vdd_2p7__temp_25C__step_1.xlsx',
    rx_f2_gain  = rf'{lut_dir}\chips_52_53_54_55__16ch__v2__rx_gain_lut__freq_9p5__algo_joint_max__iq_[80,96]__bias_i0_q1__vdd_2p7__temp_25C.xlsx',
    rx_f2_phase = rf'{lut_dir}\v2__rx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_i0_q1__vdd_2p7__temp_25C__chip_51_52_55.xlsx',
)

load_lut = True   # False: skip loading the LUTs (saves time) when they are already loaded and the chip has not been power-cycled

f_disp = 9.5      # GHz, the VNA measures only this one point (CW)
Pin_rx = -40      # VNA source power for RX in dBm
Pin_tx = -20      # VNA source power for TX in dBm
n_avg = 1         # VNA sweeps averaged per channel; every sweep adds a few ms of VNA overhead, so the noise is set by ifbw instead
ifbw = 10         # VNA IF bandwidth in Hz: 10 Hz ~ 0.1 s per reading, about the same noise as 128 averages at 1 kHz
d_settle = 0.2
# s, channel switching time: delay after switching channel before the VNA is triggered
                  # measure time ~ 4 x (d_settle + ~0.15 s VNA + SPI) ~ 1.5 s for all 4 channels

import sys
sys.path.append('../../include')

from instruments import instruments
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import glob
import openpyxl
import os
import time
import datetime

path = path.lower()
assert path in ('rx', 'tx'), "path must be 'rx' or 'tx'"
P = path.upper()
ALL = 0xF

def wrap(x):
    return (x + 180) % 360 - 180

instruments = instruments(required_instruments=['vna'])
instruments.vna.init()

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)
if load_lut:
    orion_hal.init_lut_new(lut_files['tx_gain'], lut_files['tx_phase'],
                           lut_files['rx_f1_gain'], lut_files['rx_f1_phase'],
                           lut_files['rx_f2_gain'], lut_files['rx_f2_phase'])

orion_csr.DEVICE_ID.read()
device_id = hex(orion_csr.DEVICE_ID.device_id)

def setup_vna(sp, pwr):
    # set after the measurements are defined, otherwise the VNA keeps its default sweep
    instruments.vna.cfg(1, f'{sp}_GAIN')
    instruments.vna.cfg(2, f'{sp}_PHASE')
    instruments.vna.write(':SENS:SWE:TYPE CW')
    instruments.vna.write(f':SENS:FREQ:CW {f_disp*1e9}')
    instruments.vna.write(':SENS:SWE:POIN 1')
    instruments.vna.write(f':SENS:BWID {ifbw}')
    instruments.vna.cfg_pwr(pwr=pwr)
    instruments.vna.write(':SENS:AVER:STAT ON')
    instruments.vna.write(f':SENS:AVER:COUN {n_avg}')
    instruments.vna.write(':SENS:SWE:MODE HOLD')   # sweeps only when triggered in read_vna()
    instruments.vna.rm_vna.timeout = 60000        # ms, *OPC? returns only after all n_avg sweeps
    instruments.vna.query('*OPC?')

def read_vna():
    # restart averaging, run exactly n_avg sweeps and wait until they are done (no fixed delay)
    instruments.vna.write(':SENS:AVER:CLE')
    instruments.vna.write(f':SENS:SWE:GRO:COUN {n_avg}')
    instruments.vna.query(':SENS:SWE:MODE GRO;*OPC?')
    gain = float(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(',')[0])
    phase = float(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(',')[0])
    return gain, phase

def set_mask(mask):
    if path == 'rx':
        orion_hal.set_tr_mask(rx_mask=mask)
    else:
        orion_hal.set_tr_mask(tx_mask=mask)

try:
    orion_hal.set_tr_mode('INT_TR')
    if path == 'rx':
        setup_vna('S21', Pin_rx)
        orion_hal.set_trx_mode(0)
        orion_hal.init_rx('NOM', ant_sel=ALL)
        if rx_mode == 'dual_lut' and g_idx > rx_lut_switch:
            freq_id, bias = '11G', f'i{rx_low_i}_q{rx_low_q}'
            orion_hal.set_rx_bias(rx_low_i, rx_low_q, ant_sel=ALL)   # overrides the NOM currents
        else:
            freq_id, bias = '9G', 'NOM'
        # set_mask(ALL)
        orion_hal.set_freq(freq_id)
        orion_hal.cfg_stg2_load('REG')
        orion_hal.enable_rx_correction(1)
        Pin = Pin_rx
    else:
        setup_vna('S12', Pin_tx)
        orion_hal.set_trx_mode(1)
        orion_hal.init_tx(tx_bias, ant_sel=ALL)
        # set_mask(ALL)
        orion_hal.set_freq('9G')
        orion_hal.cfg_stg2_load('REG')
        freq_id, bias, Pin = '9G', tx_bias, Pin_tx
    orion_hal.en_data_path(1)

    orion_hal.en_data_path(0)   # data path is on only while measuring, so the BFM does not heat up
    target = wrap((p_idx - 4) * 360 / 121)

    def measure(T):
        t0 = time.time()
        orion_hal.en_data_path(1)
        res = []   # per channel: (I, Q, Av, gain dB, phase deg)
        t_ch = []  # per channel: (switch + settle s, VNA s)
        try:
            for ch in range(4):
                ta = time.time()
                if pause_between_ch:
                    input(f'Connect the VNA to {P}{ch}, then press Enter...')
                set_mask(1 << ch)   # only this channel on
                orion_hal.set_lut_idx(p_idx, g_idx, 1 << ch)
                orion_hal.stg2_load()
                time.sleep(d_settle)
                tb = time.time()
                gain, phase = read_vna()
                t_ch.append((tb - ta, time.time() - tb))
                res.append((orion_hal.phase_val_i, orion_hal.phase_val_q, orion_hal.gain_val, gain, phase))
        finally:
            orion_hal.en_data_path(0)
        print()
        print(f'Temp = {T} C  |  Chip ID = {chip_name}  |  device_id = {device_id}  |  Mode = {P}  |  p_idx = {p_idx}  g_idx = {g_idx}  |  '
              f'bias {bias}  LUT {freq_id}  |  target phase = {target:.2f} deg  |  @ {f_disp} GHz')
        print(f'{"ch":<5}{"I":>5}{"Q":>5}{"Av":>6}{"Gain dB":>10}{"Phase deg":>11}{"vs ch0 deg":>12}')
        for ch, (i_code, q_code, av, gain, phase) in enumerate(res):
            print(f'{P}{ch:<3}{i_code:>5}{q_code:>5}{av:>6}{gain:>10.2f}{phase:>11.2f}{wrap(phase - res[0][4]):>12.2f}')
        print(f'measure time {time.time() - t0:.2f} s  (per channel switch+settle / VNA: '
              + ', '.join(f'{P}{ch} {a:.2f}/{b:.2f}' for ch, (a, b) in enumerate(t_ch)) + ' s)')
        return [r[4] for r in res]

    os.makedirs('./logs', exist_ok=True)
    file_key = f'{chip_name}__{path}_4ch_phase_vs_temp__{version}__vdd_{vdd}__p_idx_{p_idx}__g_idx_{g_idx}'
    header = ['Temp (C)'] + [f'{P}{ch} Phase (deg)' for ch in range(4)]

    def new_excel(T):
        xl = f'./logs/{file_key}__start_temp_{T}C__{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.xlsx'
        wb = openpyxl.Workbook()
        wb.active.append(header)
        wb.save(xl)
        print(f'New Excel: {xl}')
        return xl

    def add_row(xl, row, gap=False):
        # gap: leave one empty line before this row (first row after a reset); not before the first data row
        while True:
            try:
                wb = openpyxl.load_workbook(xl)
                ws = wb.active
                r = ws.max_row + (2 if gap and ws.max_row > 1 else 1)
                for c, v in enumerate(row, start=1):
                    ws.cell(row=r, column=c, value=v)
                wb.save(xl)
                print(f'Row added to {xl}')
                return
            except PermissionError:
                input(f'Cannot write {xl} (open in Excel?). Close it and press Enter to retry...')

    xl = None
    if str(reset).lower() != 'yes':
        old = sorted(glob.glob(f'./logs/{file_key}__start_temp_*.xlsx'), key=os.path.getmtime)
        if old:
            xl = old[-1]
            print(f'Adding to {xl}')
        else:
            print(f'reset = no, but there is no Excel for {file_key}, starting a new one')
    if xl is None:
        xl = new_excel(temp)

    add_row(xl, [temp] + [round(ph, 4) for ph in measure(temp)])
finally:
    instruments.vna.write(":OUTP OFF")
    orion_hal.en_data_path(0)   # turn off the BFM so it does not heat up
    spi.close()
