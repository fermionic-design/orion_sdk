# -*- coding: utf-8 -*-
"""

TB name: ORION_8G_12G_Testbench--tb_ORION_12G_CHIP_TOP--maestro_temp_sense_copy
Current from VDD2p7 is 7.52mA

mode = 'single' : one PTAT + one ZTAT SAR ADC reading
mode = 'sweep'  : n_points PTAT + ZTAT SAR ADC readings, saved to a CSV in results/
"""

import sys
import os
import csv
import time
import statistics
from datetime import datetime

sys.path.append('../../include')

import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from SPI import *

# ------------------------------ USER SETTINGS ------------------------------
mode = 'single'          # 'single' or 'sweep'
chip_name = '53'
version = 'v2'
vdd = 2.7               # V, only used in the file name
temp = -40              # degC, only used in the file name
n_points = 1000         # sweep: number of PTAT/ZTAT reading pairs
eoc_timeout_s = 2.0     # max wait for EOC per conversion
settle_s = 0.01         # wait after switching PTAT <-> ZTAT before converting
point_interval_s = 0.5   # sweep: time from one PTAT/ZTAT pair to the next (start to start)

results_dir = r'G:\Shared drives\PRJ_BFM\BFM_X\Silicon Validation\SAR_ADC_Temp char_Ptat_Ztat'

# one row per run is appended here (single Excel for all runs)
summary_xlsx = os.path.join(results_dir, 'temp_sense__sar_adc__run_summary.xlsx')
run_results = {}   # filled during the run, written to summary_xlsx at the end


def fmt_num(x):
    "9.5 -> 9p5, 25 -> 25, -40 -> -40"
    s = f'{x:g}' if isinstance(x, (int, float)) else str(x)
    return s.replace('.', 'p')


def get_sar_adc_value(myDevice):
    "returns (adc_code, eoc). adc_code is None if EOC never went to 1"
    sar_adc_output = None

    RF_CTRL_FUNC.set_enable_adc(myDevice, 1)

    # poll EOC instead of a fixed 2 s wait
    eoc_read = 0
    t0 = time.time()
    while time.time() - t0 < eoc_timeout_s:
        eoc_read = RF_CTRL_FUNC.read_adc_eoc(myDevice)
        if eoc_read == 1:
            break

    # if eoc is 1 then read adc input and output
    if eoc_read == 1:
        sar_adc_output = RF_CTRL_FUNC.read_adc_output(myDevice)
    else:
        print("EOC is 0, SAR ADC conversion not complete")

    RF_CTRL_FUNC.set_enable_adc(myDevice, 0)

    return sar_adc_output, eoc_read


def read_temp_adc(myDevice, source):
    "source = 'ptat' or 'ztat'"
    RF_CTRL_FUNC.send_temp_to_adc(myDevice, source)
    time.sleep(settle_s)
    return get_sar_adc_value(myDevice)


def print_stats(name, codes):
    valid = [c for c in codes if c is not None]
    if not valid:
        print(f'{name}: no valid conversions')
        return
    std = statistics.stdev(valid) if len(valid) > 1 else 0.0
    print(f'{name}: n={len(valid)}  mean={statistics.mean(valid):.2f}  std={std:.3f}  '
          f'min={min(valid)}  max={max(valid)}')


def run_single(orion):
    # Connect Ptat voltage to GP7 pin via ADC input
    RF_CTRL_FUNC.send_temp_to_adc(orion, "ptat")
    RF_CTRL_FUNC.send_gp7_to_adc(orion, 1)



    run_results['ptat'] = get_sar_adc_value(orion)[0]
    print("PTAT SAR ADC Output: ", run_results['ptat'])

    # Connect Ztat voltage to GP7 pin via ADC input
    RF_CTRL_FUNC.send_temp_to_adc(orion, "ztat")
    RF_CTRL_FUNC.send_gp7_to_adc(orion, 1)


    run_results['ztat'] = get_sar_adc_value(orion)[0]
    print("ZTAT SAR ADC Output: ", run_results['ztat'])


def run_sweep(orion):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = (f'chip_{chip_name}__{version}__vdd_{fmt_num(vdd)}'
                 f'__temp_{n_points}_points_data__{fmt_num(temp)}C_{timestamp}.csv')
    os.makedirs(results_dir, exist_ok=True)
    file_path = os.path.join(results_dir, file_name)

    # ADC input = temperature sensor, GP7 disconnected
    RF_CTRL_FUNC.send_gp7_to_adc(orion, 0)
    RF_CTRL_FUNC.sel_adc_input(orion, "temp")

    ptat_codes, ztat_codes = [], []
    total_h = (n_points - 1) * point_interval_s / 3600
    print(f'Sweep: {n_points} points, {point_interval_s} s apart -> ~{total_h:.1f} h total')
    t_start = time.time()

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['point', 'time_s', 'ptat_sar_adc', 'ptat_eoc', 'ztat_sar_adc', 'ztat_eoc'])

        for i in range(n_points):
            # fixed 30 s grid: point i starts at t_start + i*point_interval_s (read time doesn't add drift)
            wait = t_start + i * point_interval_s - time.time()
            if wait > 0:
                time.sleep(wait)

            ptat, ptat_eoc = read_temp_adc(orion, "ptat")
            ztat, ztat_eoc = read_temp_adc(orion, "ztat")
            ptat_codes.append(ptat)
            ztat_codes.append(ztat)

            writer.writerow([i, f'{time.time() - t_start:.3f}',
                             '' if ptat is None else ptat, ptat_eoc,
                             '' if ztat is None else ztat, ztat_eoc])
            f.flush()   # keep data on disk if the run is stopped

            print(f'{i + 1}/{n_points}    PTAT={ptat}  ZTAT={ztat}')

    print(f'\nSaved: {file_path}')
    print_stats('PTAT', ptat_codes)
    print_stats('ZTAT', ztat_codes)
    n_fail = sum(c is None for c in ptat_codes + ztat_codes)
    if n_fail:
        print(f'WARNING: {n_fail} conversions had EOC = 0 (blank cells in CSV)')


# --------------------------------------------------------
spi = SPI()
orion = ORION_8G_12G(spi)

try:
    print('=' * 60)
    print(f'chip             : {chip_name}')
    print(f'version          : {version}')
    print(f'mode             : {mode}')
    print(f'vdd              : {vdd} V')
    print(f'temp             : {temp} C')
    print(f'n_points         : {n_points}  (sweep only)')
    print(f'point_interval_s : {point_interval_s}  (sweep only)')
    print(f'settle_s         : {settle_s}')
    print(f'eoc_timeout_s    : {eoc_timeout_s}')
    print('=' * 60)

    orion.DEVICE_ID.read()
    print('device_id = ' + hex(orion.DEVICE_ID.device_id))

    orion.REVISION.read()
    print('major_revision = ' + hex(orion.REVISION.major_rev))
    print('minor_revision = ' + hex(orion.REVISION.minor_rev))
    run_results['device_id'] = hex(orion.DEVICE_ID.device_id)
    run_results['revision'] = f'{orion.REVISION.major_rev}.{orion.REVISION.minor_rev}'

    if mode == 'single':
        run_single(orion)
    elif mode == 'sweep':
        run_sweep(orion)
    else:
        print(f"Unknown mode '{mode}', use 'single' or 'sweep'")

    print('-' * 60)
    print(f'Done: chip {chip_name} | {version} | mode {mode} | vdd {vdd} V | temp {temp} C')
    print('-' * 60)

    RF_CTRL_FUNC.send_temp_to_adc(orion, "ptat")
    RF_CTRL_FUNC.send_gp7_to_adc(orion, 1)

    spi.tr_reset()
    time.sleep(0.1)
    spi.tr_set()

    # print("Temp flash adc value: ",((orion.SPARE_ADC_TEMP_ADC_OUT_BIN.read() & 0b1111000) >> 3))
    # print("Temp 2-bit flash adc value: ",(orion.TEMP_IN_BIN.read() & 0b11))
    #
    # Calculate temperature as follows
    # temp_degC=(MP1-MZ1)*165/0.79+40
    # print('Temperature in degC: ', temp_degC)

except BaseException as e:
    run_results['status'] = 'stopped (Ctrl+C)' if isinstance(e, KeyboardInterrupt) else f'error: {e!r}'
    raise

finally:
    spi.close()

    # ---- single mode only: append one row for this run to the summary Excel (sweep data stays in its CSV) ----
    if mode == 'single':
        row = {'date': datetime.now().strftime('%Y-%m-%d'), 'time': datetime.now().strftime('%H:%M:%S'),
               'chip': chip_name, 'version': version, 'mode': mode, 'vdd': vdd, 'temp': temp,
               'n_points': '', 'point_interval_s': '',
               'settle_s': settle_s, 'eoc_timeout_s': eoc_timeout_s, 'status': 'ok'}
        row.update(run_results)
        try:
            from openpyxl import Workbook, load_workbook
            os.makedirs(results_dir, exist_ok=True)
            if os.path.exists(summary_xlsx):
                wb = load_workbook(summary_xlsx)
                ws = wb.active
            else:
                wb = Workbook()
                ws = wb.active
                ws.title = 'runs'
                ws.append(list(row.keys()))
            header = [c.value for c in ws[1]]
            for k in row:                       # new result names get a new column
                if k not in header:
                    header.append(k)
                    ws.cell(1, len(header), k)
            ws.append(['' if row.get(h) is None else row.get(h, '') for h in header])
            wb.save(summary_xlsx)
            print(f'Run summary row added: {summary_xlsx}')
        except PermissionError:
            print(f'Run summary NOT saved - close {summary_xlsx} in Excel. Row: {row}')
        except Exception as e:
            print(f'Run summary NOT saved ({e}). Row: {row}')
