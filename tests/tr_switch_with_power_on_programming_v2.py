# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 17:34:30 2023

@author: pradipta
"""

import sys
sys.path.append('../include')
import serial
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
import time


from ORION_8G_12G import *
from SPI import *
    
spi = SPI()
orion = ORION_8G_12G(spi)



#spi.txl_set()
# spi.txl_reset()
#spi.tr_tggl()
# spi.tr_reset()
#spi.tr_tggl()


orion.TR_MASK.rx_mask = 0xF
orion.TR_MASK.tx_mask = 0xF
orion.TR_MASK.write()

RF_CTRL_FUNC.set_RX_bias_mode(orion, 'LOW_V2')
RF_CTRL_FUNC.set_TX_bias_mode(orion, 'NOM')

orion.DAC_CTRL_PA0.DAC_CTRL_PA0 = 127
orion.DAC_CTRL_PA0.write()
orion.DAC_CTRL_PA1.DAC_CTRL_PA1 = 127
orion.DAC_CTRL_PA1.write()
orion.DAC_CTRL_PA2.DAC_CTRL_PA2 = 127
orion.DAC_CTRL_PA2.write()
orion.DAC_CTRL_PA3.DAC_CTRL_PA3 = 127
orion.DAC_CTRL_PA3.write()

orion.DAC_CTRL_LNA0.DAC_CTRL_LNA0 = 0
orion.DAC_CTRL_LNA0.write()
orion.DAC_CTRL_LNA1.DAC_CTRL_LNA1 = 0
orion.DAC_CTRL_LNA1.write()
orion.DAC_CTRL_LNA2.DAC_CTRL_LNA2 = 0
orion.DAC_CTRL_LNA2.write()
orion.DAC_CTRL_LNA3.DAC_CTRL_LNA3 = 0
orion.DAC_CTRL_LNA3.write()

orion.DAC_CTRL_PA0_PDN.DAC_CTRL_PA0_PDN = 0
orion.DAC_CTRL_PA0_PDN.write()
orion.DAC_CTRL_PA1_PDN.DAC_CTRL_PA1_PDN = 0
orion.DAC_CTRL_PA1_PDN.write()
orion.DAC_CTRL_PA2_PDN.DAC_CTRL_PA2_PDN = 0
orion.DAC_CTRL_PA2_PDN.write()
orion.DAC_CTRL_PA3_PDN.DAC_CTRL_PA3_PDN = 0
orion.DAC_CTRL_PA3_PDN.write()

orion.DAC_CTRL_LNA0_PDN.DAC_CTRL_LNA0_PDN = 127
orion.DAC_CTRL_LNA0_PDN.write()
orion.DAC_CTRL_LNA1_PDN.DAC_CTRL_LNA1_PDN = 127
orion.DAC_CTRL_LNA1_PDN.write()
orion.DAC_CTRL_LNA2_PDN.DAC_CTRL_LNA2_PDN = 127
orion.DAC_CTRL_LNA2_PDN.write()
orion.DAC_CTRL_LNA3_PDN.DAC_CTRL_LNA3_PDN = 127
orion.DAC_CTRL_LNA3_PDN.write()

spi.pa_set()

orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()

orion.REG4_EXT_BIAS.rsvd7 = 0x02
orion.REG4_EXT_BIAS.write()

spi.tr_reset()
orion.EXT_CTRL_STS_REG_1.read()
orion.EXT_CTRL_STS_REG_1.display()
spi.tr_tggl()
time.sleep(1)
orion.EXT_CTRL_STS_REG_1.read()
orion.EXT_CTRL_STS_REG_1.display()
spi.tr_tggl()
time.sleep(1)
orion.EXT_CTRL_STS_REG_1.read()
orion.EXT_CTRL_STS_REG_1.display()
for i in range(1,1000000000000):
    spi.tr_tggl()
    time.sleep(5)

orion.TR_CFG.data_path_en = 0x0
orion.TR_CFG.write()

spi.close()