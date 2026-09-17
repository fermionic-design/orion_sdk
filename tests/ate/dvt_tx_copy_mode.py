version = 'v2'
ant_sel = 0x1 # Antenna selection for TX0: 0x1, TX1: 0x2, TX2: 0x4, TX3: 0x8
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

spi.cfg_logging(log_en=1)

orion_hal.init_lut_new(r'../../final_lut/v2__tx__gain_lut__8p5GHz__maxbias__vdd_2p7_at_i500_q4.xlsx',
                       r'../../final_lut/v2__tx_phase_lut__freq_8p5__gm_0p5__pm_1p5__pm2_3__abs_gain_7p5__nom__vdd_2p7.xlsx',
                       r'../../final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
                       r'../../final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
                       r'../../final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
                       r'../../final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx')

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
orion_hal.init_tx('MAX')
orion_hal.set_tr_mask(tx_mask=ant_sel)
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

spi.cfg_logging(log_en=0)

orion_csr.COPY_MODE.copy_mode = 0
orion_csr.COPY_MODE.write()

orion_hal.set_lut_idx(4,0,0xF)
orion_hal.stg2_load()

orion_hal.set_lut_idx(24,20,0x1)
orion_hal.stg2_load()

# Readback of the active TXn phase/gain registers, all 4 channels
for ch in range(4):
    i_lsb_reg = getattr(orion_csr, f'TX{ch}_I_LSB')
    q_lsb_reg = getattr(orion_csr, f'TX{ch}_Q_LSB')
    av_lsb_reg = getattr(orion_csr, f'TX{ch}_AV_LSB')
    msb_reg = getattr(orion_csr, f'TX{ch}_MSB')
    final_av_reg = getattr(orion_csr, f'TX{ch}_FINAL_AV')

    i_lsb_reg.read()
    q_lsb_reg.read()
    av_lsb_reg.read()
    msb_reg.read()
    final_av_reg.read()

    i_lsb = getattr(i_lsb_reg, f'tx{ch}_i_lsb')
    q_lsb = getattr(q_lsb_reg, f'tx{ch}_q_lsb')
    av_lsb = getattr(av_lsb_reg, f'tx{ch}_av_lsb')
    i_msb = getattr(msb_reg, f'tx{ch}_i_msb')
    q_msb = getattr(msb_reg, f'tx{ch}_q_msb')
    av_msb = getattr(msb_reg, f'tx{ch}_av_msb')
    final_av = getattr(final_av_reg, f'tx{ch}_final_av')

    tx_i = (i_msb << 8) | i_lsb
    tx_q = (q_msb << 8) | q_lsb
    tx_av = (av_msb << 8) | av_lsb
    print(f'TX{ch}: I = {tx_i}, Q = {tx_q}, AV = {tx_av}, FINAL_AV = {final_av}')


# for p_idx in range(121):
#     print(f'p_idx = {p_idx+4}')
#     orion_hal.set_lut_idx(p_idx+4,g_idx,ant_sel)
#     orion_hal.stg2_load()
#     time.sleep(0.5)

spi.close()

