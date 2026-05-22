version = 'v2'
ant_sel = 0x1
p_idx = 4   # 4...124
g_idx = 0  # Use g_idx=0 for 0dB attenuation, g_idx=53 for 16dB attenuation

d1 = 1   # delay after setting IQ

import sys
sys.path.append('../../include')
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import time

# Orion Setup
spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)

orion_hal.init_lut_new(r'../../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                        r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__tx_phase_lut__freq_8p5__gm_0p5__pm_1p5__pm2_3__abs_gain_7p5__nom__vdd_2p7.xlsx',
                       # r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__tx_phase_lut__freq_9p5__gm_0p5__pm_1p5__pm2_3__abs_gain_6p5__low__vdd_2p5.xlsx',
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
orion_hal.set_lut_idx(p_idx,g_idx,ant_sel)
orion_hal.stg2_load()
time.sleep(d1)

spi.close()

