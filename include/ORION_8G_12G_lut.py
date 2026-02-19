# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 15:34:18 2023

@author: pradipta
"""

                
class TX_PHASE_MEM:
    def __init__(self,dev, slv_addr, bdst):
        self.dev = dev
        self.slv_addr = slv_addr
        self.bdst = bdst
        self.pos = 0
        self.tx_phase_val_i = 0
        self.tx_phase_val_q = 0
    def write(self):
        val_i = 0
        val_i_sign = 0
        val_i |= (self.tx_phase_val_i & 0xFF) << 0
        val_i_sign |= (self.tx_phase_val_i & 0x100) >> 8
        val_q = 0
        val_q_sign = 0
        val_q |= (self.tx_phase_val_q & 0xFF) << 0
        val_q_sign |= (self.tx_phase_val_q & 0x100) >> 8
        val_sign = val_q_sign<<1 | val_i_sign
        # print(f" pos = {self.pos}")
        self.dev.write(self.pos*4+256,val_i, self.slv_addr, self.bdst)
        self.dev.write(self.pos*4+257,val_q, self.slv_addr, self.bdst)
        self.dev.write(self.pos*4+258,val_sign, self.slv_addr, self.bdst)
    def read(self):
        val_i = self.dev.read(self.pos*4+256, self.slv_addr)
        val_q = self.dev.read(self.pos*4+257, self.slv_addr)
        val_sign = self.dev.read(self.pos*4+258, self.slv_addr)
        self.tx_phase_val = val_sign<<16 & 0x30000 | val_q<<8 & 0xFF00 | val_i & 0xFF
        #print(val_i)
        #print(val_q)
        #print(val_sign)
        return self.tx_phase_val
        #return val_i

class TX_GAIN_MEM:
    def __init__(self,dev, slv_addr, bdst):
        self.dev = dev
        self.slv_addr = slv_addr
        self.bdst = bdst
        self.pos = 0
        self.tx_gain_val = 0
        self.tx_final_gain_val = 0
        self.tx_final_gain_gain_val = 0
    def write(self):
        gain_val_lsb = 0
        gain_val_msb = 0
        final_gain_val = 0
        gain_val_lsb |= (self.tx_gain_val & 0xFF)
        gain_val_msb |= (self.tx_gain_val & 0x700) >> 8
        final_gain_val |= (self.tx_final_gain_val & 0x1F) >> 0
        val_2nd_byte = final_gain_val << 3 | gain_val_msb
        # print(f" pos = {self.pos}")
        self.dev.write(self.pos*2+256,gain_val_lsb, self.slv_addr, self.bdst)
        self.dev.write(self.pos*2+257,val_2nd_byte, self.slv_addr, self.bdst)
    def read(self):
        val_lsb = self.dev.read(self.pos*2+256, self.slv_addr)
        val_msb = self.dev.read(self.pos*2+257, self.slv_addr)
        self.tx_gain_val = (val_msb & 0x7) << 8 | val_lsb
        self.tx_final_gain_val = val_msb & 0xF8
        self.tx_final_gain_gain_val = self.tx_final_gain_val << 8 | self.tx_gain_val
        return self.tx_final_gain_gain_val    
        #return val_i

    # def display(self):
    #     attribute_names = [name for name in dir(self) if not callable(getattr(self, name)) and not name.startswith("__")]
    #     for name in attribute_names:
    #         if name not in ['_addr','dev']:
    #             print(f'{name} = {hex(getattr(self,name))}')
                

class RX_PHASE_MEM:
    def __init__(self,dev, slv_addr, bdst):
        self.dev = dev
        self.slv_addr = slv_addr
        self.bdst = bdst
        self.pos = 0
        self.rx_phase_val_i = 0
        self.rx_phase_val_q = 0
        self.rx_gain_err = 0
        self.rx_temp_val = 0
        self.rx_freq_val = 0
    def write(self):
        val_i = 0
        val_i_sign = 0
        val_i |= (self.rx_phase_val_i & 0xFF) << 0
        val_i_sign |= (self.rx_phase_val_i & 0x100) >> 8
        val_q = 0
        val_q_sign = 0
        val_q |= (self.rx_phase_val_q & 0xFF) << 0
        val_q_sign |= (self.rx_phase_val_q & 0x100) >> 8
        val_sign = val_q_sign<<1 | val_i_sign
        val_gain_err = 0
        val_gain_err |= self.rx_gain_err & 0x7
        # print(f"temp = {self.rx_temp_val}, freq = {self.rx_freq_val}, pos = {self.pos}")
        self.dev.write(self.pos*16+256 + self.rx_temp_val*4,val_i, self.slv_addr, self.bdst)
        self.dev.write(self.pos*16+257 + self.rx_temp_val*4,val_q, self.slv_addr, self.bdst)
        self.dev.write(self.pos*16+258 + self.rx_temp_val*4,val_sign, self.slv_addr, self.bdst)
        self.dev.write(self.pos*16+259 + self.rx_temp_val*4,val_gain_err, self.slv_addr, self.bdst)
    def read(self):
        val_i = self.dev.read(self.pos*16+256 + self.rx_temp_val*4, self.slv_addr)
        val_q = self.dev.read(self.pos*16+257 + self.rx_temp_val*4, self.slv_addr)
        val_sign = self.dev.read(self.pos*16+258 + self.rx_temp_val*4, self.slv_addr)
        val_gain_err = self.dev.read(self.pos*16+259 + self.rx_temp_val*4, self.slv_addr)
        self.rx_phase_val = val_gain_err<<18 & 0x1C0000 | val_sign<<16 & 0x30000 | val_q<<8 & 0xFF00 | val_i & 0xFF
        return self.rx_phase_val
        #return val_i
        
class BEAM_MEM:
    def __init__(self,dev, slv_addr, bdst):
        self.dev = dev
        self.slv_addr = slv_addr
        self.bdst = bdst
        self.pos = 0
        self.rx_phase_val_i = 0
        self.rx_phase_val_q = 0
        self.rx_gain_val = 0
        self.tx_phase_val_i = 0
        self.tx_phase_val_q = 0
        self.tx_gain_val = 0
        self.ant = 0

    def write(self):
        rx_val_i = 0
        rx_val_i_sign = 0
        rx_val_i |= (self.rx_phase_val_i & 0xFF) << 0
        rx_val_i_sign |= (self.rx_phase_val_i & 0x100) >> 8
        rx_val_q = 0
        rx_val_q_sign = 0
        rx_val_q |= (self.rx_phase_val_q & 0xFF) << 0
        rx_val_q_sign |= (self.rx_phase_val_q & 0x100) >> 8
        rx_val_sign = rx_val_q_sign<<1 | rx_val_i_sign
        rx_gain_val_lsb = 0
        rx_gain_val_msb = 0
        rx_gain_val_lsb |= (self.rx_gain_val & 0xFF)
        rx_gain_val_msb |= (self.rx_gain_val & 0x700) >> 8
        tx_val_i = 0
        tx_val_i_sign = 0
        tx_val_i |= (self.tx_phase_val_i & 0xFF) << 0
        tx_val_i_sign |= (self.tx_phase_val_i & 0x100) >> 8
        tx_val_q = 0
        tx_val_q_sign = 0
        tx_val_q |= (self.tx_phase_val_q & 0xFF) << 0
        tx_val_q_sign |= (self.tx_phase_val_q & 0x100) >> 8
        tx_val_sign = tx_val_q_sign<<1 | tx_val_i_sign
        tx_gain_val_lsb = 0
        tx_gain_val_msb = 0
        tx_gain_val_lsb |= (self.tx_gain_val & 0xFF)
        tx_gain_val_msb |= (self.tx_gain_val & 0x700) >> 8

        # self.dev.write(self.pos*64+256 + self.ant*16,rx_val_i)
        # self.dev.write(self.pos*64+257 + self.ant*16,rx_val_q)
        # self.dev.write(self.pos*64+258 + self.ant*16,rx_val_sign)
        # self.dev.write(self.pos*64+259 + self.ant*16,rx_gain_val_lsb)
        # self.dev.write(self.pos*64+260 + self.ant*16,rx_gain_val_msb)
        # self.dev.write(self.pos*64+264 + self.ant*16,tx_val_i)
        # self.dev.write(self.pos*64+265 + self.ant*16,tx_val_q)
        # self.dev.write(self.pos*64+266 + self.ant*16,tx_val_sign)
        # self.dev.write(self.pos*64+267 + self.ant*16,tx_gain_val_lsb)
        # self.dev.write(self.pos*64+268 + self.ant*16,tx_gain_val_msb)
        
        self.dev.write(self.pos*64+264 + self.ant*16,rx_val_i, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+265 + self.ant*16,rx_val_q, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+266 + self.ant*16,rx_val_sign, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+267 + self.ant*16,rx_gain_val_lsb, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+268 + self.ant*16,rx_gain_val_msb, self.slv_addr, self.bdst)        
        self.dev.write(self.pos*64+256 + self.ant*16,tx_val_i, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+257 + self.ant*16,tx_val_q, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+258 + self.ant*16,tx_val_sign, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+259 + self.ant*16,tx_gain_val_lsb, self.slv_addr, self.bdst)
        self.dev.write(self.pos*64+260 + self.ant*16,tx_gain_val_msb, self.slv_addr, self.bdst)
        
    def read(self):
        # rx_val_i = self.dev.read(self.pos*64+256 + self.ant*16)
        # rx_val_q = self.dev.read(self.pos*64+257 + self.ant*16)
        # rx_val_sign = self.dev.read(self.pos*64+258 + self.ant*16)
        # rx_val_gain_lsb = self.dev.read(self.pos*64+259 + self.ant*16)
        # rx_val_gain_msb = self.dev.read(self.pos*64+260 + self.ant*16)
        # tx_val_i = self.dev.read(self.pos*64+264 + self.ant*16)
        # tx_val_q = self.dev.read(self.pos*64+265 + self.ant*16)
        # tx_val_sign = self.dev.read(self.pos*64+266 + self.ant*16)
        # tx_val_gain_lsb = self.dev.read(self.pos*64+267 + self.ant*16)
        # tx_val_gain_msb = self.dev.read(self.pos*64+268 + self.ant*16)
        
        rx_val_i = self.dev.read(self.pos*64+264 + self.ant*16, self.slv_addr)
        rx_val_q = self.dev.read(self.pos*64+265 + self.ant*16, self.slv_addr)
        rx_val_sign = self.dev.read(self.pos*64+266 + self.ant*16, self.slv_addr)
        rx_val_gain_lsb = self.dev.read(self.pos*64+267 + self.ant*16, self.slv_addr)
        rx_val_gain_msb = self.dev.read(self.pos*64+268 + self.ant*16, self.slv_addr)        
        tx_val_i = self.dev.read(self.pos*64+256 + self.ant*16, self.slv_addr)
        tx_val_q = self.dev.read(self.pos*64+257 + self.ant*16, self.slv_addr)
        tx_val_sign = self.dev.read(self.pos*64+258 + self.ant*16, self.slv_addr)
        tx_val_gain_lsb = self.dev.read(self.pos*64+259 + self.ant*16, self.slv_addr)
        tx_val_gain_msb = self.dev.read(self.pos*64+260 + self.ant*16, self.slv_addr)
        
        
        self.beam_val = tx_val_gain_msb<<58 & 0x1C00000000000000 | tx_val_gain_lsb<<50 & 0x3FC000000000000 | tx_val_sign<<48 & 0x3000000000000 | tx_val_q<<40 & 0xFF0000000000 | tx_val_i<<32 & 0xFF00000000 | rx_val_gain_msb<<26 & 0x1C000000 | rx_val_gain_lsb<<18 & 0x3FC0000 | rx_val_sign<<16 & 0x30000 | rx_val_q<<8 & 0xFF00 | rx_val_i & 0xFF
        
     
        return self.beam_val
        #return val_i
        
class RX_GAIN_MEM:
    def __init__(self,dev, slv_addr, bdst):
        self.dev = dev
        self.pos = 0
        self.slv_addr = slv_addr
        self.bdst = bdst
        self.rx_gain_val = 0
        self.rx_ph_err = 0
        self.rx_temp_val = 0
        self.rx_freq_val = 0
    def write(self):
        gain_val_lsb = 0
        gain_val_msb = 0
        gain_val_lsb |= (self.rx_gain_val & 0xFF)
        gain_val_msb |= (self.rx_gain_val & 0x700) >> 8
        val_ph_err = 0
        val_ph_err |= self.rx_ph_err & 0x7
        # print(f"temp = {self.rx_temp_val}, freq = {self.rx_freq_val}, pos = {self.pos}")
        self.dev.write(self.pos*16+256 + self.rx_temp_val*4,gain_val_lsb, self.slv_addr, self.bdst)
        self.dev.write(self.pos*16+257 + self.rx_temp_val*4,gain_val_msb, self.slv_addr, self.bdst)
        self.dev.write(self.pos*16+258 + self.rx_temp_val*4,val_ph_err, self.slv_addr, self.bdst)
    def read(self):
        gain_val_lsb = self.dev.read(self.pos*16+256 + self.rx_temp_val*4, self.slv_addr)
        gain_val_msb = self.dev.read(self.pos*16+257 + self.rx_temp_val*4, self.slv_addr)
        val_ph_err = self.dev.read(self.pos*16+258 + self.rx_temp_val*4, self.slv_addr)
        self.rx_gain_val = val_ph_err<<11 & 0x3800 |  gain_val_msb<<8 & 0x700 | gain_val_lsb & 0xFF
        return self.rx_gain_val
        #return val_i


class ORION_8G_12G_lut:
    def __init__(self,dev, slv_addr = None, bdst = None):
        self.TX_PHASE_MEM = TX_PHASE_MEM(dev, slv_addr, bdst)
        self.TX_GAIN_MEM = TX_GAIN_MEM(dev, slv_addr, bdst)
        self.RX_PHASE_MEM = RX_PHASE_MEM(dev, slv_addr, bdst)
        self.RX_GAIN_MEM = RX_GAIN_MEM(dev, slv_addr, bdst)
        self.BEAM_MEM = BEAM_MEM(dev, slv_addr, bdst)
    
    def read_all(self):
        attributes = vars(self)
        for name, value in attributes.items():
            if not name.startswith('__') and not callable(value):
                getattr(self,name).read()
                getattr(self,name).display()
