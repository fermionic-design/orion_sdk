from include.ORION_8G_12G import FREQ_ID, TEMP_CORR_CFG

version = 'v2'
import sys
sys.path.append('../../include')

# from libs.fd_cmn.instruments.instruments import instruments
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

spi.cfg_logging(log_en=0)

orion_csr.DEVICE_ID.read()
print('device_id = '+hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = '+hex(orion_csr.REVISION.major_rev))
print('minor_revision = '+hex(orion_csr.REVISION.minor_rev))

orion_hal.set_tr_mode('INT_TR')
#orion_hal.set_trx_mode(1)
orion_hal.set_trx_mode(0)
#orion_hal.init_tx('MAX')
orion_hal.init_rx('NOM')
#orion_hal.set_tr_mask(tx_mask=0x1)
orion_hal.set_tr_mask(rx_mask=0x1)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

#orion_hal.init_rx_lut_ate()
orion_hal.init_rx_temp_comp_lut_ate()

spi.cfg_logging(log_en=0)

#for _ in range(11):
orion_hal.set_lut_idx(0,0,ant_sel=0x1)
orion_hal.stg2_load()
# input()
NUM_FREQ = 2
NUM_TEMP = 4

for f in range(NUM_FREQ):
    for t in range(NUM_TEMP):
        print("Freq idx="+str(f)+"; Temp idx="+str(t)+";")
        orion_csr.FREQ_ID.freq_id=f
        orion_csr.FREQ_ID.write()
        orion_csr.RSVD2.write()
        orion_csr.RSVD3.write()
        orion_hal.stg2_load()
        orion_csr.TEMP_CORR_CFG.force_ana_temp=0x1
        orion_csr.TEMP_CORR_CFG.force_ana_temp_val = t
        orion_csr.TEMP_CORR_CFG.en_rx_temp_corr = 1
        orion_csr.TEMP_CORR_CFG.write()
        #read rx gain and phase values from VNA
        #expected gain shift = 0dB, expected phase shift = 45deg
        input()

spi.close()