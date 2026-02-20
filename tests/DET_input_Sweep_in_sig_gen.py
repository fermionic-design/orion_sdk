# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:38:51 2025

@author: anany

"""

"""
Setup: 
Vsup = 2.5-3.3V (nominal - 2.7V)
Connect the Signal Genrator, Multimeter to Laptop through USB
This code feeds input power from -20dBm to 16dBm through Signal generator to DETx port, and record the SAR ADC,
FLASH ADC and GP7 value(in multimeter) with and without RF.
DET_SEL=1 denotes RF+bias path, whereas DET_SEL=2 denotes only bias path. While testing a particular DET, 
other 3 DETs should be 50 ohm terminated and other RF ports need not be terminated.
Note: Flash ADC does not contain any RF path, so the flash code is same for with and without RF

"""

import sys

sys.path.append('../../include')

import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from SPI import *
import pandas as pd
import numpy as np
import xlsxwriter as xlsw
import pyvisa
import math
import time

#------------------------------------------------------------------------
spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))

#--------------------------------------------------------------

def get_sar_adc_value(myDevice):
    
    sar_adc_output=0
    
    RF_CTRL_FUNC.set_enable_adc(myDevice, 1)
    time.sleep(2)
    
    eoc_read=RF_CTRL_FUNC.read_adc_eoc(myDevice)

    # if eoc is 1 then read adc input and output
    if eoc_read==1:
        sar_adc_output=RF_CTRL_FUNC.read_adc_output(myDevice)
    else:
        print("EOC is 0, SAR ADC conversion not complete")

    RF_CTRL_FUNC.set_enable_adc(myDevice, 0)
    time.sleep(1)
    
    return sar_adc_output

#---------------------------SETUP VNA------------------------

rm = pyvisa.ResourceManager()
print('\nInstruments Available: ',rm.list_resources())
my_sgen = rm.open_resource('USB0::0x0957::0x1F01::MY62221375::0::INSTR') #Detects the Signal Generator address
print('RF Signal Gen: ',my_sgen.query('*IDN?'))
my_meter = rm.open_resource('USB0::0x1AB1::0x0C94::DM3O245002030::INSTR') #Detects the Multimeter address
print('Multimeter: ',my_meter.query('*IDN?'))


# Initialize xlsx for read
#######################################################################################################################
out_xls = xlsw.Workbook('../../results/DET/J2/DET0_Input_Power_Sweep_ADC_Result_J2_sig_gen.xlsx')#replace the file location with desired filename
#######################################################################################################################


out_sheet = out_xls.add_worksheet()
out_sheet.write(0,0,'Input Power')
out_sheet.write(0,1,'DET SEL_1')
out_sheet.write(0,21,'Input Power')
out_sheet.write(0,22,'DET SEL_2')

    
freq=8
for i in range(0,5,1):
    out_sheet.write(0,i+3,'SAR ADC_DET_SEL1 '+str(freq)+'GHz')
    out_sheet.write(0,i+9,'GP7 VOL_DET_SEL1_aft_pwr_set '+str(freq)+'GHz')

    ###############################################################
    #Based on the DET port number:0,1,2,3 - Enable the corr DETx line for Flash ADC
    out_sheet.write(0,i+15,'Flash ADC_DET_SEL1 '+str(freq)+'GHz '+'DET0')
    # out_sheet.write(0,i+15,'Flash ADC_DET_SEL1 '+str(freq)+'GHz '+'DET1')
    # out_sheet.write(0,i+15,'Flash ADC_DET_SEL1 '+str(freq)+'GHz '+'DET2')
    # out_sheet.write(0,i+15,'Flash ADC_DET_SEL1 '+str(freq)+'GHz '+'DET3')
    ###############################################################
    
    out_sheet.write(0,i+24,'SAR ADC_DET_SEL2 '+str(freq)+'GHz')
    out_sheet.write(0,i+30,'GP7 VOL_DET_SEL2_aft_pwr_set '+str(freq)+'GHz')

    ###############################################################
    #Based on the DET port number:0,1,2,3 - Enable the corr DETx line for Flash ADC
    out_sheet.write(0,i+36,'Flash ADC_DET_SEL2 '+str(freq)+'GHz '+'DET0')
    # out_sheet.write(0,i+36,'Flash ADC_DET_SEL2 '+str(freq)+'GHz '+'DET1')
    # out_sheet.write(0,i+36,'Flash ADC_DET_SEL2 '+str(freq)+'GHz '+'DET2')
    # out_sheet.write(0,i+36,'Flash ADC_DET_SEL2 '+str(freq)+'GHz '+'DET3')
    ###############################################################
    freq+=1
      

orion.REG0_ADC.en_pkdet_to_adc_sw = 0x1
orion.REG0_ADC.en_gp7_to_adc_sw = 0x1 
orion.REG0_ADC.write()

orion.POWER_DET_CFG.det0_sel = 0
orion.POWER_DET_CFG.det1_sel = 0
orion.POWER_DET_CFG.det2_sel = 0
orion.POWER_DET_CFG.det3_sel = 0
orion.POWER_DET_CFG.write()


orion.TR_CTRL_2.det_en_force = 0xF
orion.TR_CTRL_2.det_en_force_val = 0xF
orion.TR_CTRL_2.write()

#-----------------------------------------------------------------
xls_row=1
xls_row_s2=1

for det_sel_idx in range(2):
    
    det_sel=(0x1 << det_sel_idx)
    
    orion.POWER_DET_CFG.det0_sel=det_sel
    orion.POWER_DET_CFG.det1_sel=det_sel
    orion.POWER_DET_CFG.det2_sel=det_sel
    orion.POWER_DET_CFG.det3_sel=det_sel
    orion.POWER_DET_CFG.write()
    
    if (det_sel==1):
        k = 1
    elif (det_sel==2):
        k = 100
    for in_pwr_dBm in range(-20,17,k):
        
        my_sgen.write(f':SOUR:POW1 {in_pwr_dBm}') # Set input power
        time.sleep(1)
        
        for in_freq_GHz in range(8,13,1):
                                                      
            freq_idx=(in_freq_GHz-8)
            my_sgen.write(":FREQ "+str(freq_idx*1+8)+"e9")
            
            gp7_vol = float(my_meter.query(':MEAS:VOLT:DC?'))
            print(gp7_vol)
            
            spi.tr_reset()
            time.sleep(0.5)
            spi.tr_set()
            time.sleep(0.5)
        
            flash_adc_output_DET0 = (orion.DET_0_1_ADC_OUT_BIN.read() & 0x7)
            flash_adc_output_DET1 = ((orion.DET_0_1_ADC_OUT_BIN.read() & 0x38) >> 3)
            flash_adc_output_DET2 = (orion.DET_2_3_ADC_OUT_BIN.read() & 0x7)
            flash_adc_output_DET3 = ((orion.DET_2_3_ADC_OUT_BIN.read() & 0x38) >> 3)
            
            
            RF_CTRL_FUNC.set_enable_adc(orion, 0)
            time.sleep(1)
            RF_CTRL_FUNC.set_enable_adc(orion, 1)
            time.sleep(1)
            sar_adc_output=get_sar_adc_value(orion)
            

                                
            print('Input Power dBm: ', in_pwr_dBm)
            print('DET SEL: ', det_sel)
            print("SAR ADC Output:", sar_adc_output)
            print("GP7 voltage", gp7_vol)

            print('Flash ADC Output DET0:', flash_adc_output_DET0)
            print('Flash ADC Output DET1:', flash_adc_output_DET1)
            print('Flash ADC Output DET2:', flash_adc_output_DET2)
            print('Flash ADC Output DET3:', flash_adc_output_DET3)
                
  

            if(det_sel == 1):
                out_sheet.write(xls_row,0,in_pwr_dBm)
                out_sheet.write(xls_row,1,det_sel)
                 
                out_sheet.write(xls_row,(freq_idx+3),sar_adc_output)
                out_sheet.write(xls_row,(freq_idx+9),gp7_vol)

                ################################################################
                #Based on the DET port number:0,1,2,3 - Enable the corr DETx line for Flash ADC
                out_sheet.write(xls_row,(freq_idx+15),flash_adc_output_DET0)
                # out_sheet.write(xls_row,(freq_idx+15),flash_adc_output_DET1)
                # out_sheet.write(xls_row,(freq_idx+15),flash_adc_output_DET2) 
                # out_sheet.write(xls_row,(freq_idx+15),flash_adc_output_DET3)
                ###############################################################
            else:     
                out_sheet.write(xls_row_s2,21,in_pwr_dBm)
                out_sheet.write(xls_row_s2,22,det_sel)
                out_sheet.write(xls_row_s2,(freq_idx+24),sar_adc_output)
                out_sheet.write(xls_row_s2,(freq_idx+30),gp7_vol)

                ###############################################################
                #Based on the DET port number:0,1,2,3 - Enable the corr DETx line for Flash ADC
                out_sheet.write(xls_row_s2,(freq_idx+36),flash_adc_output_DET0)
                # out_sheet.write(xls_row_s2,(freq_idx+36),flash_adc_output_DET1)
                # out_sheet.write(xls_row_s2,(freq_idx+36),flash_adc_output_DET2) 
                # out_sheet.write(xls_row_s2,(freq_idx+36),flash_adc_output_DET3)
                ###############################################################  
               
        if det_sel == 1:
            xls_row+=1
        elif det_sel == 2:
            xls_row_s2+=1

#-----------------------------------------------------
orion.POWER_DET_CFG.det0_sel = 0
orion.POWER_DET_CFG.det1_sel = 0
orion.POWER_DET_CFG.det2_sel = 0
orion.POWER_DET_CFG.det3_sel = 0
orion.POWER_DET_CFG.write()

out_xls.close()
spi.close()