import sys
import serial

sys.path.append('../../include')

from ORION_8G_12G import *
from SPI import *

spi = SPI()
orion = ORION_8G_12G(spi)

orion.TR_CFG.tr_mode_sel = 0x1
orion.TR_CFG.write()

orion.TR_SW_CTRL.tr_reg = 0x1
orion.TR_SW_CTRL.write()

orion.TR_CTRL_5.en_pol = 0x0
orion.TR_CTRL_5.write()
orion.TR_CTRL_5.display()
print('------------------')

orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()
orion.TR_CFG.read()
print('data path en = '+hex(orion.TR_CFG.data_path_en))

orion.REG1_EXT_BIAS.rsvd6 = 0x1
orion.REG1_EXT_BIAS.ext_bias_neg_sw_isink = 0x1
orion.REG1_EXT_BIAS.write()
orion.REG1_EXT_BIAS.read()
orion.REG1_EXT_BIAS.display()
print('------------------')

orion.REG4_EXT_BIAS.rsvd7 = 0x80
orion.REG4_EXT_BIAS.write()
orion.REG4_EXT_BIAS.read()
orion.REG4_EXT_BIAS.display()
print('------------------')
# print('reg4_ext_bias = '+hex(orion.REG4_EXT_BIAS.reg4_ext_bias))


orion.TR_SW_CTRL.tr_reg = 0x1
orion.TR_SW_CTRL.write()
orion.TR_SW_CTRL.read()

# spi.dump_regs(start_addr=0, end_addr= 255,path='./logs/orion_v1.csv')
# orion.EXT_CTRL_STS_REG_2.read()
# orion.EXT_CTRL_STS_REG_2.display()


spi.close()

