import time

from usb2spi import USB2SPIDriver

class SPI:    
    def __init__(self, port=None):
        self.val = [i for i in range(512)]
        if port is None:
            self.dev = USB2SPIDriver('COM8')
        else:
            self.dev = USB2SPIDriver(port)
        time.sleep(1)
        self.dev.setspeed(3)
        self.gpio_configured = 0
        self.cfg_gpio()
        self.gpio_reset()
        self.trset=0
        self.txlset=0
        self.rxlset=0
        self.paset=0
        self.gpio_data=0x00
    def write(self,addr,data, slv_addr = None, bdst = None):
        if slv_addr == None and bdst == None:
            self.dev.sel()
            self.dev.write([0x3E | ((addr >> 8) & 1),addr & 0xFF,data])
            self.dev.unsel()
            self.val[addr] = data
            # print(f'setting csr[{hex(addr)}] @default = {hex(data)}')
        elif bdst == 1:
            self.dev.sel()
            self.dev.write([0x40 | ((addr >> 8) & 1),addr & 0xFF,data])
            self.dev.unsel()
            self.val[addr] = data
            # print(f'setting csr[{hex(addr)}] @bdst = {hex(data)}')
        elif bdst == 0:
            self.dev.sel()
            self.dev.write([(slv_addr<<1) | ((addr >> 8) & 1),addr & 0xFF,data])
            self.dev.unsel()
            self.val[addr] = data
            # print(f'setting csr[{hex(addr)}] @{slv_addr} = {hex(data)}')
    def read(self,addr, slv_addr = None):

        if slv_addr == None:
            self.dev.sel()
            rx=list(self.dev.writeread([0xBE | ((addr >> 8) & 1),addr & 0xFF,0x00]))
            self.dev.unsel()
            self.val[addr]=rx[2]
            # print(f'reading csr[{hex(addr)}] @default : {hex(self.val[addr])}')
        else:
            self.dev.sel()
            rx=list(self.dev.writeread([0x80 | (slv_addr<<1) | ((addr >> 8) & 1),addr & 0xFF,0x00]))
            self.dev.unsel()
            self.val[addr]=rx[2]
            # print(f'reading csr[{hex(addr)}] @{slv_addr} : {hex(self.val[addr])}')
        return self.val[addr]

    def cfg_gpio(self):        
        self.dev.seta(0)
        self.dev.write([0x06,0x0F])
        self.dev.seta(1)
        
        # SW WAR: with a single write the set does not happen
        self.dev.seta(0)
        self.dev.write([0x06,0x0F])
        self.dev.seta(1)
        self.gpio_configured = 1
    def gpio_reset(self):
        self.dev.seta(0)
        self.dev.write([0x02,0x00])
        self.dev.seta(1)        
    def tr_set(self):
        val = self.gpio_data | 0x10
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.trset=1
    def tr_reset(self):
        val = self.gpio_data & 0xEF
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.trset=0
    def tr_tggl(self):
        self.dev.seta(0)
        if self.trset==0:
            val = self.gpio_data | 0x10
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.trset=1
            print("TR SET")
            return
        if self.trset==1:
            val = self.gpio_data ^ 0x10
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.trset=0
            print("TR RESET")
            return
        self.dev.seta(1)
    def txl_set(self):
        val = self.gpio_data | 0x80
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.txlset=1
    def txl_reset(self):
        val = self.gpio_data ^ 0x80
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.txlset=0
    def txl_tggl(self):
        self.dev.seta(0)
        if self.txlset==0:
            val = self.gpio_data | 0x80
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.txlset=1
            print("TXL SET")
            return
        if self.txlset==1:
            val = self.gpio_data ^ 0x80
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.txlset=0
            print("TXL RESET")
            return
        self.dev.seta(1)
    def rxl_set(self):
        val = self.gpio_data | 0x40
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.rxlset=1
    def rxl_reset(self):
        val = self.gpio_data ^ 0x40
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.rxlset=0
    def rxl_tggl(self):
        self.dev.seta(0)
        if self.rxlset==0:
            val = self.gpio_data | 0x40
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.rxlset=1
            print("RXL SET")
            return
        if self.rxlset==1:
            val = self.gpio_data ^ 0x40
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.rxlset=0
            print("RXL RESET")
            return
        self.dev.seta(1)
    def pa_set(self):
        val = self.gpio_data | 0x20
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.paset=1
    def pa_reset(self):
        val = self.gpio_data ^ 0x20
        self.dev.seta(0)
        self.dev.write([0x02,val])
        self.dev.seta(1)
        self.gpio_data = val
        self.paset=0
    def pa_tggl(self):        
        self.dev.seta(0)
        if self.paset==0:
            val = self.gpio_data | 0x20
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.paset=1
            print("PA SET")
            return
        if self.paset==1:
            val = self.gpio_data ^ 0x20
            self.dev.write([0x02,val])
            self.gpio_data = val
            self.paset=0
            print("PA RESET")
            return
        self.dev.seta(1)
    def close(self):
        print(f'Closing SPI')
        self.dev.close()