# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 14:44:04 2023

@author: silic
"""
RX_BIAS_MODE='NOM'
import sys

sys.path.append('../include')

import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from SPI import *
import pandas as pd
import math


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
        
#------------------------------------------------------------------------


spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))

#---------------------------------------------------

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
        # orion.PAGE_ID.display()
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
        # orion.PAGE_ID.display()
    orion_lut.RX_GAIN_MEM.pos = i % 16;
    orion_lut.RX_GAIN_MEM.rx_freq_val = 0
    orion_lut.RX_GAIN_MEM.rx_temp_val = 0
    if i > 70 :
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
        # orion.PAGE_ID.display()
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
        # orion.PAGE_ID.display()
    orion_lut.RX_GAIN_MEM.pos = i % 16;
    orion_lut.RX_GAIN_MEM.rx_freq_val = 0
    orion_lut.RX_GAIN_MEM.rx_temp_val = 0
    if i > 70 :
        orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[1][0][52]
        orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[1][0][52]
        orion_lut.RX_GAIN_MEM.write()
    else :
        orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[1][0][i]
        orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[1][0][i]
        orion_lut.RX_GAIN_MEM.write()


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
""" 
    PLEASE PROVIDE TARGET GAIN/ATTENUATION and TARGET PHASE VALUES HERE 
    GAIN RANGE: 0 to -26 dB
    PHASE RANGE: 0 degrees to +360 degrees (-ve phase values not allowed)
""" 
RX_TARGET_GAIN_dB = 0
RX_TARGET_PHASE_DEG = 0

RX_TARGET_GAIN_dB_ch1 = -0.5*0
RX_TARGET_PHASE_DEG_ch1 = 0

RX_TARGET_GAIN_dB_ch2 = 0
RX_TARGET_PHASE_DEG_ch2 = 0

RX_TARGET_GAIN_dB_ch3 = 0
RX_TARGET_PHASE_DEG_ch3 = 0

RX_INPUT_FREQ_GHz=9

#--------------------------------------------------------------------------
RF_CTRL_FUNC.set_enable_rx(orion, 0xF)

""" Enable RX function : RF_CTRL_FUNC.set_enable_rx(orion, RX_EN_CODE)

    RX_EN_CODE  : DETAILS
    0x1         : RX0 ON
    0x2         : RX1 ON
    0x4         : RX2 ON
    0x8         : RX3 ON 
    0xF         : ALL 4RX ON 
    
"""    
RF_CTRL_FUNC.set_RX_bias_mode(orion, RX_BIAS_MODE)

#------------------------------------------------------------------------------ 
target_gain_lut_idx=min(63,round(abs(RX_TARGET_GAIN_dB)/0.5))
target_phase_lut_idx=round(abs(RX_TARGET_PHASE_DEG)/2.975)+4
    
target_gain_lut_idx_ch1=min(63,round(abs(RX_TARGET_GAIN_dB_ch1)/0.5))
target_phase_lut_idx_ch1=round(abs(RX_TARGET_PHASE_DEG_ch1)/2.975)+4
   
target_gain_lut_idx_ch2=min(63,round(abs(RX_TARGET_GAIN_dB_ch2)/0.5))
target_phase_lut_idx_ch2=round(abs(RX_TARGET_PHASE_DEG_ch2)/2.975)+4
    
target_gain_lut_idx_ch3=min(63,round(abs(RX_TARGET_GAIN_dB_ch3)/0.5))
target_phase_lut_idx_ch3=round(abs(RX_TARGET_PHASE_DEG_ch3)/2.975)+4

if (RX_INPUT_FREQ_GHz<10):
    target_freq_idx=0
else:
    target_freq_idx=1
    
phase_code_rx0 = target_phase_lut_idx
phase_code_rx1 = target_phase_lut_idx_ch1
phase_code_rx2 = target_phase_lut_idx_ch2
phase_code_rx3 = target_phase_lut_idx_ch3
gain_code_rx0 = target_gain_lut_idx
gain_code_rx1 = target_gain_lut_idx_ch1
gain_code_rx2 = target_gain_lut_idx_ch2
gain_code_rx3 = target_gain_lut_idx_ch3

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
# input()
# orion.read_all()

orion.REG4_EXT_BIAS.rsvd7 = 0x02
orion.REG4_EXT_BIAS.write()

RF_CTRL_FUNC.set_rx0_gain(orion,2047)
RF_CTRL_FUNC.set_rx0_iphase(orion,255)
RF_CTRL_FUNC.set_rx0_qphase(orion,0)

RF_CTRL_FUNC.set_rx2_gain(orion,2047)
RF_CTRL_FUNC.set_rx2_iphase(orion,96)
RF_CTRL_FUNC.set_rx2_qphase(orion,444)

RF_CTRL_FUNC.set_rx3_gain(orion,2047)
RF_CTRL_FUNC.set_rx3_iphase(orion,500)
RF_CTRL_FUNC.set_rx3_qphase(orion,8)

spi.close()    

