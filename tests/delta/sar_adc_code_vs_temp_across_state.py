mode = 'idle' #idle/tx/rx

import sys
sys.path.append('../../include')
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr,orion_lut,spi,'v2')

orion_csr.DEVICE_ID.read()
print('device_id = ' + hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = ' + hex(orion_csr.REVISION.major_rev))
print('minor_revision = ' + hex(orion_csr.REVISION.minor_rev))

orion_hal.sel_adc_input("temp")

if mode == 'idle':
    orion_hal.send_temp_to_adc("ptat")
    orion_hal.enable_adc(1)
    if orion_hal.read_adc_eoc() == 1:
        ptat = orion_hal.read_adc_output()
        print("PTAT SAR ADC Output:", ptat)
        orion_hal.enable_adc(0)

    orion_hal.send_temp_to_adc("ztat")
    orion_hal.enable_adc(1)
    if orion_hal.read_adc_eoc() == 1:
        ztat = orion_hal.read_adc_output()
        print("ZTAT SAR ADC Output:", ztat)
        orion_hal.enable_adc(0)

    print("PTAT - ZTAT =", ptat - ztat)

if mode == 'tx':
    orion_hal.set_tr_mode('INT_TR')
    orion_hal.set_trx_mode(1)
    orion_hal.init_tx('MAX')
    orion_hal.set_tr_mask(tx_mask=0x1)
    orion_hal.cfg_stg2_load('REG')
    orion_hal.en_data_path(1)

    orion_hal.send_temp_to_adc("ptat")
    orion_hal.enable_adc(1)
    if orion_hal.read_adc_eoc() == 1:
        ptat = orion_hal.read_adc_output()
        print("PTAT SAR ADC Output:", ptat)
        orion_hal.enable_adc(0)

    orion_hal.send_temp_to_adc("ztat")
    orion_hal.enable_adc(1)
    if orion_hal.read_adc_eoc() == 1:
        ztat = orion_hal.read_adc_output()
        print("ZTAT SAR ADC Output:", ztat)
        orion_hal.enable_adc(0)

    print("PTAT - ZTAT =", ptat - ztat)

if mode == 'rx':
    orion_hal.set_tr_mode('INT_TR')
    orion_hal.set_trx_mode(0)
    orion_hal.init_rx('NOM')
    orion_hal.set_tr_mask(rx_mask=0x1)
    orion_hal.set_freq('9G')
    orion_hal.cfg_stg2_load('REG')
    orion_hal.en_data_path(1)

    orion_hal.send_temp_to_adc("ptat")
    orion_hal.enable_adc(1)
    if orion_hal.read_adc_eoc() == 1:
        ptat = orion_hal.read_adc_output()
        print("PTAT SAR ADC Output:", ptat)
        orion_hal.enable_adc(0)

    orion_hal.send_temp_to_adc("ztat")
    orion_hal.enable_adc(1)
    if orion_hal.read_adc_eoc() == 1:
        ztat = orion_hal.read_adc_output()
        print("ZTAT SAR ADC Output:", ztat)
        orion_hal.enable_adc(0)

    print("PTAT - ZTAT =", ptat - ztat)
spi.close()