import sys
import serial


sys.path.append('../include')

from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from SPI import *
    
spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))

orion.PHASE_CODE_TX0.read()
print('phase_code_tx0 = '+hex(orion.PHASE_CODE_TX0.phase_code_tx0))

orion.PHASE_CODE_TX0.phase_code_tx0 = 0x5A
orion.PHASE_CODE_TX0.write()
orion.PHASE_CODE_TX0.read()
print('phase_code_tx0 = '+hex(orion.PHASE_CODE_TX0.phase_code_tx0))

# #write to page id
# orion.PAGE_ID.page_id = 0x00
# orion.PAGE_ID.write()
# orion.PAGE_ID.read()
# print('page_id = '+hex(orion.PAGE_ID.page_id))

# #write to LUT
# orion_lut.RX_PHASE_MEM.pos = 0;
# orion_lut.RX_PHASE_MEM.rx_freq_val = 0
# orion_lut.RX_PHASE_MEM.rx_temp_val = 0
# orion_lut.RX_PHASE_MEM.rx_phase_val_i = 0
# orion_lut.RX_PHASE_MEM.rx_phase_val_q = 0
# orion_lut.RX_PHASE_MEM.rx_gain_err = 0
# orion_lut.RX_PHASE_MEM.write()
# orion_lut.RX_PHASE_MEM.read()

spi.close()
