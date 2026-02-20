import time

# from usb2spi import USB2SPIDriver

class SPI:
    def __init__(self, port=None):
        self.val = [i for i in range(256)]
        # self.dev = USB2SPIDriver('COM16')
        # time.sleep(1)
        # self.dev.setspeed(3)
        if port is None:
            print('SPI @ COMX')
        else:
            print(f'SPI @ {port}')
    def write(self,addr,data, slv_addr = None, bdst = None):
        print(f'setting csr[{hex(addr)}] = {hex(data)}')
        # self.dev.sel()
        # self.dev.write([0x3E,addr,data])
        # self.dev.unsel()
        self.val[addr] = data
    def read(self,addr, slv_addr = None):
        # self.dev.sel()
        # rx=list(self.dev.writeread([0xBE,addr,0x00]))
        # self.dev.unsel()
        # self.val[addr]=rx[2]
        print(f'reading csr[{hex(addr)}] : {hex(self.val[addr])}')
        return self.val[addr]
    def close(self):
        print(f'Closing SPI')
        # self.dev.close()