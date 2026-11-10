"""
SAR ADC voltage sweep on GP4.

Sweeps the DC power supply (DCPS) output from V_START to V_STOP, applies it to
the GP4 pin, reads the SAR ADC output for GP4 at each step and saves
voltage vs. ADC code (decimal) to a CSV file.
"""

import os
import sys
import csv
import time
import datetime

import numpy as np
import pyvisa

sys.path.append('../../include')
from ORION_8G_12G import *
from SPI import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *

# ----------------------------- User settings -----------------------------
CHIP_NAME = '57'        # DUT identifier -> 'chip1' in the output file name
TEMP = '25C'           # test temperature, for the output file name
VDD = '2p7V'           # chip supply voltage, for the output file name
version = 'v2'
adc_input = 'gp4'

DCPS_ADDR = 'USB0::0x1AB1::0x0E11::DP8F251700261::INSTR'  # Rigol DP800 DC supply
DCPS_CH = 2            # supply channel wired to GP4
CURRENT_LIMIT = 0.01   # A
V_START = 0.0          # V
V_STOP = 2.7           # V
V_STEP = 0.01          # V
SETTLE_TIME = 0.1      # s, wait after each voltage change

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # ':' is not allowed in Windows file names
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'char', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)
CSV_FILE = os.path.join(LOG_DIR, f'chip{CHIP_NAME}__{version}__sar_adc_char__adc_input_{adc_input}__temp_{TEMP}__vdd_{VDD}__{timestamp}.csv')
# -------------------------------------------------------------------------


def read_sar_adc(hal, timeout=1.0):
    """Run one SAR ADC conversion and return the 9-bit code."""
    hal.enable_adc(1)
    t0 = time.time()
    while not hal.read_adc_eoc():
        if time.time() - t0 > timeout:
            print('WARN: ADC EOC timeout')
            break
    adc_val = hal.read_adc_output()
    hal.enable_adc(0)
    return adc_val


# ---------------------------- DUT setup ----------------------------------
spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

orion_hal.sel_adc_input(adc_input)
read_sar_adc(orion_hal)  # dummy conversion, discard first reading

# ---------------------------- DCPS setup ---------------------------------
try:
    rm = pyvisa.ResourceManager()          # NI/Keysight VISA, if installed
except ValueError:
    rm = pyvisa.ResourceManager('@py')     # fall back to pyvisa-py
print('VISA resources: ', rm.list_resources())
try:
    dcps = rm.open_resource(DCPS_ADDR)
except Exception:
    spi.close()
    raise
print('DC Supply: ', dcps.query('*IDN?').strip())

dcps.write(f':SOUR{DCPS_CH}:CURR {CURRENT_LIMIT}')
dcps.write(f':SOUR{DCPS_CH}:VOLT {V_START}')
dcps.write(f':OUTP CH{DCPS_CH},ON')
time.sleep(SETTLE_TIME)

# ------------------------------ Sweep ------------------------------------
voltages = np.round(np.arange(V_START, V_STOP + V_STEP / 2, V_STEP), 4)

try:
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Voltage (V)', 'SAR ADC Output (dec)'])

        for v in voltages:
            dcps.write(f':SOUR{DCPS_CH}:VOLT {v}')
            time.sleep(SETTLE_TIME)
            adc_val = read_sar_adc(orion_hal)
            print(f'Voltage: {v:.3f} V  ->  SAR ADC OUTPUT: {adc_val}')
            writer.writerow([v, adc_val])
            f.flush()
finally:
    dcps.write(f':SOUR{DCPS_CH}:VOLT 0')
    dcps.write(f':OUTP CH{DCPS_CH},OFF')
    dcps.close()
    orion_hal.sel_adc_input('none')
    spi.close()

print(f'\nData saved to {CSV_FILE}')
