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

spi.cfg_logging(log_en=0)

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

orion_hal.set_lut_idx(p_idx,g_idx,ant_sel)
orion_hal.stg2_load()

# Readback of the active TX0 phase/gain registers
orion_csr.TX0_I_LSB.read()
orion_csr.TX0_Q_LSB.read()
orion_csr.TX0_AV_LSB.read()
orion_csr.TX0_MSB.read()
orion_csr.TX0_FINAL_AV.read()

print('tx0_i_lsb = ' + str(orion_csr.TX0_I_LSB.tx0_i_lsb))
print('tx0_q_lsb = ' + str(orion_csr.TX0_Q_LSB.tx0_q_lsb))
print('tx0_av_lsb = ' + str(orion_csr.TX0_AV_LSB.tx0_av_lsb))
print('tx0_i_msb = ' + str(orion_csr.TX0_MSB.tx0_i_msb))
print('tx0_q_msb = ' + str(orion_csr.TX0_MSB.tx0_q_msb))
print('tx0_av_msb = ' + str(orion_csr.TX0_MSB.tx0_av_msb))
print('tx0_final_av = ' + str(orion_csr.TX0_FINAL_AV.tx0_final_av))

tx0_i = (orion_csr.TX0_MSB.tx0_i_msb << 8) | orion_csr.TX0_I_LSB.tx0_i_lsb
tx0_q = (orion_csr.TX0_MSB.tx0_q_msb << 8) | orion_csr.TX0_Q_LSB.tx0_q_lsb
tx0_av = (orion_csr.TX0_MSB.tx0_av_msb << 8) | orion_csr.TX0_AV_LSB.tx0_av_lsb
print(f'TX0: I = {tx0_i}, Q = {tx0_q}, AV = {tx0_av}, FINAL_AV = {orion_csr.TX0_FINAL_AV.tx0_final_av}')


# for p_idx in range(121):
#     print(f'p_idx = {p_idx+4}')
#     orion_hal.set_lut_idx(p_idx+4,g_idx,ant_sel)
#     orion_hal.stg2_load()
#     time.sleep(0.5)

orion_hal.set_lut_idx(4,0,ant_sel)
orion_hal.stg2_load()

input()

orion_hal.set_lut_idx(4,20,ant_sel)
orion_hal.stg2_load()

input()

orion_hal.set_lut_idx(4,0,ant_sel)
orion_hal.stg2_load()

spi.close()

