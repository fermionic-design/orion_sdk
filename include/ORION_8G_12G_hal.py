import pandas as pd
import math
import time
from SPI import *

class ORION_8G_12G_hal:
    def __init__(self, orion_csr, orion_lut, spi, version='v2'):
        self.version = version
        self.orion_csr = orion_csr
        self.orion_lut = orion_lut
        self.tr_mode = 0
        self.trx_mode = 0
        self.use_reg_inp_for_stg2 = 1
        self.spi = spi

    def read_column_from_excel(self, file_path, sheet_name, column_name):
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
            
    def calc_phase_wrapped(self, input_phase):
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
        
    def init_lut(self, tx_10G_gain_lut_xls,
                 tx_10G_phase_lut_xls, 
                 rx_9G_gain_lut_xls, 
                 rx_9G_phase_lut_xls, 
                 rx_11G_gain_lut_xls, 
                 rx_11G_phase_lut_xls):
               
        # file_path = r'../../../final_lut/RX_Phase_LUT_9GHz_NomBias.xlsx'  # Provide the path to your Excel file
        sheet_name = 'Sheet1'  # Specify the sheet name
        column_name = 'I-Code'  # Specify the user-defined column name
        self.i_code = self.read_column_from_excel(rx_9G_phase_lut_xls, sheet_name, column_name)
        self.i_code = self.i_code.astype(int)
        column_name = 'Q-Code'  # Specify the user-defined column name
        self.q_code = self.read_column_from_excel(rx_9G_phase_lut_xls, sheet_name, column_name)
        self.q_code = self.q_code.astype(int)
        column_name = 'Gain dB 9.0GHz'  # Specify the user-defined column name
        const_gain_val = self.read_column_from_excel(rx_9G_phase_lut_xls, sheet_name, column_name)

        # file_path = r'../../../final_lut/RX_Phase_LUT_11GHz_NomBias.xlsx'  # Provide the path to your Excel file
        sheet_name = 'Sheet1'  # Specify the sheet name
        column_name = 'I-Code'  # Specify the user-defined column name
        self.i_code_1 = self.read_column_from_excel(rx_11G_phase_lut_xls, sheet_name, column_name)
        self.i_code_1 = self.i_code_1.astype(int)
        column_name = 'Q-Code'  # Specify the user-defined column name
        self.q_code_1 = self.read_column_from_excel(rx_11G_phase_lut_xls, sheet_name, column_name)
        self.q_code_1 = self.q_code_1.astype(int)
        column_name = 'Gain dB 11.0GHz'  # Specify the user-defined column name
        const_gain_val_1 = self.read_column_from_excel(rx_11G_phase_lut_xls, sheet_name, column_name)

        # file_path = r'../../../final_lut/RX_Gain_LUT_9GHz_NomBias.xlsx'  # Provide the path to your Excel file
        sheet_name = 'Sheet1'  # Specify the sheet name
        column_name = 'Gain Code'  # Specify the user-defined column name
        self.gain_code = self.read_column_from_excel(rx_9G_gain_lut_xls, sheet_name, column_name)
        self.gain_code = self.gain_code.astype(int)
        column_name = 'Phase Deg 9.0GHz'  # Specify the user-defined column name
        const_ph_val = self.read_column_from_excel(rx_9G_gain_lut_xls, sheet_name, column_name)

        # file_path = r'../../../final_lut/RX_Gain_LUT_11GHz_NomBias.xlsx'  # Provide the path to your Excel file
        sheet_name = 'Sheet1'  # Specify the sheet name
        column_name = 'Gain Code'  # Specify the user-defined column name
        self.gain_code_1 = self.read_column_from_excel(rx_11G_gain_lut_xls, sheet_name, column_name)
        self.gain_code_1 = self.gain_code_1.astype(int)
        column_name = 'Phase Deg 11.0GHz'  # Specify the user-defined column name
        const_ph_val_1 = self.read_column_from_excel(rx_11G_gain_lut_xls, sheet_name, column_name)
        
        """Populating LUT for RX"""
        gain_lut_len=64
        phase_pts_in_gain_lut=4
        """Phase error Calculation"""
        ph_err = [0] * gain_lut_len
        ph_err_idx = [0] * gain_lut_len
        ph_err_idx_signed = [0] * gain_lut_len
        for i in range (gain_lut_len):
            ph_err[i]=0
            for j in range(phase_pts_in_gain_lut):
                phase_delta=self.calc_phase_wrapped(const_ph_val[0+(j*gain_lut_len)] - const_ph_val[i+(j*gain_lut_len)])
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
                phase_delta_1=self.calc_phase_wrapped(const_ph_val_1[0+(j*gain_lut_len)] - const_ph_val_1[i+(j*gain_lut_len)])
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
            rx_phase_val_i[0][0][i] = self.i_code[i]
            rx_phase_val_q[0][0][i] = self.q_code[i]
            rx_gain_err[0][0][i] = 0 if gain_corr_dis else g_err_idx_signed[i]
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + freq*8
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_PHASE_MEM.pos = i % 16;
            self.orion_lut.RX_PHASE_MEM.rx_freq_val = 0
            self.orion_lut.RX_PHASE_MEM.rx_temp_val = 0
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_i = rx_phase_val_i[0][0][i]
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_q = rx_phase_val_q[0][0][i]
            self.orion_lut.RX_PHASE_MEM.rx_gain_err = rx_gain_err[0][0][i]
            self.orion_lut.RX_PHASE_MEM.write()

        """Write RX Gain mem """
        rx_gain_val = [[[0 for _ in range(64)] for _ in range(4)] for _ in range(2)]
        rx_ph_err = [[[0 for _ in range(64)] for _ in range(4)] for _ in range(2)]


        freq = 0
        temp = 0
        i = 0    
        page_id = 16
        page_id = math.floor(i/16) + 16 + freq*4

        for i in range (gain_lut_len):
            rx_gain_val[0][0][i] = self.gain_code[i];
            rx_ph_err[0][0][i] = 0 if phase_corr_dis else ph_err_idx_signed[i];
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + 16 + freq*4
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_GAIN_MEM.pos = i % 16;
            self.orion_lut.RX_GAIN_MEM.rx_freq_val = 0
            self.orion_lut.RX_GAIN_MEM.rx_temp_val = 0
            self.orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[0][0][i]
            self.orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[0][0][i]
            self.orion_lut.RX_GAIN_MEM.write()
            
        """Programming LUT for frequency ID 1 """
        """Write RX Phase mem Freq 1"""
        freq = 1
        temp = 0
        i = 0    
        page_id = 0
        page_id = math.floor(i/16) + freq*8

        for i in range (128):
            rx_phase_val_i[1][0][i] = self.i_code_1[i]
            rx_phase_val_q[1][0][i] = self.q_code_1[i]
            rx_gain_err[1][0][i] = 0 if gain_corr_dis else g_err_idx_signed_1[i]
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + freq*8
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_PHASE_MEM.pos = i % 16;
            self.orion_lut.RX_PHASE_MEM.rx_freq_val = 0
            self.orion_lut.RX_PHASE_MEM.rx_temp_val = 0
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_i = rx_phase_val_i[1][0][i]
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_q = rx_phase_val_q[1][0][i]
            self.orion_lut.RX_PHASE_MEM.rx_gain_err = rx_gain_err[1][0][i]
            self.orion_lut.RX_PHASE_MEM.write()

        """Write RX Gain mem Freq 1"""
        freq = 1
        temp = 0
        i = 0    
        page_id = 16
        page_id = math.floor(i/16) + 16 + freq*4


        for i in range (gain_lut_len):
            rx_gain_val[1][0][i] = self.gain_code_1[i];
            rx_ph_err[1][0][i] = 0 if phase_corr_dis else ph_err_idx_signed_1[i];
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + 16 + freq*4
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_GAIN_MEM.pos = i % 16;
            self.orion_lut.RX_GAIN_MEM.rx_freq_val = 0
            self.orion_lut.RX_GAIN_MEM.rx_temp_val = 0
            self.orion_lut.RX_GAIN_MEM.rx_gain_val = rx_gain_val[1][0][i]
            self.orion_lut.RX_GAIN_MEM.rx_ph_err = rx_ph_err[1][0][i]
            self.orion_lut.RX_GAIN_MEM.write()
        
        """Populating LUT for TX"""
        sheet_name_tx = 'Sheet1'  # Specify the sheet name
        column_name_tx = 'I-Code'  # Specify the user-defined column name
        self.i_code_tx = self.read_column_from_excel(tx_10G_phase_lut_xls, sheet_name_tx, column_name_tx)
        self.i_code_tx = self.i_code_tx.astype(int)
        print(self.i_code_tx)
        column_name_tx = 'Q-Code'  # Specify the user-defined column name
        self.q_code_tx = self.read_column_from_excel(tx_10G_phase_lut_xls, sheet_name_tx, column_name_tx)
        self.q_code_tx = self.q_code_tx.astype(int)
        print(self.q_code_tx)


        sheet_name_tx = 'Sheet1'  # Specify the sheet name
        column_name_tx = 'Gain Code'  # Specify the user-defined column name
        self.gain_code_tx = self.read_column_from_excel(tx_10G_gain_lut_xls, sheet_name_tx, column_name_tx)
        self.gain_code_tx = self.gain_code_tx.astype(int)

        """Write TX Phase mem """
        self.orion_csr.PAGE_ID.page_id = 0x18
        self.orion_csr.PAGE_ID.write()
        self.orion_csr.PAGE_ID.read()
        # self.orion_csr.PAGE_ID.display()

        i=0 
        tx_phase_val_i = [0] * 128
        tx_phase_val_q = [0] * 128
        for i in range (128) :
            tx_phase_val_i[i] = self.i_code_tx[i]
            tx_phase_val_q[i] = self.q_code_tx[i]
            if i == 64 :
                self.orion_csr.PAGE_ID.page_id = 0x19
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
                
            self.orion_lut.TX_PHASE_MEM.pos = i % 64;
            self.orion_lut.TX_PHASE_MEM.tx_phase_val_i = tx_phase_val_i[i]
            self.orion_lut.TX_PHASE_MEM.tx_phase_val_q = tx_phase_val_q[i]
            self.orion_lut.TX_PHASE_MEM.write()

        """Write TX Gain mem """
        self.orion_csr.PAGE_ID.page_id = 0x1A
        self.orion_csr.PAGE_ID.write()
        self.orion_csr.PAGE_ID.read()
        # self.orion_csr.PAGE_ID.display()
            
        i=0 
        tx_gain_val = [0] * 64
        tx_final_gain_val = [0] * 64

        for i in range (64) :
            tx_gain_val[i] = self.gain_code_tx[i]
            tx_final_gain_val[i] = 0 # final av is programmed to 0, and desired final_av is forced in init_tx defination
                
            self.orion_lut.TX_GAIN_MEM.pos = i
            self.orion_lut.TX_GAIN_MEM.tx_gain_val = tx_gain_val[i]
            self.orion_lut.TX_GAIN_MEM.tx_final_gain_val = tx_final_gain_val[i]
            self.orion_lut.TX_GAIN_MEM.write()

        #--------------------------------------------------------
    def init_lut_new(self, tx_gain_lut_xls,
                 tx_phase_lut_xls, 
                 rx_f1_gain_lut_xls, 
                 rx_f1_phase_lut_xls, 
                 rx_f2_gain_lut_xls, 
                 rx_f2_phase_lut_xls):
        
        sheet_name = 'Sheet1'  # Specify the sheet name
        
        self.i_code = self.read_column_from_excel(rx_f1_phase_lut_xls, sheet_name, 'I-Code')
        self.i_code = self.i_code.astype(int)
        self.q_code = self.read_column_from_excel(rx_f1_phase_lut_xls, sheet_name, 'Q-Code')
        self.q_code = self.q_code.astype(int)
        g_err_idx_signed = self.read_column_from_excel(rx_f1_phase_lut_xls, sheet_name, 'Gain Error')
    
        self.i_code_1 = self.read_column_from_excel(rx_f2_phase_lut_xls, sheet_name, 'I-Code')
        self.i_code_1 = self.i_code_1.astype(int)
        self.q_code_1 = self.read_column_from_excel(rx_f2_phase_lut_xls, sheet_name, 'Q-Code')
        self.q_code_1 = self.q_code_1.astype(int)
        g_err_idx_signed_1 = self.read_column_from_excel(rx_f2_phase_lut_xls, sheet_name, 'Gain Error')

        self.gain_code = self.read_column_from_excel(rx_f1_gain_lut_xls, sheet_name, 'Av')
        self.gain_code = self.gain_code.astype(int)
        # ph_err_idx_signed = self.read_column_from_excel(rx_f1_gain_lut_xls, sheet_name, 'Phase error(9.0 GHz)')
        ph_err_idx_signed = self.read_column_from_excel(rx_f1_gain_lut_xls, sheet_name, 'Phase Err Code')
    
        gain_code_1 = self.read_column_from_excel(rx_f2_gain_lut_xls, sheet_name, 'Av')
        gain_code_1 = gain_code_1.astype(int)
        # ph_err_idx_signed_1 = self.read_column_from_excel(rx_f2_gain_lut_xls, sheet_name, 'Phase error(9.0 GHz)')
        ph_err_idx_signed_1 = self.read_column_from_excel(rx_f2_gain_lut_xls, sheet_name, 'Phase Err Code')
    
        gain_lut_len=64        
        phase_lut_len=128
        
        """Populating LUT for RX"""
        """Write RX Phase mem """
        freq = 0
        temp = 0
        i = 0
        page_id = math.floor(i/16) + freq*8
        
        for i in range (128):
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + freq*8
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_PHASE_MEM.pos = i % 16;
            self.orion_lut.RX_PHASE_MEM.rx_freq_val = freq
            self.orion_lut.RX_PHASE_MEM.rx_temp_val = temp
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_i = self.i_code[i]
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_q = self.q_code[i]
            self.orion_lut.RX_PHASE_MEM.rx_gain_err = g_err_idx_signed[i]
            self.orion_lut.RX_PHASE_MEM.write()
    
        """Write RX Gain mem """
        freq = 0
        temp = 0 
        i = 0
        page_id = math.floor(i/16) + 16 + freq*4
    
        for i in range (gain_lut_len):
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + 16 + freq*4
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_GAIN_MEM.pos = i % 16;
            self.orion_lut.RX_GAIN_MEM.rx_freq_val = freq
            self.orion_lut.RX_GAIN_MEM.rx_temp_val = temp
            self.orion_lut.RX_GAIN_MEM.rx_gain_val = self.gain_code[i];
            self.orion_lut.RX_GAIN_MEM.rx_ph_err = ph_err_idx_signed[i];
            self.orion_lut.RX_GAIN_MEM.write()
    
            
        """Programming LUT for frequency ID 1 """
        """Write RX Phase mem Freq 1"""
        freq = 1
        temp = 0   
        i = 0
        page_id = math.floor(i/16) + freq*8
    
    
        for i in range (128):
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + freq*8
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_PHASE_MEM.pos = i % 16;
            self.orion_lut.RX_PHASE_MEM.rx_freq_val = freq
            self.orion_lut.RX_PHASE_MEM.rx_temp_val = temp
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_i = self.i_code_1[i]
            self.orion_lut.RX_PHASE_MEM.rx_phase_val_q = self.q_code_1[i]
            self.orion_lut.RX_PHASE_MEM.rx_gain_err = g_err_idx_signed_1[i]
            self.orion_lut.RX_PHASE_MEM.write()
    
        """Write RX Gain mem Freq 1"""
        freq = 1
        temp = 0
        i = 0    
        page_id = math.floor(i/16) + 16 + freq*4
        
        for i in range (gain_lut_len):
            if i%16 == 0:
                self.orion_csr.PAGE_ID.page_id = math.floor(i/16) + 16 + freq*4
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
            self.orion_lut.RX_GAIN_MEM.pos = i % 16;
            self.orion_lut.RX_GAIN_MEM.rx_freq_val = freq
            self.orion_lut.RX_GAIN_MEM.rx_temp_val = temp
            self.orion_lut.RX_GAIN_MEM.rx_gain_val = gain_code_1[i];
            self.orion_lut.RX_GAIN_MEM.rx_ph_err = ph_err_idx_signed_1[i];
            self.orion_lut.RX_GAIN_MEM.write()
    
        
        """Populating LUT for TX"""
        sheet_name_tx = 'Sheet1'  # Specify the sheet name
        column_name_tx = 'I-Code'  # Specify the user-defined column name
        self.i_code_tx = self.read_column_from_excel(tx_phase_lut_xls, sheet_name_tx, column_name_tx)
        self.i_code_tx = self.i_code_tx.astype(int)
        # print(self.i_code_tx)
        column_name_tx = 'Q-Code'  # Specify the user-defined column name
        self.q_code_tx = self.read_column_from_excel(tx_phase_lut_xls, sheet_name_tx, column_name_tx)
        self.q_code_tx = self.q_code_tx.astype(int)
        # print(self.q_code_tx)
    
    
        sheet_name_tx = 'Sheet1'  # Specify the sheet name
        column_name_tx = 'Gain Code'  # Specify the user-defined column name
        gain_code_tx = self.read_column_from_excel(tx_gain_lut_xls, sheet_name_tx, column_name_tx)
        gain_code_tx = gain_code_tx.astype(int)
    
        """Write TX Phase mem """
        self.orion_csr.PAGE_ID.page_id = 0x18
        self.orion_csr.PAGE_ID.write()
        self.orion_csr.PAGE_ID.read()
        # self.orion_csr.PAGE_ID.display()
    
        i=0 
        tx_phase_val_i = [0] * 128
        tx_phase_val_q = [0] * 128
        for i in range (128) :
            tx_phase_val_i[i] = self.i_code_tx[i]
            tx_phase_val_q[i] = self.q_code_tx[i]
            if i == 64 :
                self.orion_csr.PAGE_ID.page_id = 0x19
                self.orion_csr.PAGE_ID.write()
                self.orion_csr.PAGE_ID.read()
                # self.orion_csr.PAGE_ID.display()
                
            self.orion_lut.TX_PHASE_MEM.pos = i % 64;
            self.orion_lut.TX_PHASE_MEM.tx_phase_val_i = tx_phase_val_i[i]
            self.orion_lut.TX_PHASE_MEM.tx_phase_val_q = tx_phase_val_q[i]
            self.orion_lut.TX_PHASE_MEM.write()
    
        """Write TX Gain mem """
        self.orion_csr.PAGE_ID.page_id = 0x1A
        self.orion_csr.PAGE_ID.write()
        self.orion_csr.PAGE_ID.read()
        # self.orion_csr.PAGE_ID.display()
            
        i=0 
        tx_gain_val = [0] * 64
        tx_final_gain_val = [0] * 64
    
        for i in range (64) :
            tx_gain_val[i] = gain_code_tx[i]
            tx_final_gain_val[i] = 0  # final av is programmed to 0, and desired final_av is forced in init_tx defination
                
            self.orion_lut.TX_GAIN_MEM.pos = i
            self.orion_lut.TX_GAIN_MEM.tx_gain_val = tx_gain_val[i]
            self.orion_lut.TX_GAIN_MEM.tx_final_gain_val = tx_final_gain_val[i]
            self.orion_lut.TX_GAIN_MEM.write()
            
    def init_tx(self, TX_BIAS_MODE, final_av=31, ant_sel=0xF):
        if self.version == 'v2':
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x02
            self.orion_csr.REG4_EXT_BIAS.write()

        for i in range(4):
            if ant_sel & (1 << i):  
                setattr(getattr(self.orion_csr, f"TX_GAIN_FORCE"), f"tx{i}_final_gain_force", 1)
                getattr(self.orion_csr, f"TX_GAIN_FORCE").write()
                    
                setattr(getattr(self.orion_csr, f"TX{i}_FINAL_GAIN_FORCE_VAL"), f"tx{i}_final_gain_force_val", final_av)
                getattr(self.orion_csr, f"TX{i}_FINAL_GAIN_FORCE_VAL").write()
        
        if (TX_BIAS_MODE == 'MAX'):
            self.set_tx_lna_curr(3)
            
            self.set_tx_cmb_icurr(3, ant_sel=ant_sel)
            self.set_tx_cmb_qcurr(3, ant_sel=ant_sel)
            
            self.set_tx_drv_curr(31, ant_sel=ant_sel)
            
        if (TX_BIAS_MODE == 'LOW'):
            self.set_tx_lna_curr(0)
            
            self.set_tx_cmb_icurr(0, ant_sel=ant_sel)
            self.set_tx_cmb_qcurr(0, ant_sel=ant_sel)
            
            self.set_tx_drv_curr(12, ant_sel=ant_sel)
            
        elif (TX_BIAS_MODE == 'NOM') :
            self.set_tx_lna_curr(3)
            
            self.set_tx_cmb_icurr(1, ant_sel=ant_sel)
            self.set_tx_cmb_qcurr(1, ant_sel=ant_sel)
            
            self.set_tx_drv_curr(31, ant_sel=ant_sel)
            
        elif (TX_BIAS_MODE == '2W_FEM') :
            self.set_tx_lna_curr(0)
            
            self.set_tx_cmb_icurr(0, ant_sel=ant_sel)
            self.set_tx_cmb_qcurr(0, ant_sel=ant_sel)
            
            self.set_tx_drv_curr(16, ant_sel=ant_sel)
            
        elif (TX_BIAS_MODE == '5W_FEM') :
            self.set_tx_lna_curr(3)
            
            self.set_tx_cmb_icurr(1, ant_sel=ant_sel)
            self.set_tx_cmb_qcurr(1, ant_sel=ant_sel)
            
            self.set_tx_drv_curr(26, ant_sel=ant_sel)
        
    def init_rx(self, RX_BIAS_MODE, ant_sel=0xF):
        if self.version == 'v2':
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x02
            self.orion_csr.REG4_EXT_BIAS.write()

        if (RX_BIAS_MODE == 'LOW'):
            if self.version == 'v2':
                self.set_rx_cmb_icurr(0, ant_sel=ant_sel)
                self.set_rx_cmb_qcurr(2, ant_sel=ant_sel)
            else:
                self.set_rx_cmb_icurr(0, ant_sel=ant_sel)
                self.set_rx_cmb_qcurr(0, ant_sel=ant_sel)
            
        elif (RX_BIAS_MODE == 'NOM') :
            if self.version == 'v2':
                self.set_rx_cmb_icurr(3, ant_sel=ant_sel)
            else:
                self.set_rx_cmb_icurr(3, ant_sel=ant_sel)
            self.set_rx_cmb_qcurr(3, ant_sel=ant_sel)

    def enable_tx(self, ant_sel, tx_lna_gain_ctrl=255, tx_lna_force_val=None):
        self.orion_csr.TX_LNA_CFG.TX_lna_gain_ctrl = (tx_lna_gain_ctrl & 0xFF)
        self.orion_csr.TX_LNA_CFG.write()
        
        self.orion_csr.TR_MASK.tx_mask = (ant_sel & 0x0F)
        self.orion_csr.TR_MASK.write()        
      
    def enable_rx(self, ant_sel):   
        self.orion_csr.TR_MASK.rx_mask = (ant_sel & 0x0F)
        self.orion_csr.TR_MASK.write()

    def set_tr_mode(self, tr_mode):
        if (tr_mode == 'INT_TR'):
           self.orion_csr.TR_CFG.tr_mode_sel = 1
           self.orion_csr.TR_CFG.write()
           self.tr_mode = 1
        elif(tr_mode == 'EXT_TR'):
            self.orion_csr.TR_CFG.tr_mode_sel = 0
            self.orion_csr.TR_CFG.write()
            self.tr_mode = 0
    
    def set_trx_mode(self, trx_val):
        if self.tr_mode:
            self.orion_csr.TR_SW_CTRL.tr_reg = trx_val
            self.orion_csr.TR_SW_CTRL.write()
        # else:
        #     if trx_val == 1:
        #         self.spi.tr_set()
        #     else:
        #         self.spi.tr_reset()
        self.trx_mode = trx_val
    
    def set_freq(self,freq):
        if (freq == '9G'):
          self.orion_csr.FREQ_ID.freq_id=0 
        elif (freq == '11G'):
           self.orion_csr.FREQ_ID.freq_id=1
           
        self.orion_csr.FREQ_ID.write()
        self.orion_csr.RSVD2.write()
        self.orion_csr.RSVD3.write()    

    def set_lut_idx(self, p_idx, g_idx, ant_sel, mode=None):
        
        #------Set LUT IDX for RX---------------------------------------#   
       
        if (self.trx_mode == 0 and mode==None) or mode=='RX':
            target_phase_deg = self.calc_phase_wrapped((p_idx - 4) * 2.975)
            target_gain_dB = -g_idx * 0.5
            self.target_gain_dB = target_gain_dB
            self.target_phase_deg = target_phase_deg

            # Set RX phase and gain codes using loop
            for i in range(4):
                # if(ant_sel & (1<<i)): # Currently setting for all antennas due to correction time issue
                phase_reg = getattr(self.orion_csr, f'PHASE_CODE_RX{i}')
                gain_reg  = getattr(self.orion_csr, f'GAIN_CODE_RX{i}')

                setattr(phase_reg, f'phase_code_rx{i}', p_idx)
                phase_reg.write()
                setattr(gain_reg, f'gain_code_rx{i}', g_idx)
                gain_reg.write()
            
            # Read back phase/gain values from RX0–RX3
            for i in range(4):
                if(ant_sel & (1<<i)):
                    i_lsb  = getattr(self.orion_csr, f'RX{i}_I_LSB_TEMP0').read()
                    q_lsb  = getattr(self.orion_csr, f'RX{i}_Q_LSB_TEMP0').read()
                    av_lsb = getattr(self.orion_csr, f'RX{i}_AV_LSB_TEMP0').read()
                    msb    = getattr(self.orion_csr, f'RX{i}_MSB_TEMP0').read()

                    self.phase_val_i = ((msb & 0x1) << 8) | (i_lsb & 0xFF)
                    self.phase_val_q = ((msb & 0x2) << 7) | (q_lsb & 0xFF)
                    self.gain_val    = ((msb & 0x1C) << 6) | (av_lsb & 0xFF)
            
        #------Set LUT IDX for TX---------------------------------------#
        
        elif (self.trx_mode == 1 and mode==None) or mode=='TX':
            target_phase_deg = self.calc_phase_wrapped((p_idx-4) * 2.975)
            # target_phase_deg = self.calc_phase_wrapped((p_idx) * 2.8125)
            target_gain_dB = -g_idx * 0.5
            self.target_gain_dB = target_gain_dB
            self.target_phase_deg = target_phase_deg
            
            # Apply phase and gain settings to TX
            for i in range(4):
                if(ant_sel & (1<<i)):
                    # Set phase and gain codes
                    phase_reg = getattr(self.orion_csr, f'PHASE_CODE_TX{i}')
                    gain_reg = getattr(self.orion_csr, f'GAIN_CODE_TX{i}')
                                        
                    setattr(phase_reg, f'phase_code_tx{i}', p_idx)
                    phase_reg.write()
                
                    setattr(gain_reg, f'gain_code_tx{i}', g_idx)
                    gain_reg.write()            
            
            # Read TX feedback values
            for i in range(4):
                if(ant_sel & (1<<i)):
                    i_lsb      = getattr(self.orion_csr, f'TX{i}_I_LSB').read()
                    q_lsb      = getattr(self.orion_csr, f'TX{i}_Q_LSB').read()
                    av_lsb     = getattr(self.orion_csr, f'TX{i}_AV_LSB').read()
                    msb        = getattr(self.orion_csr, f'TX{i}_MSB').read()
                    final_av   = getattr(self.orion_csr, f'TX{i}_FINAL_AV').read()
                
                    self.phase_val_i = ((msb & 0x1) << 8) | (i_lsb & 0xFF)
                    self.phase_val_q = ((msb & 0x2) << 7) | (q_lsb & 0xFF)
                    self.gain_val    = ((msb & 0x1C) << 6) | (av_lsb & 0xFF)
                    self.final_gain  = final_av & 0x1F                  
        
    def enable_rx_correction(self,en):
        if en==1:
            self.orion_csr.CORR_CFG.en_gain_corr = 1
            self.orion_csr.CORR_CFG.en_phase_corr = 1
            self.orion_csr.CORR_CFG.write()
        else:
            self.orion_csr.CORR_CFG.en_gain_corr = 0
            self.orion_csr.CORR_CFG.en_phase_corr = 0
            self.orion_csr.CORR_CFG.write()        
        
    def dac_cfg(
    self, pa_sel, lna_sel,
    PA0=None, PA0_PDN=None, PA1=None, PA1_PDN=None,
    PA2=None, PA2_PDN=None, PA3=None, PA3_PDN=None,
    LNA0=127, LNA0_PDN=127, LNA1=127, LNA1_PDN=127,
    LNA2=127, LNA2_PDN=127, LNA3=127, LNA3_PDN=127
):
        if PA0 == None:
            PA0 = 0 if self.version == 'v2' else 127
        if PA1 == None:
            PA1 = 0 if self.version == 'v2' else 127
        if PA2 == None:
            PA2 = 0 if self.version == 'v2' else 127
        if PA3 == None:
            PA3 = 0 if self.version == 'v2' else 127
        if PA0_PDN == None:
            PA0_PDN = 0 if self.version == 'v2' else 127
        if PA1_PDN == None:
            PA1_PDN = 0 if self.version == 'v2' else 127
        if PA2_PDN == None:
            PA2_PDN = 0 if self.version == 'v2' else 127
        if PA3_PDN == None:
            PA3_PDN = 0 if self.version == 'v2' else 127

        # DAC value map
        dac_map = {
            'DAC_CTRL_PA0': PA0, 'DAC_CTRL_PA0_PDN': PA0_PDN,
            'DAC_CTRL_PA1': PA1, 'DAC_CTRL_PA1_PDN': PA1_PDN,
            'DAC_CTRL_PA2': PA2, 'DAC_CTRL_PA2_PDN': PA2_PDN,
            'DAC_CTRL_PA3': PA3, 'DAC_CTRL_PA3_PDN': PA3_PDN,
            'DAC_CTRL_LNA0': LNA0, 'DAC_CTRL_LNA0_PDN': LNA0_PDN,
            'DAC_CTRL_LNA1': LNA1, 'DAC_CTRL_LNA1_PDN': LNA1_PDN,
            'DAC_CTRL_LNA2': LNA2, 'DAC_CTRL_LNA2_PDN': LNA2_PDN,
            'DAC_CTRL_LNA3': LNA3, 'DAC_CTRL_LNA3_PDN': LNA3_PDN
        }
    
        # Write only user-specified PA values for selected channels
        for i in range(4):
            if pa_sel & (1 << i):
                for suffix in ['', '_PDN']:
                    reg = f'DAC_CTRL_PA{i}{suffix}'
                    setattr(getattr(self.orion_csr, reg), reg, dac_map[reg])
                    getattr(self.orion_csr, reg).write()
    
            if lna_sel & (1 << i):
                for suffix in ['', '_PDN']:
                    reg = f'DAC_CTRL_LNA{i}{suffix}'
                    setattr(getattr(self.orion_csr, reg), reg, dac_map[reg])
                    getattr(self.orion_csr, reg).write() 
    
    def en_data_path(self, value:bool):
        """
        Parameters:
            value (bool): Should be 0 or 1.
        """    
        self.orion_csr.TR_CFG.data_path_en = value
        self.orion_csr.TR_CFG.write()  
    
    def set_tr_mask(self, tx_mask=None, rx_mask=None):
        
        if tx_mask is not None:
            self.orion_csr.TR_MASK.tx_mask = tx_mask
            self.orion_csr.TX_LNA_CFG.TX_lna_gain_ctrl = 255
            self.orion_csr.TX_LNA_CFG.write()
    
        if rx_mask is not None:
            self.orion_csr.TR_MASK.rx_mask = rx_mask
            print(f"🛠️ TR_MASK.rx_mask set to 0x{rx_mask:X}")
    
        if tx_mask is not None or rx_mask is not None:
            self.orion_csr.TR_MASK.write()
        else:
            print("⚠️ No changes made to TR_MASK (both tx_mask and rx_mask were None)")
    
    def cfg_stg2_load(self,value):
        if value == 'PIN':
            self.orion_csr.STG2_CFG.use_reg_for_stg2_update = 0
            self.orion_csr.STG2_CFG.write()
            self.use_reg_inp_for_stg2=0
            
        elif value == 'REG':
            self.orion_csr.STG2_CFG.use_reg_for_stg2_update = 1
            self.orion_csr.STG2_CFG.write()
            self.use_reg_inp_for_stg2=1
        else:
            print("⚠️ cfg_stg2_load: Invalid argument")
            exit(1)
            
    def stg2_load(self):
        if self.use_reg_inp_for_stg2:
            self.orion_csr.UPDATE_CODE.update_code = 0
            self.orion_csr.UPDATE_CODE.write()  
            self.orion_csr.UPDATE_CODE.update_code = 1
            self.orion_csr.UPDATE_CODE.write()
            self.orion_csr.UPDATE_CODE.update_code = 0
            self.orion_csr.UPDATE_CODE.write()           
        else:
            self.spi.txl_tggl()    

    def set_iq_val(self, I=None, Q=None, Av=None, ant_sel=0xF, mode=None):
        
        if (self.trx_mode == 1 and mode==None) or mode=='TX':
            for i in range(4):
                if ant_sel & (1 << i):                                            
                    if Av is not None:
                        setattr(getattr(self.orion_csr, f"TX{i}_AV_LSB"), f"tx{i}_av_lsb", (Av & 0xFF))
                        setattr(getattr(self.orion_csr, f"TX{i}_MSB"), f"tx{i}_av_msb", (Av & 0x700) >> 8)
                        getattr(self.orion_csr, f"TX{i}_AV_LSB").write()
                        getattr(self.orion_csr, f"TX{i}_MSB").write()

                    if I is not None:
                        setattr(getattr(self.orion_csr, f"TX{i}_I_LSB"), f"tx{i}_i_lsb", (I & 0xFF))
                        setattr(getattr(self.orion_csr, f"TX{i}_MSB"), f"tx{i}_i_msb", (I & 0x100) >> 8)
                        getattr(self.orion_csr, f"TX{i}_I_LSB").write()
                        getattr(self.orion_csr, f"TX{i}_MSB").write()

                    if Q is not None:
                        setattr(getattr(self.orion_csr, f"TX{i}_Q_LSB"), f"tx{i}_q_lsb", (Q & 0xFF))
                        setattr(getattr(self.orion_csr, f"TX{i}_MSB"), f"tx{i}_q_msb", (Q & 0x100) >> 8)
                        getattr(self.orion_csr, f"TX{i}_Q_LSB").write()
                        getattr(self.orion_csr, f"TX{i}_MSB").write()                        
                    
        else:
            for i in range(4):
                if ant_sel & (1 << i):                      
                    if Av is not None:                        
                        setattr(getattr(self.orion_csr, f"RX{i}_AV_LSB_TEMP0"), f"rx{i}_av_lsb_temp0", (Av & 0xFF))
                        setattr(getattr(self.orion_csr, f"RX{i}_MSB_TEMP0"), f"rx{i}_av_msb_temp0", (Av & 0x700) >> 8)
                        getattr(self.orion_csr, f"RX{i}_AV_LSB_TEMP0").write()
                        getattr(self.orion_csr, f"RX{i}_MSB_TEMP0").write()
                                                
                    if I is not None:
                        setattr(getattr(self.orion_csr, f"RX{i}_I_LSB_TEMP0"), f"rx{i}_i_lsb_temp0", (I & 0xFF))
                        setattr(getattr(self.orion_csr, f"RX{i}_MSB_TEMP0"), f"rx{i}_i_msb_temp0", (I & 0x100) >> 8)
                        getattr(self.orion_csr, f"RX{i}_I_LSB_TEMP0").write()
                        getattr(self.orion_csr, f"RX{i}_MSB_TEMP0").write()
                        
                    if Q is not None:
                        setattr(getattr(self.orion_csr, f"RX{i}_Q_LSB_TEMP0"), f"rx{i}_q_lsb_temp0", (Q & 0xFF))
                        setattr(getattr(self.orion_csr, f"RX{i}_MSB_TEMP0"), f"rx{i}_q_msb_temp0", (Q & 0x100) >> 8)
                        getattr(self.orion_csr, f"RX{i}_Q_LSB_TEMP0").write()
                        getattr(self.orion_csr, f"RX{i}_MSB_TEMP0").write()
    
    def force_tx_Av(self, Av=None, ant_sel=0xF):
        for i in range(4):
            if ant_sel & (1 << i):  
                setattr(getattr(self.orion_csr, f"TX_GAIN_FORCE"), f"tx{i}_final_gain_force", 1)
                getattr(self.orion_csr, f"TX_GAIN_FORCE").write()
                    
                setattr(getattr(self.orion_csr, f"TX{i}_FINAL_GAIN_FORCE_VAL"), f"tx{i}_final_gain_force_val", Av)
                getattr(self.orion_csr, f"TX{i}_FINAL_GAIN_FORCE_VAL").write()
    
    #------------------RX Tail Current Control----------------
    def set_rx_cmb_icurr(self,rx_cmb_icurr,ant_sel=0xF):
        "function to set RX combiner I-phase tail current 2-bit settings, 0 to 3"

        for i in range(4):
            if ant_sel & (1 << i):
                setattr(getattr(self.orion_csr, f"REG0_RX{i}"), f"rx{i}_cmb_icurr_ctrl", (rx_cmb_icurr & 0x3))
                getattr(self.orion_csr, f"REG0_RX{i}").write()
        
    def set_rx_cmb_qcurr(self,rx_cmb_qcurr,ant_sel=0xF):
        "function to set RX combiner Q-phase tail current 2-bit settings, 0 to 3"

        for i in range(4):
            if ant_sel & (1 << i):
                setattr(getattr(self.orion_csr, f"REG0_RX{i}"), f"rx{i}_cmb_qcurr_ctrl", (rx_cmb_qcurr & 0x3))
                getattr(self.orion_csr, f"REG0_RX{i}").write()

        
    #------------------TX Tail Current Control----------------
    def set_tx_cmb_icurr(self,tx_cmb_icurr,ant_sel=0xF):
        "function to set TX combiner I-phase tail current 2-bit settings, 0 to 3"

        for i in range(4):
            if ant_sel & (1 << i):
                setattr(getattr(self.orion_csr, f"REG0_TX{i}"), f"tx{i}_cmb_icurr_ctrl", (tx_cmb_icurr & 0x3))
                getattr(self.orion_csr, f"REG0_TX{i}").write()

    def set_tx_cmb_qcurr(self,tx_cmb_qcurr,ant_sel=0xF):
        "function to set TX combiner Q-phase tail current 2-bit settings, 0 to 3"

        for i in range(4):
            if ant_sel & (1 << i):
                setattr(getattr(self.orion_csr, f"REG0_TX{i}"), f"tx{i}_cmb_qcurr_ctrl", (tx_cmb_qcurr & 0x3))
                getattr(self.orion_csr, f"REG0_TX{i}").write()

    def set_tx_drv_curr(self,tx_drv_curr,ant_sel=0xF):
        "function to set TX driver tail current 5-bit settings, 0 to 31"

        for i in range(4):
            if ant_sel & (1 << i):
                setattr(getattr(self.orion_csr, f"TX{i}_FINAL_AV"), f"tx{i}_final_av", (tx_drv_curr & 0x1F))
                getattr(self.orion_csr, f"TX{i}_FINAL_AV").write()
                               

    #------------------TX LNA Tail Current Control----------------
    def set_tx_lna_curr(self,tx_lna_curr):
        "function to set common TX LNA tail current 2-bit settings, 0 to 3"
        
        #set value of register
        self.orion_csr.REG2_SPARE.txlna_curr_ctrl=(tx_lna_curr & 0x3)
        self.orion_csr.REG2_SPARE.write()
    
    def set_beam_idx(self, idx):
        pass

    def enable_adc(self, adc_val):
        if (adc_val == 1):
            self.orion_csr.ADC_CTRL.en_adc_osc = (adc_val & 0x01)
            self.orion_csr.ADC_CTRL.write()
            self.orion_csr.ADC_CTRL.en_adc = (adc_val & 0x01)
            self.orion_csr.ADC_CTRL.write()
        elif (adc_val == 0):
            self.orion_csr.ADC_CTRL.en_adc = (adc_val & 0x01)
            self.orion_csr.ADC_CTRL.write()
            self.orion_csr.ADC_CTRL.en_adc_osc = (adc_val & 0x01)
            self.orion_csr.ADC_CTRL.write()

    def sel_adc_input(self, adc_input):
        "function to select ADC input voltage"
        # adc_input can be "none", "pkdet", "temp", "atb" or "gp7"
        # "none" disable all connections to ADC input
        # "pkdet" selects peak detector output as ADC input
        # "temp" selects temperature as ADC input
        # "atb" selects atb as ADC input
        # "gp7" selects GP7 pin as ADC input

        # set value of register
        if (adc_input == "none"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x00
        elif (adc_input == "pkdet"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x1
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x00
        elif (adc_input == "temp"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x1
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x00
        elif (adc_input == "atb"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x1
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x00
        elif (adc_input == "gp4"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x10
        elif (adc_input == "gp5"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x20
        elif (adc_input == "gp6"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x0
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x40
        elif (adc_input == "gp7"):
            self.orion_csr.REG0_ADC.en_pkdet_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_temp_sense_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_atb_to_adc_sw = 0x0
            self.orion_csr.REG0_ADC.en_gp7_to_adc_sw = 0x1
            self.orion_csr.REG4_EXT_BIAS.rsvd7 = 0x00
        else:
            print("Unknown argument, adc_input can only be pkdet, temp, atb, gp7 or none")
        # write register
        self.orion_csr.REG4_EXT_BIAS.write()
        self.orion_csr.REG0_ADC.write()

    # ------------------Read EOC of ADC----------------
    def read_adc_eoc(self):
        "function to read eoc status of ADC"

        # read value of register
        adc_eoc = ((self.orion_csr.ADC_STS.read()) & 0x01)
        return adc_eoc

    # ------------------Read Output of ADC----------------
    def read_adc_output(self):
        "function to read 9-bit output of ADC"

        # read value of LSB 8bit
        adc_lsb = (self.orion_csr.ADC_IN_LSB.read() & 0xFF)
        # read value of MSB 1bit
        adc_msb = (self.orion_csr.ADC_IN_MSB.read() & 0x01)
        # calculate output value
        adc_output = (adc_msb << 8) | adc_lsb
        return adc_output

    #TODO: DET