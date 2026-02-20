# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 17:34:30 2023

@author: subhajit
"""


import sys
import time
sys.path.append('../include')
sys.path.append('../../include')
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from SPI import *
import pandas as pd
import math
import pyvisa
import numpy as np


from ORION_8G_12G import *
from SPI import *
    
spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))

#--------------------------------------------------------------------------
RX_BIAS_MODE='NOM' # "NOM" for nominal bias mode or "LOW" for low bias mode 
RF_CTRL_FUNC.set_RX_bias_mode(orion, RX_BIAS_MODE)
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
TX_BIAS_MODE='NOM' # "NOM" for nominal bias mode or "LOW" for low bias mode
RF_CTRL_FUNC.set_TX_bias_mode(orion, TX_BIAS_MODE)
#--------------------------------------------------------------------------

def calc_phase_wrapped(input_phase):
    if (input_phase>=0) & (input_phase<180):
        return input_phase
    elif (input_phase>=180) & (input_phase<360):
        return (input_phase-360)
    elif (input_phase<0) & (input_phase>-180):
        return input_phase
    elif (input_phase<=-180) & (input_phase>-360):
        return (input_phase+360)   
    else:
        return -1000      # error 
    
"""Read XLS and Populate LUT"""
def read_column_from_excel(file_path, sheet_name, column_name):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Check if the specified column exists
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the Excel file.")

        # Extract the specified column
        selected_column = df[column_name]

        return selected_column

    except Exception as e:
        print(f"Error: {e}")
        
#---------------------------------Populating RX LUT--------------------------------------------
        
file_path = r'RX_Phase_LUT_9GHz_NomBias_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'I-Code'  # Specify the user-defined column name
i_code = read_column_from_excel(file_path, sheet_name, column_name)
i_code = i_code.astype(int)
column_name = 'Q-Code'  # Specify the user-defined column name
q_code = read_column_from_excel(file_path, sheet_name, column_name)
q_code = q_code.astype(int)
column_name = 'Gain dB 9.0GHz'  # Specify the user-defined column name
const_gain_val = read_column_from_excel(file_path, sheet_name, column_name)

file_path = r'RX_Phase_LUT_11GHz_NomBias_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'I-Code'  # Specify the user-defined column name
i_code_1 = read_column_from_excel(file_path, sheet_name, column_name)
i_code_1 = i_code_1.astype(int)
column_name = 'Q-Code'  # Specify the user-defined column name
q_code_1 = read_column_from_excel(file_path, sheet_name, column_name)
q_code_1 = q_code_1.astype(int)
column_name = 'Gain dB 11.0GHz'  # Specify the user-defined column name
const_gain_val_1 = read_column_from_excel(file_path, sheet_name, column_name)

file_path = r'RX_Gain_LUT_9GHz_NomBias_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'Gain Code'  # Specify the user-defined column name
gain_code = read_column_from_excel(file_path, sheet_name, column_name)
gain_code = gain_code.astype(int)
column_name = 'Phase Deg 9.0GHz'  # Specify the user-defined column name
const_ph_val = read_column_from_excel(file_path, sheet_name, column_name)

file_path = r'RX_Gain_LUT_11GHz_NomBias_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'Gain Code'  # Specify the user-defined column name
gain_code_1 = read_column_from_excel(file_path, sheet_name, column_name)
gain_code_1 = gain_code_1.astype(int)
column_name = 'Phase Deg 11.0GHz'  # Specify the user-defined column name
const_ph_val_1 = read_column_from_excel(file_path, sheet_name, column_name)

gain_lut_len=64
phase_pts_in_gain_lut=4
"""Phase error Calculation"""
ph_err = [0] * gain_lut_len
ph_err_idx = [0] * gain_lut_len
ph_err_idx_signed = [0] * gain_lut_len
for i in range (gain_lut_len):
    ph_err[i]=0
    for j in range(phase_pts_in_gain_lut):
        phase_delta=calc_phase_wrapped(const_ph_val[0+(j*gain_lut_len)] - const_ph_val[i+(j*gain_lut_len)])
        ph_err[i] = (ph_err[i] + phase_delta)
    ph_err[i]=ph_err[i]/phase_pts_in_gain_lut    #avg
    ph_err_idx[i] = round(ph_err[i] / 2.975)

ph_err_min = min(ph_err_idx[0:50])
ph_err_max = max(ph_err_idx[0:50])

if (ph_err_max > 3):
    for i in range (gain_lut_len):
        if (ph_err_idx[i] + 3 - ph_err_max < -4):
            ph_err_idx[i] = -4
        else :
           ph_err_idx[i] = ph_err_idx[i] + 3 - ph_err_max
elif (ph_err_min < -4):
    for i in range (gain_lut_len):
        if (ph_err_idx[i] - 4 - ph_err_min > 3 ):
            ph_err_idx[i] = 3
        else :
            ph_err_idx[i] = ph_err_idx[i] - 4 - ph_err_min
            
for i in range (gain_lut_len):
    if (ph_err_idx[i] < 0):
        ph_err_idx_signed[i] = 8 + ph_err_idx[i]
    else :
        ph_err_idx_signed[i] = ph_err_idx[i]
        
"""Phase error Calculation freq 1"""
ph_err_1 = [0] * gain_lut_len
ph_err_idx_1 = [0] * gain_lut_len
ph_err_idx_signed_1 = [0] * gain_lut_len
for i in range (gain_lut_len):
    ph_err_1[i]=0
    for j in range(phase_pts_in_gain_lut):
        phase_delta_1=calc_phase_wrapped(const_ph_val_1[0+(j*gain_lut_len)] - const_ph_val_1[i+(j*gain_lut_len)])
        ph_err_1[i] = (ph_err_1[i] + phase_delta_1)
    ph_err_1[i]=ph_err_1[i]/phase_pts_in_gain_lut    #avg
    ph_err_idx_1[i] = round(ph_err_1[i] / 2.975)

ph_err_min_1 = min(ph_err_idx_1[0:50])
ph_err_max_1 = max(ph_err_idx_1[0:50])

if (ph_err_max_1 > 3):
    for i in range (gain_lut_len):
        if (ph_err_idx_1[i] + 3 - ph_err_max_1 < -4):
            ph_err_idx_1[i] = -4
        else :
           ph_err_idx_1[i] = ph_err_idx_1[i] + 3 - ph_err_max_1
elif (ph_err_min_1 < -4):
    for i in range (gain_lut_len):
        if (ph_err_idx_1[i] - 4 - ph_err_min_1 > 3 ):
            ph_err_idx_1[i] = 3
        else :
            ph_err_idx_1[i] = ph_err_idx_1[i] - 4 - ph_err_min_1
            
for i in range (gain_lut_len):
    if (ph_err_idx_1[i] < 0):
        ph_err_idx_signed_1[i] = 8 + ph_err_idx_1[i]
    else :
        ph_err_idx_signed_1[i] = ph_err_idx_1[i]
 

phase_lut_len=128        
"""Gain error calculation """
g_err = [0]*phase_lut_len
g_err_idx = [0]*phase_lut_len
g_err_idx_signed = [0]*phase_lut_len
for i in range (phase_lut_len):
    g_err[i] = const_gain_val[i] - const_gain_val[4]
    g_err_idx[i] = round(g_err[i]/0.5)
            
g_err_min = min(g_err_idx)
g_err_max = max(g_err_idx)

if (g_err_max > 3):
    for i in range (phase_lut_len):
        if (g_err_idx[i] + 3 - g_err_max < -4):
            g_err_idx[i] = -4
        else :
           g_err_idx[i] = g_err_idx[i] + 3 - g_err_max
elif (g_err_min < -4):
    for i in range (phase_lut_len):
        if (g_err_idx[i] - 4 - g_err_min > 3 ):
            g_err_idx[i] = 3
        else :
            g_err_idx[i] = g_err_idx[i] - 4 - g_err_min
            
for i in range (phase_lut_len):
    if (g_err_idx[i] < 0):
        g_err_idx_signed[i] = 8 + g_err_idx[i]
    else :
        g_err_idx_signed[i] = g_err_idx[i]        
        
"""Gain error calculation for freq 1"""
g_err_1 = [0]*phase_lut_len
g_err_idx_1 = [0]*phase_lut_len
g_err_idx_signed_1 = [0]*phase_lut_len
for i in range (phase_lut_len):
    g_err_1[i] = const_gain_val_1[i] - const_gain_val_1[4]
    g_err_idx_1[i] = round(g_err_1[i]/0.5)
            
g_err_min_1 = min(g_err_idx_1)
g_err_max_1 = max(g_err_idx_1)

if (g_err_max_1 > 3):
    for i in range (phase_lut_len):
        if (g_err_idx_1[i] + 3 - g_err_max_1 < -4):
            g_err_idx_1[i] = -4
        else :
           g_err_idx_1[i] = g_err_idx_1[i] + 3 - g_err_max_1
elif (g_err_min_1 < -4):
    for i in range (phase_lut_len):
        if (g_err_idx_1[i] - 4 - g_err_min_1 > 3 ):
            g_err_idx_1[i] = 3
        else :
            g_err_idx_1[i] = g_err_idx_1[i] - 4 - g_err_min_1
            
for i in range (phase_lut_len):
    if (g_err_idx_1[i] < 0):
        g_err_idx_signed_1[i] = 8 + g_err_idx_1[i]
    else :
        g_err_idx_signed_1[i] = g_err_idx_1[i]   
        
    
"""Populating LUT"""
"""Disable phase gain corr for RX"""
orion.CORR_CFG.en_gain_corr = 1
orion.CORR_CFG.en_phase_corr = 1
orion.CORR_CFG.write()

phase_corr_dis = 0
gain_corr_dis = 0

"""Write RX Phase mem """
rx_phase_val_i = [[[0 for _ in range(128)] for _ in range(4)] for _ in range(2)]
rx_phase_val_q = [[[0 for _ in range(128)] for _ in range(4)] for _ in range(2)]
rx_gain_err = [[[0 for _ in range(128)] for _ in range(4)] for _ in range(2)]


freq = 0
temp = 0
i = 0    
page_id = 0
page_id = math.floor(i/16) + freq*8



for i in range (128):
    rx_phase_val_i[0][0][i] = i_code[i]
    rx_phase_val_q[0][0][i] = q_code[i]
    rx_gain_err[0][0][i] = 0 if gain_corr_dis else g_err_idx_signed[i]
    if i%16 == 0:
        orion.PAGE_ID.page_id = math.floor(i/16) + freq*8
        orion.PAGE_ID.write()
        orion.PAGE_ID.read()
        orion.PAGE_ID.display()
    orion_lut.RX_PHASE_MEM.pos = i % 16;
    orion_lut.RX_PHASE_MEM.rx_freq_val = 0
    orion_lut.RX_PHASE_MEM.rx_temp_val = 0
    orion_lut.RX_PHASE_MEM.rx_phase_val_i = rx_phase_val_i[0][0][i]
    orion_lut.RX_PHASE_MEM.rx_phase_val_q = rx_phase_val_q[0][0][i]
    orion_lut.RX_PHASE_MEM.rx_gain_err = rx_gain_err[0][0][i]
    orion_lut.RX_PHASE_MEM.write()

"""Write RX Gain mem """
rx_gain_val = [[[0 for _ in range(64)] for _ in range(4)] for _ in range(2)]
rx_ph_err = [[[0 for _ in range(64)] for _ in range(4)] for _ in range(2)]


freq = 0
temp = 0
i = 0    
page_id = 16
page_id = math.floor(i/16) + 16 + freq*4



for i in range (gain_lut_len):
    rx_gain_val[0][0][i] = gain_code[i];
    rx_ph_err[0][0][i] = 0 if phase_corr_dis else ph_err_idx_signed[i];
    if i%16 == 0:
        orion.PAGE_ID.page_id = math.floor(i/16) + 16 + freq*4
        orion.PAGE_ID.write()
        orion.PAGE_ID.read()
        orion.PAGE_ID.display()
    orion_lut.RX_GAIN_MEM.pos = i % 16;
    orion_lut.RX_GAIN_MEM.rx_freq_val = 0
    orion_lut.RX_GAIN_MEM.rx_temp_val = 0
    if i > 52 :
        orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[0][0][52]
        orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[0][0][52]
        orion_lut.RX_GAIN_MEM.write()
    else :
        orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[0][0][i]
        orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[0][0][i]
        orion_lut.RX_GAIN_MEM.write()
    
"""Programming LUT for frequency ID 1 """
"""Write RX Phase mem Freq 1"""
freq = 1
temp = 0
i = 0    
page_id = 0
page_id = math.floor(i/16) + freq*8



for i in range (128):
    rx_phase_val_i[1][0][i] = i_code_1[i]
    rx_phase_val_q[1][0][i] = q_code_1[i]
    rx_gain_err[1][0][i] = 0 if gain_corr_dis else g_err_idx_signed_1[i]
    if i%16 == 0:
        orion.PAGE_ID.page_id = math.floor(i/16) + freq*8
        orion.PAGE_ID.write()
        orion.PAGE_ID.read()
        orion.PAGE_ID.display()
    orion_lut.RX_PHASE_MEM.pos = i % 16;
    orion_lut.RX_PHASE_MEM.rx_freq_val = 0
    orion_lut.RX_PHASE_MEM.rx_temp_val = 0
    orion_lut.RX_PHASE_MEM.rx_phase_val_i = rx_phase_val_i[1][0][i]
    orion_lut.RX_PHASE_MEM.rx_phase_val_q = rx_phase_val_q[1][0][i]
    orion_lut.RX_PHASE_MEM.rx_gain_err = rx_gain_err[1][0][i]
    orion_lut.RX_PHASE_MEM.write()

"""Write RX Gain mem Freq 1"""
freq = 1
temp = 0
i = 0    
page_id = 16
page_id = math.floor(i/16) + 16 + freq*4


for i in range (gain_lut_len):
    rx_gain_val[1][0][i] = gain_code_1[i];
    rx_ph_err[1][0][i] = 0 if phase_corr_dis else ph_err_idx_signed_1[i];
    if i%16 == 0:
        orion.PAGE_ID.page_id = math.floor(i/16) + 16 + freq*4
        orion.PAGE_ID.write()
        orion.PAGE_ID.read()
        orion.PAGE_ID.display()
    orion_lut.RX_GAIN_MEM.pos = i % 16;
    orion_lut.RX_GAIN_MEM.rx_freq_val = 0
    orion_lut.RX_GAIN_MEM.rx_temp_val = 0
    if i > 52 :
        orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[1][0][52]
        orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[1][0][52]
        orion_lut.RX_GAIN_MEM.write()
    else :
        orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[1][0][i]
        orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[1][0][i]
        orion_lut.RX_GAIN_MEM.write()




#---------------------------------Populating TX LUT--------------------------------------------
# User-defined parameters
file_path = r'TX_Phase_LUT_10p5GHz_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'I-Code'  # Specify the user-defined column name
i_code = read_column_from_excel(file_path, sheet_name, column_name)
i_code = i_code.astype(int)
column_name = 'Q-Code'  # Specify the user-defined column name
q_code = read_column_from_excel(file_path, sheet_name, column_name)
q_code = q_code.astype(int)


file_path = r'TX_Gain_LUT_10p5GHz_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'Gain Code'  # Specify the user-defined column name
gain_code = read_column_from_excel(file_path, sheet_name, column_name)
gain_code = gain_code.astype(int)

    
"""Populating LUT"""
"""Write TX Phase mem """
orion.PAGE_ID.page_id = 0x18
orion.PAGE_ID.write()
orion.PAGE_ID.read()
orion.PAGE_ID.display()

i=0 
tx_phase_val_i = [0] * 128
tx_phase_val_q = [0] * 128
for i in range (128) :
    tx_phase_val_i[i] = i_code[i]
    tx_phase_val_q[i] = q_code[i]
    if i == 64 :
        orion.PAGE_ID.page_id = 0x19
        orion.PAGE_ID.write()
        orion.PAGE_ID.read()
        orion.PAGE_ID.display()
        
    orion_lut.TX_PHASE_MEM.pos = i % 64;
    orion_lut.TX_PHASE_MEM.tx_phase_val_i = tx_phase_val_i[i]
    orion_lut.TX_PHASE_MEM.tx_phase_val_q = tx_phase_val_q[i]
    orion_lut.TX_PHASE_MEM.write()

"""Write TX Gain mem """
orion.PAGE_ID.page_id = 0x1A
orion.PAGE_ID.write()
orion.PAGE_ID.read()
orion.PAGE_ID.display()
    
i=0 
tx_gain_val = [0] * 64
tx_final_gain_val = [0] * 64

for i in range (64) :
    tx_gain_val[i] = gain_code[i]
    if (TX_BIAS_MODE=="NOM"):
        tx_final_gain_val[i] = 31
    elif (TX_BIAS_MODE=="LOW"):
        tx_final_gain_val[i] = 12
        
    orion_lut.TX_GAIN_MEM.pos = i
    orion_lut.TX_GAIN_MEM.tx_gain_val = tx_gain_val[i]
    orion_lut.TX_GAIN_MEM.tx_final_gain_val = tx_final_gain_val[i]
    orion_lut.TX_GAIN_MEM.write()


#-----------------------PA and LNA bias DAC ctrl select--------------------

orion.DAC_CTRL_PA0.DAC_CTRL_PA0 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_PA0.write()
orion.DAC_CTRL_PA1.DAC_CTRL_PA1 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_PA1.write()
orion.DAC_CTRL_PA2.DAC_CTRL_PA2 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_PA2.write()
orion.DAC_CTRL_PA3.DAC_CTRL_PA3 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_PA3.write()

orion.DAC_CTRL_LNA0.DAC_CTRL_LNA0 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_LNA0.write()
orion.DAC_CTRL_LNA1.DAC_CTRL_LNA1 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_LNA1.write()
orion.DAC_CTRL_LNA2.DAC_CTRL_LNA2 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_LNA2.write()
orion.DAC_CTRL_LNA3.DAC_CTRL_LNA3 = 0 # 0 corresponds to -2.5V
orion.DAC_CTRL_LNA3.write()

orion.DAC_CTRL_PA0_PDN.DAC_CTRL_PA0_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_PA0_PDN.write()
orion.DAC_CTRL_PA1_PDN.DAC_CTRL_PA1_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_PA1_PDN.write()
orion.DAC_CTRL_PA2_PDN.DAC_CTRL_PA2_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_PA2_PDN.write()
orion.DAC_CTRL_PA3_PDN.DAC_CTRL_PA3_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_PA3_PDN.write()

orion.DAC_CTRL_LNA0_PDN.DAC_CTRL_LNA0_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_LNA0_PDN.write()
orion.DAC_CTRL_LNA1_PDN.DAC_CTRL_LNA1_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_LNA1_PDN.write()
orion.DAC_CTRL_LNA2_PDN.DAC_CTRL_LNA2_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_LNA2_PDN.write()
orion.DAC_CTRL_LNA3_PDN.DAC_CTRL_LNA3_PDN = 127 # 0 corresponds to -5V
orion.DAC_CTRL_LNA3_PDN.write()


#---------------------------PA and LNA mask---------------------------------

# Set rx_mask as 1 for lna0 and rx0, 2 for lna1 and rx1, 4 for lna2 and rx2, 8 for lna3 and rx3
# Set tx_mask as 1 for pa0 and tx0, 2 for pa1 and tx1, 4 for pa2 and tx2, 8 for pa3 and tx3
orion.TR_MASK.rx_mask = 0x4
orion.TR_MASK.tx_mask = 0x4
orion.TR_MASK.write()


#--------------Set target gain and phase for both TX and RX-----------------

# Setting target gain and phase for TX
""" 
    PLEASE PROVIDE TARGET GAIN/ATTENUATION and TARGET PHASE VALUES HERE 
    GAIN RANGE: 0 to -26 dB
    PHASE RANGE: 0 degrees to +360 degrees (-ve phase values not allowed)
""" 
RX_TARGET_GAIN_dB = 0
RX_TARGET_PHASE_DEG = 0

RX_TARGET_GAIN_dB_ch1 = 0
RX_TARGET_PHASE_DEG_ch1 = 0

RX_TARGET_GAIN_dB_ch2 = 0
RX_TARGET_PHASE_DEG_ch2 = 0

RX_TARGET_GAIN_dB_ch3 = 0
RX_TARGET_PHASE_DEG_ch3 = 0

RX_INPUT_FREQ_GHz=9 # 9 for 9GHz LUT, 11 for 11GHz LUT


target_gain_lut_idx_rx=round(abs(RX_TARGET_GAIN_dB-1)/0.5)
target_phase_lut_idx_rx=round(abs(RX_TARGET_PHASE_DEG)/2.975)+4
    
target_gain_lut_idx_ch1_rx=round(abs(RX_TARGET_GAIN_dB_ch1-1)/0.5)
target_phase_lut_idx_ch1_rx=round(abs(RX_TARGET_PHASE_DEG_ch1)/2.975)+4
   
target_gain_lut_idx_ch2_rx=round(abs(RX_TARGET_GAIN_dB_ch2-1)/0.5)
target_phase_lut_idx_ch2_rx=round(abs(RX_TARGET_PHASE_DEG_ch2)/2.975)+4
    
target_gain_lut_idx_ch3_rx=round(abs(RX_TARGET_GAIN_dB_ch3-1)/0.5)
target_phase_lut_idx_ch3_rx=round(abs(RX_TARGET_PHASE_DEG_ch3)/2.975)+4

if (RX_INPUT_FREQ_GHz<10):
    target_freq_idx=0
else:
    target_freq_idx=1
    
phase_code_rx0 = target_phase_lut_idx_rx
phase_code_rx1 = target_phase_lut_idx_ch1_rx
phase_code_rx2 = target_phase_lut_idx_ch2_rx
phase_code_rx3 = target_phase_lut_idx_ch3_rx
gain_code_rx0 = target_gain_lut_idx_rx
gain_code_rx1 = target_gain_lut_idx_ch1_rx
gain_code_rx2 = target_gain_lut_idx_ch2_rx
gain_code_rx3 = target_gain_lut_idx_ch3_rx

""" Loading Start (SW LOADING) """
orion.STG2_CFG.use_reg_for_stg2_update = 1
orion.STG2_CFG.write()

"""LUT Frequency ID update"""
orion.FREQ_ID.freq_id=target_freq_idx
orion.FREQ_ID.write()
orion.RSVD2.write()
orion.RSVD3.write()

""" LOAD RX """
"""Set RX phase and gain code """
orion.PHASE_CODE_RX0.phase_code_rx0 =  phase_code_rx0
orion.PHASE_CODE_RX0.write()
orion.GAIN_CODE_RX0.gain_code_rx0 = gain_code_rx0
orion.GAIN_CODE_RX0.write()
orion.PHASE_CODE_RX1.phase_code_rx1 =  phase_code_rx1
orion.PHASE_CODE_RX1.write()
orion.GAIN_CODE_RX1.gain_code_rx1 = gain_code_rx1
orion.GAIN_CODE_RX1.write()
orion.PHASE_CODE_RX2.phase_code_rx2 =  phase_code_rx2
orion.PHASE_CODE_RX2.write()
orion.GAIN_CODE_RX2.gain_code_rx2 = gain_code_rx2
orion.GAIN_CODE_RX2.write()
orion.PHASE_CODE_RX3.phase_code_rx3 =  phase_code_rx3
orion.PHASE_CODE_RX3.write()
orion.GAIN_CODE_RX3.gain_code_rx3 = gain_code_rx3
orion.GAIN_CODE_RX3.write()


""" set update code """
orion.UPDATE_CODE.update_code = 1
orion.UPDATE_CODE.write()

# Setting target gain and phase for TX
""" 
    PLEASE PROVIDE TARGET GAIN/ATTENUATION and TARGET PHASE VALUES HERE 
    GAIN RANGE: 0 to -30 dB
    PHASE RANGE: 0 degrees to +360 degrees (-ve phase values not allowed)
""" 
TX_TARGET_GAIN_dB = 0
TX_TARGET_PHASE_DEG = 0

TX_TARGET_GAIN_dB_ch1 = 0
TX_TARGET_PHASE_DEG_ch1 = 0

TX_TARGET_GAIN_dB_ch2 = 0
TX_TARGET_PHASE_DEG_ch2 = 0

TX_TARGET_GAIN_dB_ch3 = 0
TX_TARGET_PHASE_DEG_ch3 =0


target_gain_lut_idx_tx=round(abs(TX_TARGET_GAIN_dB)/0.5)
target_phase_lut_idx_tx=round(abs(TX_TARGET_PHASE_DEG)/2.8125)

target_gain_lut_idx_ch1_tx=round(abs(TX_TARGET_GAIN_dB_ch1)/0.5)
target_phase_lut_idx_ch1_tx=round(abs(TX_TARGET_PHASE_DEG_ch1)/2.8125)

target_gain_lut_idx_ch2_tx=round(abs(TX_TARGET_GAIN_dB_ch2)/0.5)
target_phase_lut_idx_ch2_tx=round(abs(TX_TARGET_PHASE_DEG_ch2)/2.8125)

target_gain_lut_idx_ch3_tx=round(abs(TX_TARGET_GAIN_dB_ch3)/0.5)
target_phase_lut_idx_ch3_tx=round(abs(TX_TARGET_PHASE_DEG_ch3)/2.8125)

phase_code_tx0 = target_phase_lut_idx_tx
phase_code_tx1 = target_phase_lut_idx_ch1_tx
phase_code_tx2 = target_phase_lut_idx_ch2_tx
phase_code_tx3 = target_phase_lut_idx_ch3_tx

gain_code_tx0 = target_gain_lut_idx_tx
gain_code_tx1 = target_gain_lut_idx_ch1_tx
gain_code_tx2 = target_gain_lut_idx_ch2_tx
gain_code_tx3 = target_gain_lut_idx_ch3_tx

""" Loading Start (SW LOADING) """
orion.STG2_CFG.use_reg_for_stg2_update = 1
orion.STG2_CFG.write()

""" LOAD tx """
"""Set TX phase and gain code """
orion.PHASE_CODE_TX0.phase_code_tx0 =  phase_code_tx0
orion.PHASE_CODE_TX0.write()
orion.GAIN_CODE_TX0.gain_code_tx0 = gain_code_tx0
orion.GAIN_CODE_TX0.write()
orion.PHASE_CODE_TX1.phase_code_tx1 =  phase_code_tx1
orion.PHASE_CODE_TX1.write()
orion.GAIN_CODE_TX1.gain_code_tx1 = gain_code_tx1
orion.GAIN_CODE_TX1.write()
orion.PHASE_CODE_TX2.phase_code_tx2 =  phase_code_tx2
orion.PHASE_CODE_TX2.write()
orion.GAIN_CODE_TX2.gain_code_tx2 = gain_code_tx2
orion.GAIN_CODE_TX2.write()
orion.PHASE_CODE_TX3.phase_code_tx3 =  phase_code_tx3
orion.PHASE_CODE_TX3.write()
orion.GAIN_CODE_TX3.gain_code_tx3 = gain_code_tx3
orion.GAIN_CODE_TX3.write()

""" set update code """
orion.UPDATE_CODE.update_code = 1
orion.UPDATE_CODE.write()


#------------------------------Read RX and TX----------------------------------
"""Read RX"""
rx0_i_lsb_temp0  = orion.RX0_I_LSB_TEMP0.read()
rx0_q_lsb_temp0  = orion.RX0_Q_LSB_TEMP0.read()
rx0_av_lsb_temp0 = orion.RX0_AV_LSB_TEMP0.read()
rx0_msb_temp0 	 = orion.RX0_MSB_TEMP0.read()

rx1_i_lsb_temp0  = orion.RX1_I_LSB_TEMP0.read()
rx1_q_lsb_temp0  = orion.RX1_Q_LSB_TEMP0.read()
rx1_av_lsb_temp0 = orion.RX1_AV_LSB_TEMP0.read()
rx1_msb_temp0 	 = orion.RX1_MSB_TEMP0.read()

rx2_i_lsb_temp0  = orion.RX2_I_LSB_TEMP0.read()
rx2_q_lsb_temp0  = orion.RX2_Q_LSB_TEMP0.read()
rx2_av_lsb_temp0 = orion.RX2_AV_LSB_TEMP0.read()
rx2_msb_temp0 	 = orion.RX2_MSB_TEMP0.read()

rx3_i_lsb_temp0  = orion.RX3_I_LSB_TEMP0.read()
rx3_q_lsb_temp0  = orion.RX3_Q_LSB_TEMP0.read()
rx3_av_lsb_temp0 = orion.RX3_AV_LSB_TEMP0.read()
rx3_msb_temp0 	 = orion.RX3_MSB_TEMP0.read()

rx0_phase_val_i_read_temp0 = (rx0_msb_temp0 & 0x1) << 8 | (rx0_i_lsb_temp0 & 0xFF)
rx0_phase_val_q_read_temp0 = (rx0_msb_temp0 & 0x2) << 7 | (rx0_q_lsb_temp0 & 0xFF)
rx0_gain_val_read_temp0 = (rx0_msb_temp0 & 0x1C) << 6 | (rx0_av_lsb_temp0 & 0xFF)

rx1_phase_val_i_read_temp0 = (rx1_msb_temp0 & 0x1) << 8 | (rx1_i_lsb_temp0 & 0xFF)
rx1_phase_val_q_read_temp0 = (rx1_msb_temp0 & 0x2) << 7 | (rx1_q_lsb_temp0 & 0xFF)
rx1_gain_val_read_temp0 = (rx1_msb_temp0 & 0x1C) << 6 | (rx1_av_lsb_temp0 & 0xFF)

rx2_phase_val_i_read_temp0 = (rx2_msb_temp0 & 0x1) << 8 | (rx2_i_lsb_temp0 & 0xFF)
rx2_phase_val_q_read_temp0 = (rx2_msb_temp0 & 0x2) << 7 | (rx2_q_lsb_temp0 & 0xFF)
rx2_gain_val_read_temp0 = (rx2_msb_temp0 & 0x1C) << 6 | (rx2_av_lsb_temp0 & 0xFF)

rx3_phase_val_i_read_temp0 = (rx3_msb_temp0 & 0x1) << 8 | (rx3_i_lsb_temp0 & 0xFF)
rx3_phase_val_q_read_temp0 = (rx3_msb_temp0 & 0x2) << 7 | (rx3_q_lsb_temp0 & 0xFF)
rx3_gain_val_read_temp0 = (rx3_msb_temp0 & 0x1C) << 6 | (rx3_av_lsb_temp0 & 0xFF)


"""Read TX"""
tx0_i_lsb	 = orion.TX0_I_LSB.read()	
tx0_q_lsb 	 = orion.TX0_Q_LSB.read()
tx0_av_lsb 	 = orion.TX0_AV_LSB.read()
tx0_msb 	 = orion.TX0_MSB.read()
tx0_final_av = orion.TX0_FINAL_AV.read()
tx1_i_lsb	 = orion.TX1_I_LSB.read()	
tx1_q_lsb 	 = orion.TX1_Q_LSB.read()
tx1_av_lsb 	 = orion.TX1_AV_LSB.read()
tx1_msb 	 = orion.TX1_MSB.read()
tx1_final_av = orion.TX1_FINAL_AV.read()
tx2_i_lsb	 = orion.TX2_I_LSB.read()	
tx2_q_lsb 	 = orion.TX2_Q_LSB.read()
tx2_av_lsb 	 = orion.TX2_AV_LSB.read()
tx2_msb 	 = orion.TX2_MSB.read()
tx2_final_av = orion.TX2_FINAL_AV.read()
tx3_i_lsb	 = orion.TX3_I_LSB.read()	
tx3_q_lsb 	 = orion.TX3_Q_LSB.read()
tx3_av_lsb 	 = orion.TX3_AV_LSB.read()
tx3_msb 	 = orion.TX3_MSB.read()
tx3_final_av = orion.TX3_FINAL_AV.read()


tx0_phase_val_i_read    = (tx0_msb & 0x1) << 8 | (tx0_i_lsb & 0xFF)
tx0_phase_val_q_read    = (tx0_msb & 0x2) << 7 | (tx0_q_lsb & 0xFF)
tx0_gain_val_read       = (tx0_msb & 0x1C) << 6 | (tx0_av_lsb & 0xFF)
tx0_final_gain_val_read = tx0_final_av & 0x1F
tx1_phase_val_i_read    = (tx1_msb & 0x1) << 8 | (tx1_i_lsb & 0xFF)
tx1_phase_val_q_read    = (tx1_msb & 0x2) << 7 | (tx1_q_lsb & 0xFF)
tx1_gain_val_read       = (tx1_msb & 0x1C) << 6 | (tx1_av_lsb & 0xFF)
tx1_final_gain_val_read = tx1_final_av & 0x1F
tx2_phase_val_i_read    = (tx2_msb & 0x1) << 8 | (tx2_i_lsb & 0xFF)
tx2_phase_val_q_read    = (tx2_msb & 0x2) << 7 | (tx2_q_lsb & 0xFF)
tx2_gain_val_read       = (tx2_msb & 0x1C) << 6 | (tx2_av_lsb & 0xFF)
tx2_final_gain_val_read = tx2_final_av & 0x1F
tx3_phase_val_i_read    = (tx3_msb & 0x1) << 8 | (tx3_i_lsb & 0xFF)
tx3_phase_val_q_read    = (tx3_msb & 0x2) << 7 | (tx3_q_lsb & 0xFF)
tx3_gain_val_read       = (tx3_msb & 0x1C) << 6 | (tx3_av_lsb & 0xFF)
tx3_final_gain_val_read = tx3_final_av & 0x1F


spi.pa_set()

orion.TR_CFG.data_path_en = 0x1
orion.TR_CFG.write()

orion.TR_CTRL_2.det_en_force = 0xF
orion.TR_CTRL_2.det_en_force_val = 0xF
orion.TR_CTRL_2.write()


orion.REG0_ADC.en_pkdet_to_adc_sw=0x1
orion.REG0_ADC.en_gp7_to_adc_sw=0x1
orion.REG0_ADC.write()
orion.POWER_DET_CFG.det0_sel=0x1
orion.POWER_DET_CFG.write() #Check the output at JP13

spi.tr_reset()
orion.EXT_CTRL_STS_REG_1.read()
orion.EXT_CTRL_STS_REG_1.display()
spi.tr_tggl()
time.sleep(1)
orion.EXT_CTRL_STS_REG_1.read()
orion.EXT_CTRL_STS_REG_1.display()
spi.tr_tggl()
time.sleep(1)
orion.EXT_CTRL_STS_REG_1.read()
orion.EXT_CTRL_STS_REG_1.display()
for i in range(1,100000000):
    spi.tr_set()  # tr set
    print("TR is SET")
    time.sleep(0.000001)
    spi.tr_reset()   # tr reset
    print("TR is RESET")
    time.sleep(0.000009)

orion.TR_CFG.data_path_en = 0x0
orion.TR_CFG.write()

spi.close()
      



