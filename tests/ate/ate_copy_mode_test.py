version = 'v2'
import sys
sys.path.append('../../include')

# from libs.fd_cmn.instruments.instruments import instruments
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *

spi = SPI(log_en=0)
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

orion_csr.DEVICE_ID.read()
print('device_id = '+hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = '+hex(orion_csr.REVISION.major_rev))
print('minor_revision = '+hex(orion_csr.REVISION.minor_rev))

# LUT Programming
# TODO(abhra): move these to a common place
NUM_FREQ = 2
NUM_TEMP = 4
RX_GAIN_LUT_DEPTH = 64
RX_PHASE_LUT_DEPTH = 128
NUM_BYTES_PER_PAGE = 256

NUM_BYTES_PER_RX_PHASE_UNIT = 4
NUM_BYTES_PER_RX_PHASE_CODE = NUM_BYTES_PER_RX_PHASE_UNIT * NUM_TEMP
NUM_RX_PHASE_CODES_PER_PAGE = int(NUM_BYTES_PER_PAGE / NUM_BYTES_PER_RX_PHASE_CODE)

NUM_BYTES_PER_RX_GAIN_UNIT = 4
NUM_BYTES_PER_RX_GAIN_CODE = NUM_BYTES_PER_RX_GAIN_UNIT * NUM_TEMP
NUM_RX_GAIN_CODES_PER_PAGE = int(NUM_BYTES_PER_PAGE / NUM_BYTES_PER_RX_GAIN_CODE)

RX_PHASE_LUT_START_PAGE = 0
RX_GAIN_LUT_START_PAGE = 16

for f in range(NUM_FREQ):
    for i in range(RX_PHASE_LUT_DEPTH):
        if i % NUM_RX_PHASE_CODES_PER_PAGE == 0:
            orion_csr.PAGE_ID.page_id = (RX_PHASE_LUT_START_PAGE +
                                              f * int(
                        NUM_BYTES_PER_RX_PHASE_CODE * RX_PHASE_LUT_DEPTH / NUM_BYTES_PER_PAGE) +
                                              int(i / NUM_RX_PHASE_CODES_PER_PAGE)
                                              )
            # print(f'page_id = {orion_csr.PAGE_ID.page_id}')
            orion_csr.PAGE_ID.write()
        for t in range(NUM_TEMP):
            # print(f'freq = {f}, code = {i}, temp = {t}')
            orion_lut.RX_PHASE_MEM.pos = i % NUM_RX_PHASE_CODES_PER_PAGE
            orion_lut.RX_PHASE_MEM.rx_temp_val = t
            iq_val = int(256/RX_PHASE_LUT_DEPTH*(RX_PHASE_LUT_DEPTH-i))-1
            # print(iq_val)
            orion_lut.RX_PHASE_MEM.rx_phase_val_i = iq_val
            orion_lut.RX_PHASE_MEM.rx_phase_val_q = iq_val
            orion_lut.RX_PHASE_MEM.rx_gain_err = 0
            orion_lut.RX_PHASE_MEM.write()

for f in range(NUM_FREQ):
    for i in range(RX_GAIN_LUT_DEPTH):
        if i % NUM_RX_GAIN_CODES_PER_PAGE == 0:
            orion_csr.PAGE_ID.page_id = (RX_GAIN_LUT_START_PAGE +
                                              f * int(
                        NUM_BYTES_PER_RX_GAIN_CODE * RX_GAIN_LUT_DEPTH / NUM_BYTES_PER_PAGE) +
                                              int(i / NUM_RX_GAIN_CODES_PER_PAGE))
            # print(f'page_id = {orion_csr.PAGE_ID.page_id}')
            orion_csr.PAGE_ID.write()
        for t in range(NUM_TEMP):
            # print(f'freq = {f}, code = {i}, temp={t}')
            orion_lut.RX_GAIN_MEM.pos = i % NUM_RX_GAIN_CODES_PER_PAGE
            orion_lut.RX_GAIN_MEM.rx_temp_val = t
            orion_lut.RX_GAIN_MEM.rx_gain_val = int(2048/RX_GAIN_LUT_DEPTH*(RX_GAIN_LUT_DEPTH-i))-1
            # print(int(2048/RX_GAIN_LUT_DEPTH*(RX_GAIN_LUT_DEPTH-i))-1)
            orion_lut.RX_GAIN_MEM.rx_ph_err = 2
            orion_lut.RX_GAIN_MEM.write()

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('NOM')
orion_hal.set_tr_mask(rx_mask=0x1)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)
orion_hal.enable_rx_correction(0)

orion_csr.COPY_MODE.copy_mode = 1
orion_csr.COPY_MODE.write()



orion_hal.set_lut_idx(124, 63, 0xF)
orion_hal.stg2_load()

orion_hal.set_lut_idx(4, 0, 0x1)
# orion_hal.set_lut_idx(0, 1, 0x2)
# orion_hal.set_lut_idx(0, 2, 0x4)
# orion_hal.set_lut_idx(0, 3, 0x8)

orion_hal.stg2_load()

# Readback of the active RXn TEMP0 phase/gain registers, all 4 channels
for ch in range(4):
    i_lsb_reg = getattr(orion_csr, f'RX{ch}_I_LSB_TEMP0')
    q_lsb_reg = getattr(orion_csr, f'RX{ch}_Q_LSB_TEMP0')
    av_lsb_reg = getattr(orion_csr, f'RX{ch}_AV_LSB_TEMP0')
    msb_reg = getattr(orion_csr, f'RX{ch}_MSB_TEMP0')

    i_lsb_reg.read()
    q_lsb_reg.read()
    av_lsb_reg.read()
    msb_reg.read()

    i_lsb = getattr(i_lsb_reg, f'rx{ch}_i_lsb_temp0')
    q_lsb = getattr(q_lsb_reg, f'rx{ch}_q_lsb_temp0')
    av_lsb = getattr(av_lsb_reg, f'rx{ch}_av_lsb_temp0')
    i_msb = getattr(msb_reg, f'rx{ch}_i_msb_temp0')
    q_msb = getattr(msb_reg, f'rx{ch}_q_msb_temp0')
    av_msb = getattr(msb_reg, f'rx{ch}_av_msb_temp0')

    rx_i_temp0 = (i_msb << 8) | i_lsb
    rx_q_temp0 = (q_msb << 8) | q_lsb
    rx_av_temp0 = (av_msb << 8) | av_lsb
    print(f'RX{ch} TEMP0: I = {rx_i_temp0}, Q = {rx_q_temp0}, AV = {rx_av_temp0}')

spi.close()
