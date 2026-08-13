version = 'v2'
import sys
import time

sys.path.append('../include')

from ORION_8G_12G import *
from SPI import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *

### ----- Initialize SPI and Devices -----
spi = SPI()

# Broadcast device
orion_bdst = ORION_8G_12G(spi, 0, 1)
orion_lut_bdst = ORION_8G_12G_lut(spi)
###############################################################
device_count = 0x20  # Scans from 0x00 to 0x1F (32 addresses)
dev_addr = []

print("Scanning for ORION devices at hex addresses 0x00 to 0x1F...")

for addr in range(0x00, device_count):
    try:
        dev = ORION_8G_12G(spi, addr, 0)
        dev.DEVICE_ID.read()
        device_id = dev.DEVICE_ID.device_id
        dev.REVISION.read()
        major = dev.REVISION.major_rev
        minor = dev.REVISION.minor_rev
        
        if device_id == 0xF2 and major == 1 and minor == 1:
            print(f"Device found at address 0x{addr:02X}: ID=0x{device_id:02X}, Rev={major}.{minor}")
            dev_addr.append(addr)
    except Exception:
        pass  # Ignore errors if no device responds

print("\nSummary:")
print(f"Total Devices Detected: {len(dev_addr)}")
print("dev_addr =", [f"0x{addr:02X}" for addr in dev_addr])

print('\n')
###############################################################

devices = {f'orion_dev{i}': ORION_8G_12G(spi, addr, 0) for i, addr in enumerate(dev_addr)}
hal_devs = {name: ORION_8G_12G_hal(dev, ORION_8G_12G_lut(spi), spi,version) for name, dev in devices.items()}
hal_bdst = ORION_8G_12G_hal(orion_bdst,orion_lut_bdst,spi,version)

### ----- Functions -----

def broadcast_phase_code(value):
    orion_bdst.PHASE_CODE_TX0.phase_code_tx0 = value
    orion_bdst.PHASE_CODE_TX0.write()
    print(f"✅ Broadcast: PHASE_CODE_TX0 set to {hex(value)} on all devices")

def read_phase_code_all(devices):
    for name, dev in devices.items():
        dev.PHASE_CODE_TX0.read()
        print(f'{name}: phase_code_tx0 = {hex(dev.PHASE_CODE_TX0.phase_code_tx0)}')

def write_phase_code_individual(devices, code_map):
    for name, value in code_map.items():
        devices[name].PHASE_CODE_TX0.phase_code_tx0 = value
        devices[name].PHASE_CODE_TX0.write()
        print(f'{name}: PHASE_CODE_TX0 individually set to {hex(value)}')

### ----- Main Execution -----

# Broadcast phase code to all devices    
broadcast_phase_code(0x3B)

# Read phase code from all devices
read_phase_code_all(devices)

# Unicast phase code to all devices 
individual_phase_codes = {f'orion_dev{i}': 0x20 + i for i in range(len(dev_addr))}
write_phase_code_individual(devices, individual_phase_codes)

# Read phase code from all devices
read_phase_code_all(devices)

# Write DACs and reset TR configs via broadcast
hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)

# Setting data path and tx and rx mask to 0 for safety
hal_bdst.en_data_path(0)
hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)



spi.close()
