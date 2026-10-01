version = 'v2'
adc_input = 'gp7' # sar adc input can be gp4/gp5/gp6/gp7

import sys
sys.path.append('../../include')
from ORION_8G_12G import *
from SPI import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

orion_hal.sel_adc_input(adc_input)
orion_hal.enable_adc(1)
orion_hal.read_adc_eoc()
orion_hal.read_adc_output()
orion_hal.enable_adc(0)

orion_hal.enable_adc(1)
orion_hal.read_adc_eoc()
adc_val = orion_hal.read_adc_output()
orion_hal.enable_adc(0)
print(f"SAR ADC OUTPUT: {adc_val}")
spi.close()

