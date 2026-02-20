# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 14:44:04 2023

@author: silic
"""
# need to modify for LUT loading
version = 'v2'
chip_id = 'AB38'
ant_sel = 0x1         # Tx0=0x1, Tx1=0x2, Tx2=0x4, Tx3=0x8
param = 'psat'
log_path = f'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/bench_char/AB38'

i_code_list = [254]
q_code_list = [1]
d1 = 0.1    # delay after bfm

import sys
sys.path.append('../include')
sys.path.append('.\\..\\..\\include')
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from SPI import *
from ORION_8G_12G_hal import *
import xlsxwriter as xlsw
import pyvisa
import time
import datetime
ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()
#------------------------------------------------------------------------
spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion,orion_lut,spi,version)

#---------------------------SETUP Instrument------------------------
rm = pyvisa.ResourceManager()
print('\nInstruments Available: ',rm.list_resources())

my_sgen = rm.open_resource('USB0::0x0957::0x1F01::MY62221375::INSTR')
my_pm = rm.open_resource('USB0::0x2A8D::0x1301::MY64320008::INSTR')
print('Power meter: ',my_pm.query('*IDN?'))
print('RF Signal Gen: ',my_sgen.query('*IDN?'))

# ------------Sig Gen Setup--------------
in_pwr_dBm= [8]
my_sgen.write(f':POW {in_pwr_dBm[0]}')
my_sgen.write(':FREQ 10 GHz')
time.sleep(2)

# ------------Power meter Setup------------
my_pm.write(':SYST:PRES DEF')
my_pm.write(':CAL1:ZERO:AUTO ON')
my_pm.write(':CAL1:ZERO:AUTO ONCE')
time.sleep(15)

#-----------------------------------------------------------------------------
# Initialize xlsx for read
file_path = f'{log_path}/tx__{param}__{version}__{chip_id}__ant_sel_{ant_sel}__{ts}.xlsx'
out_xls = xlsw.Workbook(file_path)

out_sheet = out_xls.add_worksheet()
out_sheet.write(0,0,'Gain Code')
out_sheet.write(0,1,'I-Code')
out_sheet.write(0,2,'Q-Code')
out_sheet.write(0,3,'Src Power dBm')

freq = [7,7.25,7.5,7.75,8,8.25,8.5,8.75,9,9.25,9.5,9.75,10,10.25,10.5,10.75,11,11.25,11.5,11.75,12,12.25,12.5,12.75,13]
# freq = [9,10,11,11.5]
col1 = 0
for freq_idx in freq:
    out_sheet.write(0,col1+5,'Out Pwr dBm '+str(freq_idx)+'GHz')
    col1+=1

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(1)
orion_hal.init_tx('MAX')
orion_hal.set_tr_mask(tx_mask=ant_sel)
orion_hal.cfg_stg2_load('REG')
orion_hal.en_data_path(1)

xls_row = 1

# Sweep I/Q pair-wise: (254,1)
for i_code, q_code in zip(i_code_list, q_code_list):

    print("\n============================================")
    print(f"   Sweeping I={i_code}, Q={q_code}")
    print("============================================")

    # Program IQ values into ORION
    orion_hal.set_iq_val(I=i_code, Q=q_code, Av=2047, ant_sel=ant_sel)
    orion_hal.stg2_load()
    time.sleep(d1)

    for pwr in in_pwr_dBm:
        col = 0
        for freq_idx in freq:

            print('Phase: ', 0)
            print('Freq GHz: ', freq_idx)
            print('Inp Pow is:', pwr  )

            # set signal gen freq and power
            my_sgen.write(f":FREQ {freq_idx} GHz")
            my_sgen.write(":POW "+str(pwr))
            my_sgen.write(":OUTP ON")
            time.sleep(1)

           # set power meter freq and read power
            my_pm.write(f":SENS1:FREQ {freq_idx}e9")
            time.sleep(1)
            out_pwr_dBm = float(my_pm.query("FETCH?"))  # Read measured power in dBm
            print("Out pwr in dBm:", out_pwr_dBm)

            out_sheet.write(xls_row, 0, 2047)
            out_sheet.write(xls_row, 1, i_code)
            out_sheet.write(xls_row, 2, q_code)
            out_sheet.write(xls_row, 3, pwr)
            out_sheet.write(xls_row, 5+col, out_pwr_dBm)
            col+=1
        xls_row+=1
    
#------------------------------------------------------------------------------ 
end_time = time.time()
print(f'Runtime: {end_time - start_time:.2f} seconds')
print(f"\nData Dump File: {file_path}")
my_sgen.write(':OUTP OFF')
out_xls.close()
spi.close()