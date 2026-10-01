version = 'v2'
ant_sel = 0x8 # Antenna selection for TX0: 0x1, TX1: 0x2, TX2: 0x4, TX3: 0x8
p_idx = 4   # 4...124
g_idx = 0  # Use g_idx=0 for 0dB attenuation, g_idx=53 for 16dB attenuation

import sys
sys.path.append('../../include')
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *

# Orion Setup
spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
orion_hal.init_tx('MAX')
orion_hal.set_tr_mask(tx_mask=ant_sel)
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

orion_hal.set_iq_val(255, 0, 2047, ant_sel)
orion_hal.stg2_load()

spi.close()