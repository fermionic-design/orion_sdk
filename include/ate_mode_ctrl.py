from libs.fd_cmn.drivers.fd_ft232h import fd_ft232h

class ate_mode_ctrl:
    def __init__(self):
        self.ft232h = fd_ft232h()
        self.ft232h.cfg_gpio(pins=0x0F, direction=0x0F)
        self.gpio_val = 0x0
        print(f'GPIO = {self.gpio_val:04b}')

    def set_mode(self, mode:str):
        # [1:0] bits control the mode
        # TX = 01
        # RX = 10
        # DET= 00
        if mode=='TX':
            self.gpio_val = (self.gpio_val & 0xC) | 0x1
        if mode=='RX':
            self.gpio_val = (self.gpio_val & 0xC) | 0x2
        if mode=='DET':
            self.gpio_val = (self.gpio_val & 0xC) | 0x0
        self.ft232h.gpio_write(self.gpio_val)
        print(f'GPIO = {self.gpio_val:04b}')

    def set_ch(self, ch:int):
        # [3:2] control the channel
        ch_map = {  # This come from the PCB configuration
            0: 2,
            1: 3,
            2: 0,
            3: 1
        }
        self.gpio_val = (self.gpio_val & 0x3) | ch_map[ch]<<2
        self.ft232h.gpio_write(self.gpio_val)
        print(f'GPIO = {self.gpio_val:04b}')

if __name__ == "__main__":
    ate_mode = ate_mode_ctrl()
    ate_mode.set_mode('TX')
    ate_mode.set_ch(0)