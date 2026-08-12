"""
bfm_DETx_Flash_ADC_Test.py

Enables all four on-chip power detectors (DET0-DET3) on the ORION
8G/12G BFM device via SPI, toggles the TR (transmit/receive) line to
trigger a fresh detector reading, then reads back and prints each
detector's flash-ADC output code (3-bit value per detector, packed
two detectors per register).

Setup: connect a signal generator to one or more of the detector ports
(DET0-DET3) on the BFM before running this script, so the flash ADC
has an actual RF signal to detect and convert.

Note: the detectors are force-enabled directly via det_en_force /
det_en_force_val, rather than through the proper per-channel enables,
so this test bypasses the normal channel-enable path.

Usage: run standalone against a connected/simulated BFM part over SPI.
"""

import sys
sys.path.append('../include')
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from SPI import *
import time


#------------------------------------------------------------
# Open the SPI link and bind it to an ORION_8G_12G register map instance
spi = SPI()
orion = ORION_8G_12G(spi)

#-------------------------------------------------------------
# Enable Detector Register : orion.TR_CTRL_2.det_en_force_val = DET_EN_CODE
# DET_EN_CODE : DETAILS
# 0x1         : DET0 ON
# 0x2         : DET1 ON
# 0x4         : DET2 ON
# 0x8         : DET3 ON
# 0xF         : ALL DET ON

# Force-enable all four detectors (bypass the normal TR-state-based enable)
orion.TR_CTRL_2.det_en_force = 0xF
orion.TR_CTRL_2.det_en_force_val = 0xF
orion.TR_CTRL_2.write()

# Toggle TR (transmit/receive) to re-trigger the detectors and let the
# flash ADC output settle before reading it back
spi.tr_reset()
time.sleep(0.5)
spi.tr_set()
time.sleep(0.5)

# DET0/DET1 and DET2/DET3 are each packed into one register:
# bits [2:0] = lower detector, bits [5:3] = upper detector
flash_adc_output_DET0 = (orion.DET_0_1_ADC_OUT_BIN.read() & 0x7)
flash_adc_output_DET1 = ((orion.DET_0_1_ADC_OUT_BIN.read() & 0x38) >> 3)
flash_adc_output_DET2 = (orion.DET_2_3_ADC_OUT_BIN.read() & 0x7)
flash_adc_output_DET3 = ((orion.DET_2_3_ADC_OUT_BIN.read() & 0x38) >> 3)

# Report the 3-bit flash ADC code for each detector
print('Flash ADC Output DET0:', flash_adc_output_DET0)
print('Flash ADC Output DET1:', flash_adc_output_DET1)
print('Flash ADC Output DET2:', flash_adc_output_DET2)
print('Flash ADC Output DET3:', flash_adc_output_DET3)

# Release the SPI link
spi.close()