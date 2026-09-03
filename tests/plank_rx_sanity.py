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

lna_dac_values = {
    0x00: {
        'LNA0': 15,
        'LNA1': 15,
        'LNA2': 15,
        'LNA3': 15
    },
    0x01: {
        'LNA0': 15,
        'LNA1': 15,
        'LNA2': 15,
        'LNA3': 15
    }
}
mode = 'Cumulative' #Option: Single or Cumulative
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
    name: ORION_8G_12G_hal(dev, devices_lut[f'orion_lut{i}'],spi,version)
    for i, (name, dev) in enumerate(devices.items())
}
hal_bdst = ORION_8G_12G_hal(orion_bdst,orion_lut_bdst,spi,version)

# Write DACs and reset TR configs via broadcast
hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)

if (mode=='Single'):
    print("Turning ON one channel at a time")
else:
    print("Cumulatively turning ON one channel at a time")

for (name,hal), addr in zip(hal_devs.items(), dev_addr):
    hal_bdst.en_data_path(0)
    hal.set_tr_mode('EXT_TR')
    hal.set_trx_mode(0)
    hal.en_data_path(1)
    hal.init_rx('NOM')
        
    rx_channels = rf_ch_list[addr]
    rx_enable = [1 << ch for ch in rx_channels]
    lna_channels = bias_ch_list[addr]
    lna_keys = [f'LNA{ch}' for ch in lna_channels]  # Dynamically mapped
    dac_values = lna_dac_values[addr]
    cumulative_rx_en = 0
   
    if (mode=='Single'):         
        print(f"Turning ON channels for {name}")
    else:
        print(f"Cumulatively turning ON channels for {name}")
    
    for rx_en, lna_key in zip(rx_enable, lna_keys):
        if mode == 'Single':
            current_rx_mask = rx_en
        else:
            cumulative_rx_en |= rx_en
            current_rx_mask = cumulative_rx_en 
        hal.set_iq_val(I=218, Q=2, Av=1748, ant_sel=current_rx_mask)
        hal.set_tr_mask(rx_mask=current_rx_mask)
        
        if (mode=='Single'):
            hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF) #Setting all DACs to 127
    
        # Set current LNA
        hal.dac_cfg(pa_sel=0, lna_sel=rx_en, **{lna_key: dac_values[lna_key]})
        
        input(f"⏸️ Press Enter to continue after checking {name} - {lna_key}...")
                
# Setting data path and tx and rx mask to 0 for safety    
hal_bdst.en_data_path(0)
hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)

spi.close()
