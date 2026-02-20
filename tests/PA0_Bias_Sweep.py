# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 09:52:56 2023

@author: subhajit

TB name: 
Current from VDD2p7: 
"""
import sys

sys.path.append('../include')
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from SPI import *
import numpy as np
import pyvisa
import time
import csv



#--------------------------------Basic SETUP------------------------------
# setup multimeter fot measurement
rm = pyvisa.ResourceManager()
print('\nInstruments Available: ',rm.list_resources())
my_meter = rm.open_resource('USB0::0x1AB1::0x0C94::DM3O272300791::INSTR')
# print('Multimeter: ',my_meter.query('*IDN?'))



#--------------------------Generate Table------------------ 
blank_col=[""]
file = open("C:/Users/silic/OneDrive/Documents/GitHub/orion/results/bench_char/SOL_M2/CHIP_M2_PA0_BIAS_SWEEP_85C_day1.csv","w",newline="")
writer = csv.writer(file)

header_row = ["DAC Code", "M2_PA0 Voltage"]
writer.writerow(header_row)


#----------------------------SETUP SPI-----------------------------    
spi = SPI()
orion = ORION_8G_12G(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))


#---------------------------MAIN CODE-----------------------
# Enable PA0 Bias
RF_CTRL_FUNC.set_enable_PA_bias(orion, 0x1)

# sweep DAC input code and measure output
i=0
for i in range(0,256,1):
    RF_CTRL_FUNC.set_PA0_bias(orion, i)
    # RF_CTRL_FUNC.set_PA1_bias(orion, i)
    # RF_CTRL_FUNC.set_PA2_bias(orion, i)
    # RF_CTRL_FUNC.set_PA3_bias(orion, i)
    time.sleep(1)
    v_meas = float(my_meter.query(':MEAS:VOLT:DC?'))
    print("measured voltage at PA0 pin: ",v_meas)
    time.sleep(1)

    
    row_content= [i] + [v_meas]
    writer.writerow(row_content)
    # time.sleep(1)

# close all
file.close()
spi.close()
