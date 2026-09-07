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

orion_csr.DEVICE_ID.read()
print('device_id = '+hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = '+hex(orion_csr.REVISION.major_rev))
print('minor_revision = '+hex(orion_csr.REVISION.minor_rev))

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
orion_hal.init_tx('MAX')
orion_hal.set_tr_mask(tx_mask=0x1)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

orion_hal.init_beam_lut()

orion_csr.BEAM_CFG.use_beam_lut = 1
orion_csr.BEAM_CFG.tx_beam_seq_en = 1
orion_csr.BEAM_CFG.rx_beam_seq_en = 1
orion_csr.BEAM_CFG.write()

orion_csr.RX_BEAM_START_ADDR.rx_beam_start_addr = 0
orion_csr.RX_BEAM_START_ADDR.write()
orion_csr.RX_BEAM_STOP_ADDR.rx_beam_stop_addr = 127
orion_csr.RX_BEAM_STOP_ADDR.write()
orion_csr.TX_BEAM_START_ADDR.tx_beam_start_addr = 0
orion_csr.TX_BEAM_START_ADDR.write()
orion_csr.TX_BEAM_STOP_ADDR.tx_beam_stop_addr = 127
orion_csr.TX_BEAM_STOP_ADDR.write()

orion_csr.BEAM_CFG.beam_cfg_done = 1
orion_csr.BEAM_CFG.write()

for _ in range(16):
    orion_hal.stg2_load()
    input()

# orion_csr.TX0_STS_REG.read()
# print('tx0_iphase_ctrl = '+hex(orion_csr.TX0_STS_REG.TX0_iphase_ctrl))
#
# orion_csr.TX0_STS_REG_1.read()
# print('tx0_qphase_ctrl = '+hex(orion_csr.TX0_STS_REG_1.TX0_qphase_ctrl))
#
# orion_csr.TX0_STS_REG_2.read()
# print('tx0_sign_i = '+hex(orion_csr.TX0_STS_REG_2.TX0_sign_i))
# print('tx0_sign_q = '+hex(orion_csr.TX0_STS_REG_2.TX0_sign_q))
#
# orion_csr.TX0_STS_REG_3.read()
# print('tx0_gain_ctrl_lsb = '+hex(orion_csr.TX0_STS_REG_3.TX0_gain_ctrl_lsb))
#
# orion_csr.TX0_STS_REG_4.read()
# print('tx0_gain_ctrl_msb = '+hex(orion_csr.TX0_STS_REG_4.TX0_gain_ctrl_msb))
# print('tx0_final_gain_ctrl = '+hex(orion_csr.TX0_STS_REG_4.TX0_final_gain_ctrl))

spi.close()