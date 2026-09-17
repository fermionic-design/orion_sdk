version = 'v2'
ant_sel = 0x8  # Antenna selection for RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8

import sys
sys.path.append('../../include')
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import time

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('NOM')
orion_hal.set_tr_mask(rx_mask=ant_sel)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(0)
orion_hal.en_data_path(1)

orion_hal.set_iq_val(0,255,2047,ant_sel)
orion_hal.stg2_load()

spi.close()