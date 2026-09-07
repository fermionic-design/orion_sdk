import csv
import os
import re

LOG_PATH = r"C:\Users\silic\GitHub\orion_sdk\logs\beam_lut_simple.log"  # <-- change this before running

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, '..')
REGMAP_PATH = os.path.join(REPO_ROOT, 'regs', 'ORION_8G_12G_csr.csv')

OUT_STEM = os.path.splitext(LOG_PATH)[0]
OUT_PATH = OUT_STEM + '.csv'
COE_PATH = OUT_STEM + '.coe'

PAGE_ID_ADDR = 114  # 0x72
SLAVE_ADDR_BITS = 0x00  # A4:A0

# addr(int) -> list of (reg_name, field_name, bit_hi, bit_lo)
regmap = {}
with open(REGMAP_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = int(row['addr'])
        hi, lo = row['bits'].split(':')
        hi, lo = int(hi), int(lo)
        regmap.setdefault(addr, []).append((row['reg_name'], row['field_name'], hi, lo))

LINE_RE = re.compile(r'^(setting|reading)\s+csr\[(0x[0-9a-fA-F]+)\].*?[=:]\s*(0x[0-9a-fA-F]+)\s*$')

entries = []  # (mode, addr, val) per matched log line
with open(LOG_PATH) as f:
    for line in f:
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        kind, addr_s, val_s = m.groups()
        mode = 'wr' if kind == 'setting' else 'rd'
        entries.append((mode, int(addr_s, 16), int(val_s, 16)))

# --- CSV: mode, reg_name, field_name, addr, value ---
rows = []
unknown_addrs = set()
current_page = None
for mode, addr, val in entries:
    if addr == PAGE_ID_ADDR:
        current_page = val

    if addr >= 256:
        page_s = hex(current_page) if current_page is not None else ''
        rows.append((mode, f'LUT - page_id<{page_s}>', 'LUT', hex(addr), hex(val)))
        continue

    fields = regmap.get(addr)
    if not fields:
        unknown_addrs.add(addr)
        rows.append((mode, 'UNKNOWN', 'UNKNOWN', hex(addr), hex(val)))
        continue

    for i, (reg_name, field_name, hi, lo) in enumerate(fields):
        mask = (1 << (hi - lo + 1)) - 1
        field_val = (val >> lo) & mask
        if i == 0:
            rows.append((mode, reg_name, field_name, hex(addr), hex(field_val)))
        else:
            rows.append((mode, '', field_name, '', hex(field_val)))

with open(OUT_PATH, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['mode', 'reg_name', 'field_name', 'addr', 'value'])
    writer.writerows(rows)

print(f'wrote {len(rows)} rows to {OUT_PATH}')
if unknown_addrs:
    print('addrs not found in regmap:', sorted(hex(a) for a in unknown_addrs))

# --- COE: one 24-bit word per write line in the log = 16-bit SPI address word + 1 value byte ---
# word: bit15=R/W (0=write), bit14=B (1=broadcast), bits13:9=A4:A0 (slave addr), bits8:0=register addr (9b)
# reads are excluded - only writes are programmed via the .coe
words = []
for mode, addr, val in entries:
    if mode != 'wr':
        continue
    rw = 0
    b_bit = 1
    addr9 = addr & 0x1FF
    spi_word = (rw << 15) | (b_bit << 14) | (SLAVE_ADDR_BITS << 9) | addr9
    combined = (spi_word << 8) | (val & 0xFF)
    words.append(f'{combined:06X}')

with open(COE_PATH, 'w', newline='\n') as f:
    f.write('memory_initialization_radix=16;\n')
    f.write('memory_initialization_vector=\n')
    f.write(',\n'.join(words))
    f.write(';\n')

print(f'wrote {len(words)} words to {COE_PATH}')
