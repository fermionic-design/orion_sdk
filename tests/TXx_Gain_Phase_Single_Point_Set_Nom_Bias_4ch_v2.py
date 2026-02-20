# -*- coding: utf-8 -*-
"""
Set TXx at a single gain and phase setting
"""
import sys

sys.path.append('../include')

import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from SPI import *
import pandas as pd


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
TX_BIAS_MODE="MAX"      # "NOM" for nominal bias mode or "LOW" for low bias mode

spi = SPI()
orion = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)

orion.DEVICE_ID.read()
print('device_id = '+hex(orion.DEVICE_ID.device_id))

orion.REVISION.read()
print('major_revision = '+hex(orion.REVISION.major_rev))
print('minor_revision = '+hex(orion.REVISION.minor_rev))

#-------------------------------------------------------------------------
# User-defined parameters
file_path = r'TX_Phase_LUT_10p5GHz_Demo.xlsx'  # Provide the path to your Excel file
sheet_name = 'Sheet1'  # Specify the sheet name
column_name = 'I-Code'  # Specify the user-defined column name
i_code = read_column_from_excel(file_path, sheet_name, column_name)
i_code = i_code.astype(int)
# print(i_code)
column_name = 'Q-Code'  # Specify the user-defined column name
q_code = read_column_from_excel(file_path, sheet_name, column_name)
q_code = q_code.astype(int)
# print(q_code)


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
# orion.PAGE_ID.display()

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
        # orion.PAGE_ID.display()
        
    orion_lut.TX_PHASE_MEM.pos = i % 64;
    orion_lut.TX_PHASE_MEM.tx_phase_val_i = tx_phase_val_i[i]
    orion_lut.TX_PHASE_MEM.tx_phase_val_q = tx_phase_val_q[i]
    orion_lut.TX_PHASE_MEM.write()

"""Write TX Gain mem """
orion.PAGE_ID.page_id = 0x1A
orion.PAGE_ID.write()
orion.PAGE_ID.read()
# orion.PAGE_ID.display()
    
i=0 
tx_gain_val = [0] * 64
tx_final_gain_val = [0] * 64

for i in range (64) :
    tx_gain_val[i] = gain_code[i]
    if ((TX_BIAS_MODE=="MAX") | (TX_BIAS_MODE=="NOM")):
        tx_final_gain_val[i] = 31
    elif (TX_BIAS_MODE=="LOW"):
        tx_final_gain_val[i] = 12
        
    orion_lut.TX_GAIN_MEM.pos = i
    orion_lut.TX_GAIN_MEM.tx_gain_val = tx_gain_val[i]
    orion_lut.TX_GAIN_MEM.tx_final_gain_val = tx_final_gain_val[i]
    orion_lut.TX_GAIN_MEM.write()
    

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
TX_TARGET_PHASE_DEG_ch3 = 0

#-------------------------------------------------------------------------
RF_CTRL_FUNC.set_enable_txlna(orion, 0x1)
RF_CTRL_FUNC.set_enable_tx(orion, 0x1)
""" Enable TX function : RF_CTRL_FUNC.set_enable_tx(orion, TX_EN_CODE)

    TX_EN_CODE  : DETAILS
    0x1         : TX0 ON
    0x2         : TX1 ON
    0x4         : TX2 ON
    0x8         : TX3 ON 
    0xF         : ALL 4TX ON 
    
"""    
RF_CTRL_FUNC.set_TX_bias_mode(orion, TX_BIAS_MODE)
RF_CTRL_FUNC.set_tx_lna_gain(orion, 255)


#------------------------------------------------------------------------------ 
target_gain_lut_idx=round(abs(TX_TARGET_GAIN_dB)/0.5)
target_phase_lut_idx=round(abs(TX_TARGET_PHASE_DEG)/2.8125)

target_gain_lut_idx_ch1=round(abs(TX_TARGET_GAIN_dB_ch1)/0.5)
target_phase_lut_idx_ch1=round(abs(TX_TARGET_PHASE_DEG_ch1)/2.8125)

target_gain_lut_idx_ch2=round(abs(TX_TARGET_GAIN_dB_ch2)/0.5)
target_phase_lut_idx_ch2=round(abs(TX_TARGET_PHASE_DEG_ch2)/2.8125)

target_gain_lut_idx_ch3=round(abs(TX_TARGET_GAIN_dB_ch3)/0.5)
target_phase_lut_idx_ch3=round(abs(TX_TARGET_PHASE_DEG_ch3)/2.8125)

phase_code_tx0 = target_phase_lut_idx
phase_code_tx1 = target_phase_lut_idx_ch1
phase_code_tx2 = target_phase_lut_idx_ch2
phase_code_tx3 = target_phase_lut_idx_ch3

gain_code_tx0 = target_gain_lut_idx
gain_code_tx1 = target_gain_lut_idx_ch1
gain_code_tx2 = target_gain_lut_idx_ch2
gain_code_tx3 = target_gain_lut_idx_ch3

""" Loading Start (SW LOADING) """
# orion.STG2_CFG.use_reg_for_stg2_update = 1
# orion.STG2_CFG.write()

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

RF_CTRL_FUNC.set_tx0_gain(orion,2047)
RF_CTRL_FUNC.set_tx1_gain(orion,2047)
RF_CTRL_FUNC.set_tx2_gain(orion,2047)
RF_CTRL_FUNC.set_tx3_gain(orion,2047)

RF_CTRL_FUNC.set_tx0_iphase(orion,254)
RF_CTRL_FUNC.set_tx0_qphase(orion,1)
RF_CTRL_FUNC.set_tx2_iphase(orion,254)
RF_CTRL_FUNC.set_tx2_qphase(orion,1)
RF_CTRL_FUNC.set_tx3_iphase(orion,254)
RF_CTRL_FUNC.set_tx3_qphase(orion,1)
#
# orion.TX0_Q_LSB.tx0_i_lsb = 254
# orion.TX0_Q_LSB.tx0_q_lsb = 1
# orion.TX0_Q_LSB.write()
#
# orion.TX1_Q_LSB.tx0_i_lsb = 254
# orion.TX1_Q_LSB.tx0_q_lsb = 1
# orion.TX1_Q_LSB.write()
#
# orion.TX2_Q_LSB.tx0_i_lsb = 254
# orion.TX2_Q_LSB.tx0_q_lsb = 1
# orion.TX2_Q_LSB.write()
#
# orion.TX3_Q_LSB.tx0_i_lsb = 254
# orion.TX3_Q_LSB.tx0_q_lsb = 1
# orion.TX3_Q_LSB.write()

orion.REG4_EXT_BIAS.rsvd7 = 0x02
orion.REG4_EXT_BIAS.write()
RF_CTRL_FUNC.set_tx0_drv_curr(orion,31)
RF_CTRL_FUNC.set_tx0_cmb_icurr(orion,3)
RF_CTRL_FUNC.set_tx0_cmb_qcurr(orion,3)
RF_CTRL_FUNC.set_tx_lna_curr(orion,3)
# RF_CTRL_FUNC.set_tx0_drv_curr(orion,31)
# RF_CTRL_FUNC.set_tx0_cmb_icurr(orion,3)
# RF_CTRL_FUNC.set_tx0_cmb_qcurr(orion,3)
# RF_CTRL_FUNC.set_tx_lna_curr(orion,3)
RF_CTRL_FUNC.set_tx3_drv_curr(orion,31)
RF_CTRL_FUNC.set_tx3_cmb_icurr(orion,3)
RF_CTRL_FUNC.set_tx3_cmb_qcurr(orion,3)
RF_CTRL_FUNC.set_tx_lna_curr(orion,3)
# orion.TX0_Q_LSB.read()
# orion.TX0_Q_LSB.display()
# orion.TX1_Q_LSB.read()
# orion.TX1_Q_LSB.display()
# orion.TX2_Q_LSB.read()
# orion.TX2_Q_LSB.display()
# orion.TX3_Q_LSB.read()
# orion.TX3_Q_LSB.display()

spi.close()