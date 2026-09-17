import sys
import csv
sys.path.append('../../include')
from ORION_8G_12G import *
from SPI import *

spi = SPI()
orion_csr = ORION_8G_12G(spi)

PAGE_START = 32
PAGE_END = 32
PAGE_SIZE = 256
BASE_ADDR = 256
BYTES_PER_ROW = 8

with open('lut_dump.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Lower address goes last (rightmost), so header/columns count down from
    # the highest offset in the row to the lowest.
    writer.writerow(['page', 'address'] + [f'byte+{i}' for i in range(BYTES_PER_ROW - 1, -1, -1)])

    for page in range(PAGE_START, PAGE_END + 1):
        orion_csr.PAGE_ID.page_id = page
        orion_csr.PAGE_ID.write()

        for row_start in range(0, PAGE_SIZE, BYTES_PER_ROW):
            addr = BASE_ADDR + row_start
            row_bytes = [spi.read(addr + i) for i in range(BYTES_PER_ROW)]
            addr_str = f'{(addr >> 8) & 0xFF:02X}_{addr & 0xFF:02X}'
            hex_bytes = [f'{b:02X}' for b in row_bytes]
            hex_bytes_reversed = hex_bytes[::-1]

            print(f'Page {page:2d} | Addr {addr_str}: {" ".join(hex_bytes_reversed)}')
            writer.writerow([page, addr_str] + hex_bytes_reversed)

spi.close()
