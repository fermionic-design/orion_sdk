# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 09:52:56 2023

@author: subhajit

TB name: 
Current from VDD2p7: 
"""
import sys
import time
sys.path.append('../include')
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC

import time
import numpy as np
from ORION_8G_12G import *
from SPI import *
import csv

#--------------------------------Basic SETUP------------------------------
# setup multimeter fot measurement
import pyvisa
rm = pyvisa.ResourceManager()
print('\nInstruments Available: ',rm.list_resources())
my_meter = rm.open_resource('USB0::0x1AB1::0x0C94::DM3O272300791::INSTR')
# print('Multimeter: ',my_meter.query('*IDN?'))

# setup xlsx for write
# import xlsxwriter as xlsw
# out_xls = xlsw.Workbook('../results/LNA0_BIAS_SWEEP_RESULT.xlsx')
# out_sheet = out_xls.add_worksheet()
# out_sheet.write('A1','DAC Code')
# out_sheet.write('B1','LNA0 Voltage')

#--------------------------Generate Table------------------ 
blank_col=[""]
file = open("C:/Users/silic/OneDrive/Documents/GitHub/orion/results/bench_char/SOL_M2/CHIP_M2_LNA0_BIAS_SWEEP_85C_day1.csv","w",newline="")
writer = csv.writer(file)

header_row = ["DAC Code", "M2_LNA0 Voltage"]
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
# Enable LNA0 Bias
RF_CTRL_FUNC.set_enable_LNA_bias(orion, 0x1)

# sweep DAC input code and measure output
i=0
for i in range(0,256,1):
    # RF_CTRL_FUNC.set_LNA3_bias(orion, i)
    # RF_CTRL_FUNC.set_LNA2_bias(orion, i)
    # RF_CTRL_FUNC.set_LNA1_bias(orion, i)
    RF_CTRL_FUNC.set_LNA0_bias(orion, i)
    """
    Measure GP7 voltage at this point
    """
    time.sleep(1)
    v_meas=float(my_meter.query(':MEAS:VOLT:DC?'))
    print("measured voltage at LNA0 pin: ",v_meas)
    time.sleep(1)
    row_content= [i] + [v_meas]
    writer.writerow(row_content)

# close all
file.close()
spi.close()
