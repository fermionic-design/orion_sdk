# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 17:34:30 2023

@author: ananya
"""
"""
Setup: VDD_2P7-2.7V, VDD_NEG-m5V
Connections with DSO: Connect the soldered TR wire, PA_BIASx, LNA BIASx to three respective DSO channel (x can be 0,1,2,3)
Run the code and observe the waveforms in DSO
"""

import sys
import serial
sys.path.append('../include')
from ORION_8G_12G import *
from SPI import *
    
spi = SPI()
orion = ORION_8G_12G(spi)

# Set tx_mask as 1 for pa0 and tx0, 2 for pa1 and tx1, 4 for pa2 and tx2, 8 for pa3 and tx3
orion.TR_MASK.tx_mask = 0x1
orion.TR_MASK.write()

orion.DAC_CTRL_PA0.DAC_CTRL_PA0 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_PA0.write()
orion.DAC_CTRL_PA1.DAC_CTRL_PA1 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_PA1.write()
orion.DAC_CTRL_PA2.DAC_CTRL_PA2 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_PA2.write()
orion.DAC_CTRL_PA3.DAC_CTRL_PA3 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_PA3.write()

orion.DAC_CTRL_PA0_PDN.DAC_CTRL_PA0_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_PA0_PDN.write()
orion.DAC_CTRL_PA1_PDN.DAC_CTRL_PA1_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_PA1_PDN.write()
orion.DAC_CTRL_PA2_PDN.DAC_CTRL_PA2_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_PA2_PDN.write()
orion.DAC_CTRL_PA3_PDN.DAC_CTRL_PA3_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_PA3_PDN.write()

spi.tr_set()
orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()
print("observe the pa bias voltage and press enter to toggle the pa bias")
input()
spi.tr_reset()
orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()
print("observe the toggled pa bias voltage")

spi.close()