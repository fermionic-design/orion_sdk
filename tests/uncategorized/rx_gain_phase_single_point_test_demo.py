# -- coding: utf-8 --
"""
Created on Thu Apr 17 19:09:41 2025

@author: silic
"""
version = 'v2'
ant_sel = 0x1 # Antenna selection for RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8
mode = "dual_lut" # single_lut, dual_lut

p_idx = 4   # 4...124
g_idx = 0   # 0...63

d1 = 0.1   # delay after setting IQ

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
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,version)    

orion_hal.init_lut_new(r'../../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                       r'../../final_lut/tx_v2__phase_lut_freq_14p25_gm_0p5_pm_1p5_pm2_4_abs_gain_8__maxbias__vdd_2p7.xlsx',
                       r'../../final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
                       r'../../final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
                       r'../../final_lut/v2__rx2__gain_lut__9p5GHz__lowbias_00__vdd_2p7_with_avg_for_dual_lut.xlsx',
                       r'../../final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_15__lowbias_00__vdd_2p5.xlsx')

                       
orion_csr.DEVICE_ID.read()
print('device_id = '+hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = '+hex(orion_csr.REVISION.major_rev))
print('minor_revision = '+hex(orion_csr.REVISION.minor_rev))

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('NOM')
orion_hal.set_tr_mask(rx_mask=0xF)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)
if mode == "dual_lut":
    if g_idx <= 31:
        orion_hal.set_freq('9G')
        orion_hal.init_rx('NOM')
    else:
        orion_hal.set_freq('11G')
        orion_hal.init_rx('LOW')
else:
    orion_hal.set_freq('9G')
    orion_hal.init_rx('NOM')

orion_hal.set_lut_idx(p_idx,g_idx,0xF)
orion_hal.stg2_load()
time.sleep(d1)

spi.close()