# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 14:27:30 2023

@author: ananya
"""
"""
Setup: 
Vsup = 2.5-3.3V (nominal - 2.7V)
Feed any input power from -20dBm to 16dBm through Signal generator to DETx port,set any freq from 8-12GHz
and record the SAR ADC output
While testing a particular DET, other 3 DETs should be 50 ohm terminated and other RF ports need not be terminated.
"""

import sys
sys.path.append('../include')
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from SPI import *
import time 

def get_sar_adc_value(myDevice):
    sar_adc_output=0
    RF_CTRL_FUNC.set_enable_adc(myDevice, 0)
    time.sleep(1)
    RF_CTRL_FUNC.set_enable_adc(myDevice, 1)
    time.sleep(1)
    eoc_read=RF_CTRL_FUNC.read_adc_eoc(myDevice)
    # if eoc is 1 then read adc input and output
    if eoc_read==1:
        sar_adc_output=RF_CTRL_FUNC.read_adc_output(myDevice)
    else:
        print("EOC is 0, SAR ADC conversion not complete")
    RF_CTRL_FUNC.set_enable_adc(myDevice, 0)
    time.sleep(1)
    return sar_adc_output

def reset_all_det_sel():
    orion.POWER_DET_CFG.det0_sel = 0
    orion.POWER_DET_CFG.det1_sel = 0
    orion.POWER_DET_CFG.det2_sel = 0
    orion.POWER_DET_CFG.det3_sel = 0
    orion.POWER_DET_CFG.write()

def measure_rf_only_adc(myDevice, det_ch):
    # Validate input
    if det_ch not in [0, 1, 2, 3]:
        raise ValueError("Invalid detector channel. Use 0, 1, 2, or 3.")

    # --- Measure Bias Only ---
    reset_all_det_sel()
    if det_ch == 0:
        orion.POWER_DET_CFG.det0_sel = 2
    elif det_ch == 1:
        orion.POWER_DET_CFG.det1_sel = 2
    elif det_ch == 2:
        orion.POWER_DET_CFG.det2_sel = 2
    elif det_ch == 3:
        orion.POWER_DET_CFG.det3_sel = 2
    orion.POWER_DET_CFG.write()
    time.sleep(1)
    adc_bias_only = get_sar_adc_value(myDevice)

    # --- Measure RF + Bias ---
    if det_ch == 0:
        orion.POWER_DET_CFG.det0_sel = 1
    elif det_ch == 1:
        orion.POWER_DET_CFG.det1_sel = 1
    elif det_ch == 2:
        orion.POWER_DET_CFG.det2_sel = 1
    elif det_ch == 3:
        orion.POWER_DET_CFG.det3_sel = 1
    orion.POWER_DET_CFG.write()
    time.sleep(1)
    adc_rf_plus_bias = get_sar_adc_value(myDevice)

    # --- Calculate RF-only contribution ---
    adc_rf_only = adc_rf_plus_bias - adc_bias_only
    return adc_rf_only

#------------------------------------------------------------
spi = SPI()
orion = ORION_8G_12G(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))

#-------------------------------------------------------------
""" Enable Detector Register : orion.TR_CTRL_2.det_en_force_val = DET_EN_CODE
    DET_EN_CODE : DETAILS
    0x1         : DET0 ON
    0x2         : DET1 ON
    0x4         : DET2 ON
    0x8         : DET3 ON 
    0xF         : ALL DET ON  
""" 

# Configure SAR ADC to take input from RF Peak Detector
orion.REG0_ADC.en_pkdet_to_adc_sw = 1
orion.REG0_ADC.write()

orion.TR_CTRL_2.det_en_force = 0xF
orion.TR_CTRL_2.det_en_force_val = 0xF
orion.TR_CTRL_2.write()

reset_all_det_sel()
    
adc_rf_only = measure_rf_only_adc(orion,3) # 0 for DET0, 1 for DET1, 2 for DET2 and 3 for DET3
print("SAR ADC Output (RF Component)  :", adc_rf_only)

reset_all_det_sel()
spi.close()      