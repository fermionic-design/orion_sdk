

import sys
sys.path.append('../include')
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from SPI import *
import time


#------------------------------------------------------------
spi = SPI()
orion = ORION_8G_12G(spi)

#-------------------------------------------------------------
""" Enable Detector Register : orion.TR_CTRL_2.det_en_force_val = DET_EN_CODE
    DET_EN_CODE : DETAILS
    0x1         : DET0 ON
    0x2         : DET1 ON
    0x4         : DET2 ON
    0x8         : DET3 ON 
    0xF         : ALL DET ON  
"""

orion.TR_CTRL_2.det_en_force = 0xF
orion.TR_CTRL_2.det_en_force_val = 0xF
orion.TR_CTRL_2.write()

spi.tr_reset()
time.sleep(0.5)
spi.tr_set()
time.sleep(0.5)

flash_adc_output_DET0 = (orion.DET_0_1_ADC_OUT_BIN.read() & 0x7)
flash_adc_output_DET1 = ((orion.DET_0_1_ADC_OUT_BIN.read() & 0x38) >> 3)
flash_adc_output_DET2 = (orion.DET_2_3_ADC_OUT_BIN.read() & 0x7)
flash_adc_output_DET3 = ((orion.DET_2_3_ADC_OUT_BIN.read() & 0x38) >> 3)

print('Flash ADC Output DET0:', flash_adc_output_DET0)
print('Flash ADC Output DET1:', flash_adc_output_DET1)
print('Flash ADC Output DET2:', flash_adc_output_DET2)
print('Flash ADC Output DET3:', flash_adc_output_DET3)

spi.close()      