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

orion.TR_MASK.rx_mask = 0xF
orion.TR_MASK.write()

orion.DAC_CTRL_LNA0.DAC_CTRL_LNA0 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_LNA0.write()
orion.DAC_CTRL_LNA1.DAC_CTRL_LNA1 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_LNA1.write()
orion.DAC_CTRL_LNA2.DAC_CTRL_LNA2 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_LNA2.write()
orion.DAC_CTRL_LNA3.DAC_CTRL_LNA3 = 0 # 0 corresponds to -4.5V
orion.DAC_CTRL_LNA3.write()

orion.DAC_CTRL_LNA0_PDN.DAC_CTRL_LNA0_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_LNA0_PDN.write()
orion.DAC_CTRL_LNA1_PDN.DAC_CTRL_LNA1_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_LNA1_PDN.write()
orion.DAC_CTRL_LNA2_PDN.DAC_CTRL_LNA2_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_LNA2_PDN.write()
orion.DAC_CTRL_LNA3_PDN.DAC_CTRL_LNA3_PDN = 127 # 127 corresponds to -2.5V
orion.DAC_CTRL_LNA3_PDN.write()

spi.tr_set()
orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()
orion.EXT_CTRL_STS_REG_1.read()
# orion.EXT_CTRL_STS_REG_1.display()
print("observe the lna bias voltage and press enter to toggle the lna bias")
input()
spi.tr_reset()
orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()
orion.EXT_CTRL_STS_REG_1.read()
# orion.EXT_CTRL_STS_REG_1.display()
print("observe the toggled lna bias voltage")
spi.close()