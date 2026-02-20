# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 11:41:30 2023

@author: subhajit
"""
import sys
import time

#-------------------RX Enable-----------------------
def set_enable_rx(myDevice,myValue):
    "function to enable RX, 4-bit for 4-RX, 1 is enable"
    # Enable RX0, myValue=0x1
    # Enable RX1, myValue=0x2
    # Enable RX2, myValue=0x4
    # Enable RX3, myValue=0x8
    # Enable all RX, myValue=0xF
    myDevice.TR_CTRL.RX_en_force=0x0F
    myDevice.TR_CTRL.RX_en_force_val=(myValue & 0x0F)
    myDevice.TR_CTRL.write()
    

#------------------TX Enable-----------------------
def set_enable_tx(myDevice,myValue):
    "function to enable TX, 4-bit for 4-TX, 1 is enable"
    # Enable TX0, myValue=0x1
    # Enable TX1, myValue=0x2
    # Enable TX2, myValue=0x4
    # Enable TX3, myValue=0x8
    # Enable all TX, myValue=0xF
    myDevice.TR_CTRL_1.TX_en_force=0x0F
    myDevice.TR_CTRL_1.TX_en_force_val=(myValue & 0x0F)
    myDevice.TR_CTRL_1.write()
    
def set_enable_txlna(myDevice,myValue):
    "function to enable TX LNA, 1 is enable"
    myDevice.TR_CTRL_5.TX_lna_en_force=0x01
    myDevice.TR_CTRL_5.TX_lna_en_force_val=(myValue & 0x01)
    myDevice.TR_CTRL_5.write()


#-----------------Register change commit----------------------
def commit_reg_change(myDevice):
    "function to commit all the register changes to the device"
    
    #set STG2_CFG to 1
    myDevice.STG2_CFG.use_reg_for_stg2_update=0x01
    myDevice.STG2_CFG.write()
    
    #toggle UPDATE_CODE from 0 to 1
    myDevice.UPDATE_CODE.update_code=0x00
    myDevice.UPDATE_CODE.write()
    time.sleep(0.1)
    myDevice.UPDATE_CODE.update_code=0x01
    myDevice.UPDATE_CODE.write()
    time.sleep(0.1)
    myDevice.UPDATE_CODE.update_code=0x00
    myDevice.UPDATE_CODE.write()
    time.sleep(0.1)
    


#--------------------RX0 phase and gain ctrl------------------------
def set_rx0_iphase(myDevice,myValue):
    "function to set RX0 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    #set LSB and MSB of registers
    myDevice.RX0_I_LSB_TEMP0.rx0_i_lsb_temp0=(myValue & 0xFF)
    myDevice.RX0_MSB_TEMP0.rx0_i_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX0_I_LSB_TEMP0.write()
    myDevice.RX0_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_rx0_qphase(myDevice,myValue):
    "function to set RX0 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX0_Q_LSB_TEMP0.rx0_q_lsb_temp0=(myValue & 0xFF)
    myDevice.RX0_MSB_TEMP0.rx0_q_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX0_Q_LSB_TEMP0.write()
    myDevice.RX0_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_rx0_gain(myDevice,myValue):
    "function to set RX0 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.RX0_AV_LSB_TEMP0.rx0_av_lsb_temp0=(myValue & 0xFF)
    myDevice.RX0_MSB_TEMP0.rx0_av_msb_temp0=(myValue & 0x700) >> 8
    myDevice.RX0_AV_LSB_TEMP0.write()
    myDevice.RX0_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
 
    
#--------------------RX1 phase and gain ctrl------------------------ 
def set_rx1_iphase(myDevice,myValue):
    "function to set RX1 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX1_I_LSB_TEMP0.rx1_i_lsb_temp0=(myValue & 0xFF)
    myDevice.RX1_MSB_TEMP0.rx1_i_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX1_I_LSB_TEMP0.write()
    myDevice.RX1_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_rx1_qphase(myDevice,myValue):
    "function to set RX1 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX1_Q_LSB_TEMP0.rx1_q_lsb_temp0=(myValue & 0xFF)
    myDevice.RX1_MSB_TEMP0.rx1_q_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX1_Q_LSB_TEMP0.write()
    myDevice.RX1_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_rx1_gain(myDevice,myValue):
    "function to set RX1 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.RX1_AV_LSB_TEMP0.rx1_av_lsb_temp0=(myValue & 0xFF)
    myDevice.RX1_MSB_TEMP0.rx1_av_msb_temp0=(myValue & 0x700) >> 8
    myDevice.RX1_AV_LSB_TEMP0.write()
    myDevice.RX1_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)


#--------------------RX2 phase and gain ctrl------------------------    
def set_rx2_iphase(myDevice,myValue):
    "function to set RX2 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX2_I_LSB_TEMP0.rx2_i_lsb_temp0=(myValue & 0xFF)
    myDevice.RX2_MSB_TEMP0.rx2_i_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX2_I_LSB_TEMP0.write()
    myDevice.RX2_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_rx2_qphase(myDevice,myValue):
    "function to set RX2 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX2_Q_LSB_TEMP0.rx2_q_lsb_temp0=(myValue & 0xFF)
    myDevice.RX2_MSB_TEMP0.rx2_q_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX2_Q_LSB_TEMP0.write()
    myDevice.RX2_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_rx2_gain(myDevice,myValue):
    "function to set RX2 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.RX2_AV_LSB_TEMP0.rx2_av_lsb_temp0=(myValue & 0xFF)
    myDevice.RX2_MSB_TEMP0.rx2_av_msb_temp0=(myValue & 0x700) >> 8
    myDevice.RX2_AV_LSB_TEMP0.write()
    myDevice.RX2_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)


#--------------------RX3 phase and gain ctrl------------------------    
def set_rx3_iphase(myDevice,myValue):
    "function to set RX3 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX3_I_LSB_TEMP0.rx3_i_lsb_temp0=(myValue & 0xFF)
    myDevice.RX3_MSB_TEMP0.rx3_i_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX3_I_LSB_TEMP0.write()
    myDevice.RX3_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_rx3_qphase(myDevice,myValue):
    "function to set RX3 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.RX3_Q_LSB_TEMP0.rx3_q_lsb_temp0=(myValue & 0xFF)
    myDevice.RX3_MSB_TEMP0.rx3_q_msb_temp0=(myValue & 0x100) >> 8
    myDevice.RX3_Q_LSB_TEMP0.write()
    myDevice.RX3_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_rx3_gain(myDevice,myValue):
    "function to set RX3 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.RX3_AV_LSB_TEMP0.rx3_av_lsb_temp0=(myValue & 0xFF)
    myDevice.RX3_MSB_TEMP0.rx3_av_msb_temp0=(myValue & 0x700) >> 8
    myDevice.RX3_AV_LSB_TEMP0.write()
    myDevice.RX3_MSB_TEMP0.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    

#--------------------TX0 phase and gain ctrl------------------------
def set_tx0_iphase(myDevice,myValue):
    "function to set TX0 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX0_I_LSB.tx0_i_lsb=(myValue & 0xFF)
    myDevice.TX0_MSB.tx0_i_msb=(myValue & 0x100) >> 8
    myDevice.TX0_I_LSB.write()
    myDevice.TX0_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_tx0_qphase(myDevice,myValue):
    "function to set TX0 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX0_Q_LSB.tx0_q_lsb=(myValue & 0xFF)
    myDevice.TX0_MSB.tx0_q_msb=(myValue & 0x100) >> 8
    myDevice.TX0_Q_LSB.write()
    myDevice.TX0_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_tx0_gain(myDevice,myValue):
    "function to set TX0 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.TX0_AV_LSB.tx0_av_lsb=(myValue & 0xFF)
    myDevice.TX0_MSB.tx0_av_msb=(myValue & 0x700) >> 8
    myDevice.TX0_AV_LSB.write()
    myDevice.TX0_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)


#--------------------TX1 phase and gain ctrl------------------------
def set_tx1_iphase(myDevice,myValue):
    "function to set TX1 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX1_I_LSB.tx1_i_lsb=(myValue & 0xFF)
    myDevice.TX1_MSB.tx1_i_msb=(myValue & 0x100) >> 8
    myDevice.TX1_I_LSB.write()
    myDevice.TX1_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_tx1_qphase(myDevice,myValue):
    "function to set TX1 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX1_Q_LSB.tx1_q_lsb=(myValue & 0xFF)
    myDevice.TX1_MSB.tx1_q_msb=(myValue & 0x100) >> 8
    myDevice.TX1_Q_LSB.write()
    myDevice.TX1_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_tx1_gain(myDevice,myValue):
    "function to set TX1 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.TX1_AV_LSB.tx1_av_lsb=(myValue & 0xFF)
    myDevice.TX1_MSB.tx1_av_msb=(myValue & 0x700) >> 8
    myDevice.TX1_AV_LSB.write()
    myDevice.TX1_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)


#--------------------TX2 phase and gain ctrl------------------------
def set_tx2_iphase(myDevice,myValue):
    "function to set TX2 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX2_I_LSB.tx2_i_lsb=(myValue & 0xFF)
    myDevice.TX2_MSB.tx2_i_msb=(myValue & 0x100) >> 8
    myDevice.TX2_I_LSB.write()
    myDevice.TX2_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_tx2_qphase(myDevice,myValue):
    "function to set TX2 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX2_Q_LSB.tx2_q_lsb=(myValue & 0xFF)
    myDevice.TX2_MSB.tx2_q_msb=(myValue & 0x100) >> 8
    myDevice.TX2_Q_LSB.write()
    myDevice.TX2_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_tx2_gain(myDevice,myValue):
    "function to set TX2 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.TX2_AV_LSB.tx2_av_lsb=(myValue & 0xFF)
    myDevice.TX2_MSB.tx2_av_msb=(myValue & 0x700) >> 8
    myDevice.TX2_AV_LSB.write()
    myDevice.TX2_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
#--------------------TX3 phase and gain ctrl------------------------
def set_tx3_iphase(myDevice,myValue):
    "function to set TX3 I-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX3_I_LSB.tx3_i_lsb=(myValue & 0xFF)
    myDevice.TX3_MSB.tx3_i_msb=(myValue & 0x100) >> 8
    myDevice.TX3_I_LSB.write()
    myDevice.TX3_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
def set_tx3_qphase(myDevice,myValue):
    "function to set TX3 Q-phase 9-bit settings (9th bit is sign), 0 to 511"
    
    #set LSB and MSB of registers
    myDevice.TX3_Q_LSB.tx3_q_lsb=(myValue & 0xFF)
    myDevice.TX3_MSB.tx3_q_msb=(myValue & 0x100) >> 8
    myDevice.TX3_Q_LSB.write()
    myDevice.TX3_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
def set_tx3_gain(myDevice,myValue):
    "function to set TX3 Gain 11-bit settings, 0 to 2047"
    
    #set LSB and MSB of registers
    myDevice.TX3_AV_LSB.tx3_av_lsb=(myValue & 0xFF)
    myDevice.TX3_MSB.tx3_av_msb=(myValue & 0x700) >> 8
    myDevice.TX3_AV_LSB.write()
    myDevice.TX3_MSB.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)


#------------------RX0 Tail Current Control----------------
def set_rx0_cmb_icurr(myDevice,myValue):
    "function to set RX0 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX0.rx0_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX0.write()
    commit_reg_change(myDevice)
def set_rx0_cmb_qcurr(myDevice,myValue):
    "function to set RX0 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX0.rx0_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX0.write()
    commit_reg_change(myDevice)

#------------------RX1 Tail Current Control----------------
def set_rx1_cmb_icurr(myDevice,myValue):
    "function to set RX1 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX1.rx1_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX1.write()
    commit_reg_change(myDevice)
def set_rx1_cmb_qcurr(myDevice,myValue):
    "function to set RX1 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX1.rx1_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX1.write()
    commit_reg_change(myDevice)

#------------------RX2 Tail Current Control----------------
def set_rx2_cmb_icurr(myDevice,myValue):
    "function to set RX2 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX2.rx2_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX2.write()
    commit_reg_change(myDevice)
def set_rx2_cmb_qcurr(myDevice,myValue):
    "function to set RX2 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX2.rx2_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX2.write()
    commit_reg_change(myDevice)

#------------------RX3 Tail Current Control----------------
def set_rx3_cmb_icurr(myDevice,myValue):
    "function to set RX3 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX3.rx3_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX3.write()
    commit_reg_change(myDevice)
def set_rx3_cmb_qcurr(myDevice,myValue):
    "function to set RX3 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_RX3.rx3_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_RX3.write()
    commit_reg_change(myDevice)
    
#------------------TX0 Tail Current Control----------------
def set_tx0_cmb_icurr(myDevice,myValue):
    "function to set TX0 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX0.tx0_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX0.write()

def set_tx0_cmb_qcurr(myDevice,myValue):
    "function to set TX0 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX0.tx0_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX0.write()

def set_tx0_drv_curr(myDevice,myValue):
    "function to set TX0 driver tail current 5-bit settings, 0 to 31"
    
    #set value of register
    myDevice.TX0_FINAL_AV.tx0_final_av=(myValue & 0x1F)
    myDevice.TX0_FINAL_AV.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
#------------------TX1 Tail Current Control----------------
def set_tx1_cmb_icurr(myDevice,myValue):
    "function to set TX1 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX1.tx1_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX1.write()

def set_tx1_cmb_qcurr(myDevice,myValue):
    "function to set TX1 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX1.tx1_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX1.write()

def set_tx1_drv_curr(myDevice,myValue):
    "function to set TX1 driver tail current 5-bit settings, 0 to 31"
    
    #set value of register
    myDevice.TX1_FINAL_AV.tx1_final_av=(myValue & 0x1F)
    myDevice.TX1_FINAL_AV.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
#------------------TX2 Tail Current Control----------------
def set_tx2_cmb_icurr(myDevice,myValue):
    "function to set TX2 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX2.tx2_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX2.write()

def set_tx2_cmb_qcurr(myDevice,myValue):
    "function to set TX2 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX2.tx2_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX2.write()

def set_tx2_drv_curr(myDevice,myValue):
    "function to set TX2 driver tail current 5-bit settings, 0 to 31"
    
    #set value of register
    myDevice.TX2_FINAL_AV.tx2_final_av=(myValue & 0x1F)
    myDevice.TX2_FINAL_AV.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    
    
#------------------TX3 Tail Current Control----------------
def set_tx3_cmb_icurr(myDevice,myValue):
    "function to set TX3 combiner I-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX3.tx3_cmb_icurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX3.write()

def set_tx3_cmb_qcurr(myDevice,myValue):
    "function to set TX3 combiner Q-phase tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG0_TX3.tx3_cmb_qcurr_ctrl=(myValue & 0x3)
    myDevice.REG0_TX3.write()

def set_tx3_drv_curr(myDevice,myValue):
    "function to set TX3 driver tail current 5-bit settings, 0 to 31"
    
    #set value of register
    myDevice.TX3_FINAL_AV.tx3_final_av=(myValue & 0x1F)
    myDevice.TX3_FINAL_AV.write()
    
    #commit changes to the device
    commit_reg_change(myDevice)
    

#------------------TX LNA Tail Current Control----------------
def set_tx_lna_curr(myDevice,myValue):
    "function to set common TX LNA tail current 2-bit settings, 0 to 3"
    
    #set value of register
    myDevice.REG2_SPARE.txlna_curr_ctrl=(myValue & 0x3)
    myDevice.REG2_SPARE.write()
    

#------------------TX LNA Gain Control----------------
def set_tx_lna_gain(myDevice,myValue):
    "function to set common TX LNA gain 8-bit settings, 0 to 255"
    
    #set value of register
    myDevice.TX_LNA_CFG.TX_lna_gain_ctrl=(myValue & 0xFF)
    myDevice.TX_LNA_CFG.write()
    
    
#------------------RX and TX Low Power Down Mode----------------
def set_low_pdn_mode(myDevice,myValue):
    "function to set RX and TX in low power-down mode, 1 is low power mode enabled"
    # 0 is RX and TX both in normal power mode
    # 1 is RX in normal mode, TX in low power mode
    # 2 is RX in low power mode, TX in normal mode
    # 3 is RX and TX both in low power mode
    
    #set value of register
    myDevice.REG2_SPARE.low_pdn_curr_tx=(myValue & 0x01)
    myDevice.REG2_SPARE.low_pdn_curr_rx=(myValue & 0x02) >> 1
    myDevice.REG2_SPARE.write()
    
#------------------Temperature Sense to ADC Input----------------
def send_temp_to_adc(myDevice,myString):
    "function to send Ptat or Ztat temperature to ADC input"
    # myString can be "none", "ptat" or "ztat"
    # "none" disables connection to ADC input
    # "ptat" enables connection of PTAT voltage to ADC input
    # "ztat" enables connection of ZTAT voltage to ADC input
    
    #set value of register
    if (myString=="none"):
        myDevice.REG0_BGR.bgr_to_adc_ptat_volt_en=0x0
        myDevice.REG0_BGR.bgr_to_adc_ztat_volt_en=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
    elif (myString=="ptat"):
        myDevice.REG0_BGR.bgr_to_adc_ptat_volt_en=0x1
        myDevice.REG0_BGR.bgr_to_adc_ztat_volt_en=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x1
    elif (myString=="ztat"):
        myDevice.REG0_BGR.bgr_to_adc_ptat_volt_en=0x0
        myDevice.REG0_BGR.bgr_to_adc_ztat_volt_en=0x1
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x1
    else:
        print("Unknown argument, myString can only be ptat, ztat or none")
    #write register
    myDevice.REG0_BGR.write()
    myDevice.REG0_ADC.write()
    
#------------------GP7 to ADC Input----------------
def send_gp7_to_adc(myDevice,myValue):
    "function to connect GP7 pin to ADC input"
    # 0 disconnects GP7 to ADC input
    # 1 connects GP7 to ADC Input
    
    #set value of register
    myDevice.REG0_ADC.en_gp7_to_adc_sw=(myValue & 0x01)
    myDevice.REG0_ADC.write()
    
#------------------Select ADC Input Voltage----------------
def sel_adc_input(myDevice,myString):
    "function to select ADC input voltage"
    # myString can be "none", "pkdet", "temp", "atb" or "gp7"
    # "none" disable all connections to ADC input
    # "pkdet" selects peak detector output as ADC input
    # "temp" selects temperature as ADC input
    # "atb" selects atb as ADC input
    # "gp7" selects GP7 pin as ADC input
    
    #set value of register
    if (myString=="none"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x00
    elif (myString=="pkdet"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x1
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x00
    elif (myString=="temp"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x1
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x00
    elif (myString=="atb"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x1
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x00
    elif (myString == "gp4"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw = 0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw = 0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw = 0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x10
    elif (myString=="gp5"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x20
    elif (myString=="gp6"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x0
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x40
    elif (myString=="gp7"):
        myDevice.REG0_ADC.en_pkdet_to_adc_sw=0x0
        myDevice.REG0_ADC.en_temp_sense_to_adc_sw=0x0
        myDevice.REG0_ADC.en_atb_to_adc_sw=0x0
        myDevice.REG0_ADC.en_gp7_to_adc_sw=0x1
        myDevice.REG4_EXT_BIAS.rsvd7 = 0x00
    else:
        print("Unknown argument, myString can only be pkdet, temp, atb, gp7 or none")
    #write register
    myDevice.REG4_EXT_BIAS.write()
    myDevice.REG0_ADC.write()
    
#------------------Enable ADC----------------
def set_enable_adc(myDevice,myValue):
    "function to enable or disbale ADC, 1 is enable"
    
    #set value of register
    if (myValue==1):
       myDevice.ADC_CTRL.en_adc_osc=(myValue & 0x01)
       myDevice.ADC_CTRL.write()
       myDevice.ADC_CTRL.en_adc=(myValue & 0x01)
       myDevice.ADC_CTRL.write()
    elif (myValue==0):
       myDevice.ADC_CTRL.en_adc=(myValue & 0x01)
       myDevice.ADC_CTRL.write()
       myDevice.ADC_CTRL.en_adc_osc=(myValue & 0x01)
       myDevice.ADC_CTRL.write()
    
    

#------------------Read EOC of ADC----------------
def read_adc_eoc(myDevice):
    "function to read eoc status of ADC"
    
    # read value of register
    myValue=(myDevice.ADC_STS.read() & 0x01)
    return myValue

#------------------Read Output of ADC----------------
def read_adc_output(myDevice):
    "function to read 9-bit output of ADC"
    
    # read value of LSB 8bit
    myValue_LSB=(myDevice.ADC_IN_LSB.read() & 0xFF)
    # read value of MSB 1bit
    myValue_MSB=(myDevice.ADC_IN_MSB.read() & 0x01)
    # calculate output value
    myValue=(myValue_MSB << 8) | myValue_LSB
    return myValue

#-------------------PA Bias Enable-----------------------
def set_enable_PA_bias(myDevice,myValue):
    "function to enable PA Bias, 4-bit for 4-PA, 1 is enable"
    # Enable PA Bias 0, myValue=0x1
    # Enable PA Bias 1, myValue=0x2
    # Enable PA Bias 2, myValue=0x4
    # Enable PA Bias 3, myValue=0x8
    # Enable all PA Bias, myValue=0xF
    myDevice.TR_CTRL_4.en_pa_force=0x0F
    myDevice.TR_CTRL_4.en_pa_force_val=(myValue & 0x0F)
    myDevice.TR_CTRL_4.write()
    
#-------------------LNA Bias Enable-----------------------
def set_enable_LNA_bias(myDevice,myValue):
    "function to enable LNA Bias, 4-bit for 4-LNA, 1 is enable"
    # Enable LNA Bias 0, myValue=0x1
    # Enable LNA Bias 1, myValue=0x2
    # Enable LNA Bias 2, myValue=0x4
    # Enable LNA Bias 3, myValue=0x8
    # Enable all LNA Bias, myValue=0xF
    myDevice.TR_CTRL_3.en_lna_force=0x0F
    myDevice.TR_CTRL_3.en_lna_force_val=(myValue & 0x0F)
    myDevice.TR_CTRL_3.write()
    
#-------------------set PA Bias voltage-----------------------
def set_PA0_bias(myDevice,myValue):
    "function to set 8-bit PA0 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_PA0.DAC_CTRL_PA0=(myValue & 0xFF)
    myDevice.DAC_CTRL_PA0.write()
    
def set_PA1_bias(myDevice,myValue):
    "function to set 8-bit PA1 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_PA1.DAC_CTRL_PA1=(myValue & 0xFF)
    myDevice.DAC_CTRL_PA1.write()

def set_PA2_bias(myDevice,myValue):
    "function to set 8-bit PA2 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_PA2.DAC_CTRL_PA2=(myValue & 0xFF)
    myDevice.DAC_CTRL_PA2.write()

def set_PA3_bias(myDevice,myValue):
    "function to set 8-bit PA3 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_PA3.DAC_CTRL_PA3=(myValue & 0xFF)
    myDevice.DAC_CTRL_PA3.write()  
    
#-------------------set LNA Bias voltage-----------------------
def set_LNA0_bias(myDevice,myValue):
    "function to set 8-bit LNA0 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_LNA0.DAC_CTRL_LNA0=(myValue & 0xFF)
    myDevice.DAC_CTRL_LNA0.write()
    
def set_LNA1_bias(myDevice,myValue):
    "function to set 8-bit LNA1 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_LNA1.DAC_CTRL_LNA1=(myValue & 0xFF)
    myDevice.DAC_CTRL_LNA1.write()

def set_LNA2_bias(myDevice,myValue):
    "function to set 8-bit LNA2 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_LNA2.DAC_CTRL_LNA2=(myValue & 0xFF)
    myDevice.DAC_CTRL_LNA2.write()

def set_LNA3_bias(myDevice,myValue):
    "function to set 8-bit LNA3 Bias Voltage Value, 0 to 255"
    myDevice.DAC_CTRL_LNA3.DAC_CTRL_LNA3=(myValue & 0xFF)
    myDevice.DAC_CTRL_LNA3.write()
    
#-------------------------TX ATB----------------------------
def set_tx0_atb(myDevice, myValue):
    "function to set 14-bit TX0 ATB value, only single bit is 1 at any time"
    if (myValue<=0x80):
        myDevice.REG1_TX0.tx0_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_TX0.tx0_obs_9_8=0x0
        myDevice.REG0_SPARE.ch0_tx_obs_13_10=0x0
    elif (myValue > 0x80) & (myValue <=0x200):
        myDevice.REG1_TX0.tx0_obs_7_0=0x0
        myDevice.REG0_TX0.tx0_obs_9_8=(myValue & 0x300) >> 8
        myDevice.REG0_SPARE.ch0_tx_obs_13_10=0x0
    elif (myValue > 0x200):
        myDevice.REG1_TX0.tx0_obs_7_0=0x0
        myDevice.REG0_TX0.tx0_obs_9_8=0x0
        myDevice.REG0_SPARE.ch0_tx_obs_13_10=(myValue & 0x3C00) >> 10
    myDevice.REG1_TX0.write()
    myDevice.REG0_TX0.write()
    myDevice.REG0_SPARE.write()
    
def set_tx1_atb(myDevice, myValue):
    "function to set 14-bit TX1 ATB value, only single bit is 1 at any time"
    if (myValue<=0x80):
        myDevice.REG1_TX1.tx1_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_TX1.tx1_obs_9_8=0x0
        myDevice.REG0_SPARE.ch1_tx_obs_13_10=0x0
    elif (myValue > 0x80) & (myValue <=0x200):
        myDevice.REG1_TX1.tx1_obs_7_0=0x0
        myDevice.REG0_TX1.tx1_obs_9_8=(myValue & 0x300) >> 8
        myDevice.REG0_SPARE.ch1_tx_obs_13_10=0x0
    elif (myValue > 0x200):
        myDevice.REG1_TX1.tx1_obs_7_0=0x0
        myDevice.REG0_TX1.tx1_obs_9_8=0x0
        myDevice.REG0_SPARE.ch1_tx_obs_13_10=(myValue & 0x3C00) >> 10
    myDevice.REG1_TX1.write()
    myDevice.REG0_TX1.write()
    myDevice.REG0_SPARE.write()
    
def set_tx2_atb(myDevice, myValue):
    "function to set 14-bit TX2 ATB value, only single bit is 1 at any time"
    if (myValue<=0x80):
        myDevice.REG1_TX2.tx2_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_TX2.tx2_obs_9_8=0x0
        myDevice.REG1_SPARE.ch2_tx_obs_13_10=0x0
    elif (myValue > 0x80) & (myValue <=0x200):
        myDevice.REG1_TX2.tx2_obs_7_0=0x0
        myDevice.REG0_TX2.tx2_obs_9_8=(myValue & 0x300) >> 8
        myDevice.REG1_SPARE.ch2_tx_obs_13_10=0x0
    elif (myValue > 0x200):
        myDevice.REG1_TX2.tx2_obs_7_0=0x0
        myDevice.REG0_TX2.tx2_obs_9_8=0x0
        myDevice.REG1_SPARE.ch2_tx_obs_13_10=(myValue & 0x3C00) >> 10
    myDevice.REG1_TX2.write()
    myDevice.REG0_TX2.write()
    myDevice.REG1_SPARE.write()
    
def set_tx3_atb(myDevice, myValue):
    "function to set 14-bit TX3 ATB value, only single bit is 1 at any time"
    if (myValue<=0x80):
        myDevice.REG1_TX3.tx3_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_TX3.tx3_obs_9_8=0x0
        myDevice.REG1_SPARE.ch3_tx_obs_13_10=0x0
    elif (myValue > 0x80) & (myValue <=0x200):
        myDevice.REG1_TX3.tx3_obs_7_0=0x0
        myDevice.REG0_TX3.tx3_obs_9_8=(myValue & 0x300) >> 8
        myDevice.REG1_SPARE.ch3_tx_obs_13_10=0x0
    elif (myValue > 0x200):
        myDevice.REG1_TX3.tx3_obs_7_0=0x0
        myDevice.REG0_TX3.tx3_obs_9_8=0x0
        myDevice.REG1_SPARE.ch3_tx_obs_13_10=(myValue & 0x3C00) >> 10
    myDevice.REG1_TX3.write()
    myDevice.REG0_TX3.write()
    myDevice.REG1_SPARE.write()
    
#-------------------------RX ATB----------------------------
def set_rx0_atb(myDevice, myValue):
    "function to set 12-bit RX0 ATB value, only single bit is 1 at any time"
    if (myValue<=0xFF):
        myDevice.REG1_RX0.rx0_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_RX0.rx0_obs_11_8=0x0
    elif (myValue > 0xFF):
        myDevice.REG1_RX0.rx0_obs_7_0=0x0
        myDevice.REG0_RX0.rx0_obs_11_8=(myValue & 0xF00) >> 8
    myDevice.REG1_RX0.write()
    myDevice.REG0_RX0.write()
    
def set_rx1_atb(myDevice, myValue):
    "function to set 12-bit RX1 ATB value, only single bit is 1 at any time"
    if (myValue<=0xFF):
        myDevice.REG1_RX1.rx1_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_RX1.rx1_obs_11_8=0x0
    elif (myValue > 0xFF):
        myDevice.REG1_RX1.rx1_obs_7_0=0x0
        myDevice.REG0_RX1.rx1_obs_11_8=(myValue & 0xF00) >> 8
    myDevice.REG1_RX1.write()
    myDevice.REG0_RX1.write() 
    
def set_rx2_atb(myDevice, myValue):
    "function to set 12-bit RX2 ATB value, only single bit is 1 at any time"
    if (myValue<=0xFF):
        myDevice.REG1_RX2.rx2_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_RX2.rx2_obs_11_8=0x0
    elif (myValue > 0xFF):
        myDevice.REG1_RX2.rx2_obs_7_0=0x0
        myDevice.REG0_RX2.rx2_obs_11_8=(myValue & 0xF00) >> 8
    myDevice.REG1_RX2.write()
    myDevice.REG0_RX2.write()
    
def set_rx3_atb(myDevice, myValue):
    "function to set 12-bit RX3 ATB value, only single bit is 1 at any time"
    if (myValue<=0xFF):
        myDevice.REG1_RX3.rx3_obs_7_0=(myValue & 0xFF) >> 0
        myDevice.REG0_RX3.rx3_obs_11_8=0x0
    elif (myValue > 0xFF):
        myDevice.REG1_RX3.rx3_obs_7_0=0x0
        myDevice.REG0_RX3.rx3_obs_11_8=(myValue & 0xF00) >> 8
    myDevice.REG1_RX3.write()
    myDevice.REG0_RX3.write()      
    
#--------------------PA Bias ATB-------------------
def set_PA0_atb(myDevice,myValue):
    "function to set 1-bit PA0 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x01)
    myDevice.REG0_EXT_BIAS.write()
    
def set_PA1_atb(myDevice,myValue):
    "function to set 1-bit PA1 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x02)
    myDevice.REG0_EXT_BIAS.write()    

def set_PA2_atb(myDevice,myValue):
    "function to set 1-bit PA2 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x04)
    myDevice.REG0_EXT_BIAS.write()    

def set_PA3_atb(myDevice,myValue):
    "function to set 1-bit PA3 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x08)
    myDevice.REG0_EXT_BIAS.write() 

#--------------------LNA Bias ATB-------------------
def set_LNA0_atb(myDevice,myValue):
    "function to set 1-bit LNA0 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x10)
    myDevice.REG0_EXT_BIAS.write()
    
def set_LNA1_atb(myDevice,myValue):
    "function to set 1-bit LNA1 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x20)
    myDevice.REG0_EXT_BIAS.write()    

def set_LNA2_atb(myDevice,myValue):
    "function to set 1-bit LNA2 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x40)
    myDevice.REG0_EXT_BIAS.write()    

def set_LNA3_atb(myDevice,myValue):
    "function to set 1-bit LNA3 Bias ATB value"
    myDevice.REG0_EXT_BIAS.ext_bias_top_obs=(myValue & 0x80)
    myDevice.REG0_EXT_BIAS.write()     
    
#----------------------TX LNA ATB-----------------------
def set_txlna_atb(myDevice, myValue):
    "function to set 3-bit TX LNA ATB value, only single bit is 1 at a time"
    myDevice.REG2_SPARE.txlna_obs=(myValue & 0x07)
    myDevice.REG2_SPARE.write()
    
#---------------------Peak Detect ATB--------------------
def set_pkdet0_atb(myDevice, myValue):
    "function to set 1-bit peak det0 ATB value"
    myDevice.REG3_SPARE.pk_det_obs=(myValue & 0x01) << 0
    myDevice.REG3_SPARE.write()

def set_pkdet1_atb(myDevice, myValue):
    "function to set 1-bit peak det1 ATB value"
    myDevice.REG3_SPARE.pk_det_obs=(myValue & 0x01) << 1
    myDevice.REG3_SPARE.write()

def set_pkdet2_atb(myDevice, myValue):
    "function to set 1-bit peak det2 ATB value"
    myDevice.REG3_SPARE.pk_det_obs=(myValue & 0x01) << 2
    myDevice.REG3_SPARE.write()

def set_pkdet3_atb(myDevice, myValue):
    "function to set 1-bit peak det3 ATB value"
    myDevice.REG3_SPARE.pk_det_obs=(myValue & 0x01) << 3
    myDevice.REG3_SPARE.write()

#----------------------Temp Sense ATB---------------------
def set_temp_sense_atb(myDevice, myValue):
    "function to set 1-bit Temp Sense ATB value"
    myDevice.REG3_SPARE.temp_sense_obs=(myValue & 0x01)
    myDevice.REG3_SPARE.write()

def set_temp_sense_adc_atb(myDevice, myValue):
    "function to set 1-bit Temp Sense ADC ATB value"
    myDevice.REG3_SPARE.temp_sense_adc_obs=(myValue & 0x01)
    myDevice.REG3_SPARE.write() 
    
#--------------------Clear ATB--------------------
def clear_all_atb(myDevice):
    "function to disconnect or clear all ATB switches on the chip"
    # clear tx atb
    set_tx0_atb(myDevice, 0x0)
    set_tx1_atb(myDevice, 0x0)
    set_tx2_atb(myDevice, 0x0)
    set_tx3_atb(myDevice, 0x0)
    set_txlna_atb(myDevice, 0x0)
    
    # clear rx atb
    set_rx0_atb(myDevice, 0x0)
    set_rx1_atb(myDevice, 0x0)
    set_rx2_atb(myDevice, 0x0)
    set_rx3_atb(myDevice, 0x0)
    
    # clear PA atb
    set_PA0_atb(myDevice, 0x0)
    set_PA1_atb(myDevice, 0x0)
    set_PA2_atb(myDevice, 0x0)
    set_PA3_atb(myDevice, 0x0)
            
    # clear LNA atb
    set_LNA0_atb(myDevice, 0x0)
    set_LNA1_atb(myDevice, 0x0)
    set_LNA2_atb(myDevice, 0x0)
    set_LNA3_atb(myDevice, 0x0)

    # clear pkdet atb
    set_pkdet0_atb(myDevice, 0x0)
    set_pkdet1_atb(myDevice, 0x0)
    set_pkdet2_atb(myDevice, 0x0)
    set_pkdet3_atb(myDevice, 0x0)
    
    # clear temp sense atb
    set_temp_sense_atb(myDevice, 0x0)
    set_temp_sense_adc_atb(myDevice, 0x0)
    
#--------------Peak Detector Enable------------------
def set_enable_pkdet(myDevice, myValue):
    "function to enable Peak Detector, 4-bit for 4-pkdet, 1 is enable"
    # Enable pkdet0, myValue=0x1
    # Enable pkdet1, myValue=0x2
    # Enable pkdet2, myValue=0x4
    # Enable pkdet3, myValue=0x8
    # Enable all pkdet, myValue=0xF
    myDevice.TR_CTRL_2.det_en_force=0x0F
    myDevice.TR_CTRL_2.det_en_force_val=(myValue & 0x0F)
    myDevice.TR_CTRL_2.write()

#---------------------TX Bias Mode------------------
def set_TX_bias_mode(myDevice, myString):
    " function to set TX Bias Mode -> LOW or NOM "
    if (myString == 'MAX'):
        set_tx_lna_curr(myDevice, 3)
        
        set_tx0_cmb_icurr(myDevice, 3)
        set_tx0_cmb_qcurr(myDevice, 3)
        set_tx1_cmb_icurr(myDevice, 3)
        set_tx1_cmb_qcurr(myDevice, 3)
        set_tx2_cmb_icurr(myDevice, 3)
        set_tx2_cmb_qcurr(myDevice, 3)
        set_tx3_cmb_icurr(myDevice, 3)
        set_tx3_cmb_qcurr(myDevice, 3)
        
        set_tx0_drv_curr(myDevice, 31)
        set_tx1_drv_curr(myDevice, 31)
        set_tx2_drv_curr(myDevice, 31)
        set_tx3_drv_curr(myDevice, 31)
        
    if (myString == 'LOW'):
        set_tx_lna_curr(myDevice, 0)
        
        set_tx0_cmb_icurr(myDevice, 0)
        set_tx0_cmb_qcurr(myDevice, 0)
        set_tx1_cmb_icurr(myDevice, 0)
        set_tx1_cmb_qcurr(myDevice, 0)
        set_tx2_cmb_icurr(myDevice, 0)
        set_tx2_cmb_qcurr(myDevice, 0)
        set_tx3_cmb_icurr(myDevice, 0)
        set_tx3_cmb_qcurr(myDevice, 0)
        
        set_tx0_drv_curr(myDevice, 12)
        set_tx1_drv_curr(myDevice, 12)
        set_tx2_drv_curr(myDevice, 12)
        set_tx3_drv_curr(myDevice, 12)
    elif (myString == 'NOM') :
        set_tx_lna_curr(myDevice, 3)
        
        set_tx0_cmb_icurr(myDevice, 1)
        set_tx0_cmb_qcurr(myDevice, 1)
        set_tx1_cmb_icurr(myDevice, 1)
        set_tx1_cmb_qcurr(myDevice, 1)
        set_tx2_cmb_icurr(myDevice, 1)
        set_tx2_cmb_qcurr(myDevice, 1)
        set_tx3_cmb_icurr(myDevice, 1)
        set_tx3_cmb_qcurr(myDevice, 1)
        
        set_tx0_drv_curr(myDevice, 31)
        set_tx1_drv_curr(myDevice, 31)
        set_tx2_drv_curr(myDevice, 31)
        set_tx3_drv_curr(myDevice, 31)
    elif (myString == '2W_FEM') :
        set_tx_lna_curr(myDevice, 0)
        
        set_tx0_cmb_icurr(myDevice, 0)
        set_tx0_cmb_qcurr(myDevice, 0)
        set_tx1_cmb_icurr(myDevice, 0)
        set_tx1_cmb_qcurr(myDevice, 0)
        set_tx2_cmb_icurr(myDevice, 0)
        set_tx2_cmb_qcurr(myDevice, 0)
        set_tx3_cmb_icurr(myDevice, 0)
        set_tx3_cmb_qcurr(myDevice, 0)
        
        set_tx0_drv_curr(myDevice, 16)
        set_tx1_drv_curr(myDevice, 16)
        set_tx2_drv_curr(myDevice, 16)
        set_tx3_drv_curr(myDevice, 16)
    elif (myString == '5W_FEM') :
        set_tx_lna_curr(myDevice, 3)
        
        set_tx0_cmb_icurr(myDevice, 1)
        set_tx0_cmb_qcurr(myDevice, 1)
        set_tx1_cmb_icurr(myDevice, 1)
        set_tx1_cmb_qcurr(myDevice, 1)
        set_tx2_cmb_icurr(myDevice, 1)
        set_tx2_cmb_qcurr(myDevice, 1)
        set_tx3_cmb_icurr(myDevice, 1)
        set_tx3_cmb_qcurr(myDevice, 1)
        
        set_tx0_drv_curr(myDevice, 26)
        set_tx1_drv_curr(myDevice, 26)
        set_tx2_drv_curr(myDevice, 26)
        set_tx3_drv_curr(myDevice, 26)
    
    return    

#--------------------------RX BIAS MODE-------------------
def set_RX_bias_mode(myDevice, myString):
    " function to set RX Bias Mode -> LOW or NOM "
    if (myString == 'LOW'):
        set_rx0_cmb_icurr(myDevice, 0)
        set_rx0_cmb_qcurr(myDevice, 0)

        set_rx1_cmb_icurr(myDevice, 0)
        set_rx1_cmb_qcurr(myDevice, 0)

        set_rx2_cmb_icurr(myDevice, 0)
        set_rx2_cmb_qcurr(myDevice, 0)

        set_rx3_cmb_icurr(myDevice, 0)
        set_rx3_cmb_qcurr(myDevice, 0)
    elif (myString == 'NOM') :
        set_rx0_cmb_icurr(myDevice, 3)
        set_rx0_cmb_qcurr(myDevice, 3)

        set_rx1_cmb_icurr(myDevice, 3)
        set_rx1_cmb_qcurr(myDevice, 3)

        set_rx2_cmb_icurr(myDevice, 3)
        set_rx2_cmb_qcurr(myDevice, 3)

        set_rx3_cmb_icurr(myDevice, 3)
        set_rx3_cmb_qcurr(myDevice, 3)
    elif (myString == 'LOW_V2') :
        set_rx0_cmb_icurr(myDevice, 0)
        set_rx0_cmb_qcurr(myDevice, 2)

        set_rx1_cmb_icurr(myDevice, 0)
        set_rx1_cmb_qcurr(myDevice, 2)

        set_rx2_cmb_icurr(myDevice, 0)
        set_rx2_cmb_qcurr(myDevice, 2)

        set_rx3_cmb_icurr(myDevice, 0)
        set_rx3_cmb_qcurr(myDevice, 2)
    return  