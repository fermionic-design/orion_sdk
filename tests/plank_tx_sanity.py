import sys
import time

sys.path.append('../include')

from ORION_8G_12G import *
from SPI import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
############### User Settings ##############################################
version = 'v2'
dev_addr = [0x00, 0x01]

rf_ch_list = {
    0x00: [0,1,2,3],
    0x01: [0,1,2,3]
}

bias_ch_list = {
    0x00: [0,1,2,3],
    0x01: [0,1,2,3]
}

pa_dac_values = {
    0x00: {
        'PA0': 87,
        'PA1': 87,
        'PA2': 88,
        'PA3': 82
    },
    0x01: {
        'PA0': 80,
        'PA1': 80,
        'PA2': 80,
        'PA3': 80
    }
} 
############## END: User Settings - do NOT Modify anything after this ######

spi = SPI()
orion_bdst = ORION_8G_12G(spi, 0, 1)
orion_lut_bdst = ORION_8G_12G_lut(orion_bdst,0,1)

devices = {f'orion_dev{i}': ORION_8G_12G(spi, addr, 0) for i, addr in enumerate(dev_addr)}
devices_lut = {
    f'orion_lut{i}': ORION_8G_12G_lut(devices[f'orion_dev{i}'], addr, 0)
    for i, addr in enumerate(dev_addr)
}
hal_devs = {
    name: ORION_8G_12G_hal(dev, devices_lut[f'orion_lut{i}'], spi, version)
    for i, (name, dev) in enumerate(devices.items())
}
hal_bdst = ORION_8G_12G_hal(orion_bdst,orion_lut_bdst,spi,version)

# Write DACs and reset TR configs via broadcast
hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)

print("Turning ON one channel at a time")

for (name,hal), addr in zip(hal_devs.items(), dev_addr):
    hal_bdst.en_data_path(0)
    hal.set_tr_mode('EXT_TR')
    hal.set_trx_mode(1)
    hal.en_data_path(1)
    spi.pa_set()
    hal.init_tx('5W_FEM')
        
    tx_channels = rf_ch_list[addr]
    tx_enable = [1 << ch for ch in tx_channels]
    pa_channels = bias_ch_list[addr]
    pa_keys = [f'PA{ch}' for ch in pa_channels]  # Dynamically mapped
    dac_values = pa_dac_values[addr]
            
    print(f"Turning ON channels for {name}")
    
    for tx_en, pa_key in zip(tx_enable, pa_keys):
        hal.set_iq_val(I=230, Q=257, Av=2047, ant_sel=tx_en)
        hal.set_tr_mask(tx_mask=tx_en)
    
        hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF) #Setting all DACs to 127
    
        # Set current PA
        hal.dac_cfg(pa_sel=tx_en, lna_sel=0, **{pa_key: dac_values[pa_key]})
        
        input(f"⏸️ Press Enter to continue after checking {name} - {pa_key}...")

        
# Setting data path and tx and rx mask to 0 for safety    
hal_bdst.en_data_path(0)
hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)

spi.close()
