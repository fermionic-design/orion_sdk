"""
PA / LNA bias DAC sweep.

Sweeps the internal 8-bit bias DAC from 0 to 255 for one PA or LNA bias
channel and reads the bias pin voltage with a digital multimeter (DMM) at
every code. Results are saved to a CSV: DAC Code | Bias Voltage (V).

Setup: VDD_2P7 = 2.7 V, VDD_NEG = -5 V
The DMM must already be connected to the PA_BIAS<ANT_SEL> / LNA_BIAS<ANT_SEL>
pin selected below.
"""

import os
import sys
import csv
import time
import datetime

import pyvisa

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'include'))
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from SPI import *

# ----------------------------- User settings -----------------------------
CHIP_NAME = '57'       # DUT identifier -> 'chip57' in the output file name
TEMP = '25C'           # test temperature, for the output file name
VDD = '2p7V'           # chip supply voltage, for the output file name
version = 'V2'
mode = 'lna'       # 'PA' or 'LNA'
ant_sel = 0           # channel: 0, 1, 2 or 3

DMM_ADDR = 'USB0::0x1AB1::0x0C94::DM3O272300791::INSTR'  # Rigol DM3058 DMM
DAC_START = 0
DAC_STOP = 255
DAC_STEP = 1
SETTLE_TIME = 0.2      # s, wait after each DAC change before measuring
# -------------------------------------------------------------------------

mode = mode.upper()
if mode not in ('PA', 'LNA'):
    sys.exit(f"BIAS_TYPE must be 'PA' or 'LNA', got {mode!r}")
if ant_sel not in (0, 1, 2, 3):
    sys.exit(f'ant_sel must be 0, 1, 2 or 3, got {ant_sel!r}')

PORT = f'{mode}{ant_sel}'                                     # e.g. 'PA0'
set_bias = getattr(RF_CTRL_FUNC, f'set_{PORT}_bias')               # e.g. set_PA0_bias

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # ':' is not allowed in Windows file names
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'char', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)
CSV_FILE = os.path.join(
    LOG_DIR,
    f'chip_{CHIP_NAME}__{version}__{mode}_bias__dac_sweep__ch{ant_sel}__temp_{TEMP}__vdd_{VDD}__{timestamp}.csv')

# ---------------------------- DMM setup ----------------------------------
try:
    rm = pyvisa.ResourceManager()          # NI/Keysight VISA, if installed
except ValueError:
    rm = pyvisa.ResourceManager('@py')     # fall back to pyvisa-py
print('VISA resources: ', rm.list_resources())
dmm = rm.open_resource(DMM_ADDR)
dmm.timeout = 5000
print('DMM: ', dmm.query('*IDN?').strip())
dmm.write(':FUNC:VOLT:DC')

# ---------------------------- DUT setup ----------------------------------
spi = SPI()
orion = ORION_8G_12G(spi)
orion.DEVICE_ID.read()
print('device_id = ' + hex(orion.DEVICE_ID.device_id))

# Force-enable only the selected channel's bias
mask = 1 << ant_sel
if mode == 'PA':
    RF_CTRL_FUNC.set_enable_LNA_bias(orion, 0x0)
    RF_CTRL_FUNC.set_enable_PA_bias(orion, mask)
else:
    RF_CTRL_FUNC.set_enable_PA_bias(orion, 0x0)
    RF_CTRL_FUNC.set_enable_LNA_bias(orion, mask)

# ------------------------------ Sweep ------------------------------------
print(f'\nSweeping {PORT} bias DAC {DAC_START}..{DAC_STOP}')
try:
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['DAC Code', f'{PORT} Bias Voltage (V)'])
        for code in range(DAC_START, DAC_STOP + 1, DAC_STEP):
            set_bias(orion, code)
            time.sleep(SETTLE_TIME)
            v_meas = float(dmm.query(':MEAS:VOLT:DC?'))
            print(f'{PORT}  DAC code: {code:3d}  ->  {v_meas:.5f} V')
            writer.writerow([code, v_meas])
            f.flush()
finally:
    RF_CTRL_FUNC.set_enable_PA_bias(orion, 0x0)
    RF_CTRL_FUNC.set_enable_LNA_bias(orion, 0x0)
    dmm.close()
    spi.close()

print(f'\nData saved to {CSV_FILE}')
