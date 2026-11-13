# -*- coding: utf-8 -*-
"""
det_flash_adc_samp_delay_char.py

Measures the actual sampling delay of the DET flash ADC for each HAL delay case
(orion_hal.set_det_flash_adc_samp_delay(1..5)), reported to 0.01 us.

How it works
------------
  TR rising edge (FTDI GPIO)  --> chip: flash ADC samples T_adc after the edge
                              --> sig gen TRIG IN: RF pulse starts D after the edge

  The sig gen sends a triggered RF pulse (pulse modulation) with delay D, sweeping
  D from delay_start_us down to delay_stop_us (default 4.00 -> 0.00 us, editable in
  USER SETTINGS). The pulse is wider than the sweep window.
     D >  T_adc : RF is not there yet when the ADC samples  -> "no RF" code
     D <  T_adc : RF is already there when the ADC samples  -> "RF" code
  The D where the code flips (50 % detect point) = flash ADC sample delay.

  Sweep per case: coarse step (0.1 us) over the range, then a fine step (0.01 us)
  around the flip. Every delay point is read n_reads times (one TR pulse each).

Setup
-----
  - Sig gen RF out -> DETx port of the chip (det_mask below), other DETs 50 ohm.
  - Chip TR line (same signal the FTDI drives) -> sig gen TRIG IN (BNC).
    Use a tee so the chip still gets TR. Keep the cable short.
  - sgen_trig_latency_us: fixed sig gen trigger-in -> RF-out latency + cable delay.
    Measure once on a scope (TR edge vs RF burst) and enter it; it is added to the
    result. Leave 0 if not known (result is then relative to sig gen trigger).

Outputs (tests/char/logs)
-------------------------
  base = chip<id>__<version>__vdd<vdd>__det_flash_adc_samp_char__pin<pin_dbm>__temp<temp>__<timestamp>
  <base>__raw.csv      every read: case, expected delay, delay regs, sg delay, read idx, flash code
  <base>__summary.csv  per case: expected (HAL comment) vs actual delay + delay regs
  Delay regs (read back after each case is set):
    REG0_TX1 (0x86) bits[5:4] = tr_clk_delay_ctrl_1_0
    REG0_TX0 (0x84) bits[5:4] = tr_clk_delay_ctrl_3_2
  <base>.png           detect fraction vs delay, one curve per case
"""

import sys
import os
import csv
import time
from datetime import datetime

sys.path.append('../../include')

import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *

# ------------------------------ USER SETTINGS ------------------------------
chip_name = '55'
version = 'v2'
vdd = 2.7                # V, file name only
temp = 25                # degC, file name only

det_mask = 0x8           # DET0: 0x1, DET1: 0x2, DET2: 0x4, DET3: 0x8 (one detector)
det_sel = 1              # 1: RF + bias path, 2: bias only
hal_cases = [1, 2, 3, 4, 5]   # set_det_flash_adc_samp_delay() cases to characterise

# nominal delays from the HAL comments (us), only used for comparison in the summary
hal_nominal_us = {1: 0.60075, 2: 1.157, 3: 1.71325, 4: 2.047, 5: 2.269}

# sig gen
sgen_addr = 'USB0::0x0957::0x1F01::MY65280028::0::INSTR'
freq_ghz = 9.5
pin_dbm = 0              # RF level at the DET port; pick a level that gives a clear flash code change
pulse_width_us = 100.0    # must be > delay_start_us so the RF is still on at the sample instant
sgen_trig_latency_us = 0.0   # trigger-in -> RF-out latency + cable delay (added to the result)
# pulse setup: internal pulse generator in TRIGgered mode (one pulse per external trigger).
# Checked on N5173B (opt UNW): both commands below are accepted.
# ':TRIG:PULS:SOUR EXT' / ':TRIG:PULS:EXT:SLOP POS' are NOT valid on N5173B (-113 Undefined header).
# Set the trigger input / polarity on the front panel (Pulse menu) if needed.
sgen_trig_cmds = [
    ':PULM:SOUR INT',
    ':PULM:SOUR:INT TRIG',
]

# ------------------------------ DELAY SWEEP RANGE (us) ------------------------------
# sig gen pulse delay is swept from delay_start_us down to delay_stop_us.
# The range must contain the flash ADC sample delay of every case in hal_cases.
delay_start_us = 4.0     # sweep start (largest delay)
delay_stop_us = 0.0      # sweep end (smallest delay), >= 0
coarse_step_us = 0.1     # coarse step used to find the flip
fine_step_us = 0.01      # fine step around the flip = final resolution
fine_span_us = 0.2       # fine sweep covers flip +/- this
full_fine = False        # True: skip coarse, run the whole range at fine_step_us (slower)

run_preflight = True          # before the sweep: flash ADC with RF off / continuous RF / pulsed RF
preflight_stop_on_fail = True # stop if the pre-check shows the sweep can't work

n_reads = 5              # TR pulses / flash reads per delay point
tr_low_s = 0.002         # TR low time before the rising edge
tr_high_s = 0.005        # wait after the rising edge before reading (>> 4 us + pulse)

results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')   # tests/char/logs


def fmt_num(x):
    "9.5 -> 9p5, 25 -> 25, -10 -> m10"
    s = f'{x:g}' if isinstance(x, (int, float)) else str(x)
    return s.replace('.', 'p').replace('-', 'm')


def delay_grid(start, stop, step):
    "start..stop inclusive (either direction), rounded to 0.01 us"
    n = int(round(abs(stop - start) / step))
    sgn = -1 if stop < start else 1
    return [round(start + sgn * i * step, 2) for i in range(n + 1)]


# ------------------------------ SIG GEN ------------------------------
def sgen_cmd(sgen, cmd):
    "send one command and check the error queue, so a failure names the exact command"
    sgen.write(cmd)
    sgen.query('*OPC?')
    err = sgen.query(':SYST:ERR?').strip()
    if not (err.startswith('+0') or err.startswith('0')):
        raise RuntimeError(f'Sig gen rejected "{cmd}": {err}')


def sgen_init(sgen):
    sgen.write('*CLS')
    cmds = ([f':FREQ {freq_ghz}e9', f':POW {pin_dbm}']
            + sgen_trig_cmds
            + [f':PULM:INT:PWID {pulse_width_us * 1e-6:.9e}',
               f':PULM:INT:DEL {delay_start_us * 1e-6:.9e}',
               ':PULM:STAT ON',
               ':OUTP:MOD:STAT ON',
               ':OUTP:STAT ON'])
    for cmd in cmds:
        sgen_cmd(sgen, cmd)
    print('Sig gen setup OK: pulse source', sgen.query(':PULM:SOUR?').strip(),
          '/', sgen.query(':PULM:SOUR:INT?').strip(),
          ', width', sgen.query(':PULM:INT:PWID?').strip(), 's')


def sgen_set_delay(sgen, delay_us):
    sgen.write(f':PULM:INT:DEL {delay_us * 1e-6:.9e}')
    sgen.query('*OPC?')


# ------------------------------ MEASUREMENT ------------------------------
def read_point(spi, orion_hal, sgen, delay_us):
    "set sig gen delay, fire n_reads TR pulses, return list of flash codes"
    sgen_set_delay(sgen, delay_us)
    codes = []
    for _ in range(n_reads):
        spi.tr_reset()
        time.sleep(tr_low_s)
        spi.tr_set()            # rising edge: ADC sample timer + sig gen trigger start
        time.sleep(tr_high_s)
        codes.append(orion_hal.read_flash_adc_output(det_mask))
    spi.tr_reset()
    return codes


REG_HDR = ['reg0_tx1_addr', 'reg0_tx1_val', 'tr_clk_delay_ctrl_1_0',
           'reg0_tx0_addr', 'reg0_tx0_val', 'tr_clk_delay_ctrl_3_2', 'tr_clk_delay_ctrl_3_0']
reg_cols = {}   # case -> register columns for the CSVs (hex strings)


def reg_to_cols(r):
    return [f"0x{r['tx1_addr']:02X}", f"0x{r['tx1_val']:02X}", r['ctrl_1_0'],
            f"0x{r['tx0_addr']:02X}", f"0x{r['tx0_val']:02X}", r['ctrl_3_2'],
            f"0x{r['ctrl_3_0']:X}"]


def run_sweep(spi, orion_hal, sgen, delays, data, case, writer):
    "measure delays not yet in data[case]; data[case] = {delay_us: [codes]}"
    for d in delays:
        if d in data[case]:
            continue
        codes = read_point(spi, orion_hal, sgen, d)
        data[case][d] = codes
        for i, c in enumerate(codes):
            writer.writerow([case, hal_nominal_us.get(case, ''), *reg_cols[case], f'{d:.2f}', i, c])
        flash_dec = int(np.bincount(codes).argmax())   # most common of the n_reads reads
        print(f'  case {case}  delay {d:5.2f} us  flash ADC = {flash_dec}')


def detect_fraction(points, no_rf_code, rf_code):
    "points: {delay: [codes]} -> sorted delays, fraction of reads closer to rf_code"
    ds = sorted(points)
    frac = []
    for d in ds:
        c = np.array(points[d])
        frac.append(float(np.mean(np.abs(c - rf_code) < np.abs(c - no_rf_code))))
    return np.array(ds), np.array(frac)


def find_flip(points, no_rf_code, rf_code):
    """50 % detect point in us (linear interpolation), or None.
    Small delay -> detected (1), large delay -> not detected (0)."""
    ds, frac = detect_fraction(points, no_rf_code, rf_code)
    for k in range(len(ds) - 1):
        if frac[k] >= 0.5 > frac[k + 1]:
            f0, f1 = frac[k], frac[k + 1]
            return ds[k] + (f0 - 0.5) / (f0 - f1) * (ds[k + 1] - ds[k])
    return None


def ref_codes(points):
    "no-RF code = most common code at the largest delay, RF code = at the smallest delay"
    ds = sorted(points)
    no_rf = int(np.bincount(points[ds[-1]]).argmax())
    rf = int(np.bincount(points[ds[0]]).argmax())
    return no_rf, rf


def read_delay_regs(orion_csr):
    """read back the registers set_det_flash_adc_samp_delay() writes.
    REG0_TX1[5:4] = tr_clk_delay_ctrl_1_0, REG0_TX0[5:4] = tr_clk_delay_ctrl_3_2"""
    tx1_val = orion_csr.REG0_TX1.read()
    tx0_val = orion_csr.REG0_TX0.read()
    f10 = orion_csr.REG0_TX1.tr_clk_delay_ctrl_1_0
    f32 = orion_csr.REG0_TX0.tr_clk_delay_ctrl_3_2
    return {
        'tx1_addr': orion_csr.REG0_TX1._addr, 'tx1_val': tx1_val, 'ctrl_1_0': f10,
        'tx0_addr': orion_csr.REG0_TX0._addr, 'tx0_val': tx0_val, 'ctrl_3_2': f32,
        'ctrl_3_0': (f32 << 2) | f10,
    }


def fmt_regs(r):
    return (f"REG0_TX1 @0x{r['tx1_addr']:02X} = 0x{r['tx1_val']:02X} (tr_clk_delay_ctrl_1_0 = {r['ctrl_1_0']}), "
            f"REG0_TX0 @0x{r['tx0_addr']:02X} = 0x{r['tx0_val']:02X} (tr_clk_delay_ctrl_3_2 = {r['ctrl_3_2']}), "
            f"tr_clk_delay_ctrl[3:0] = 0x{r['ctrl_3_0']:X}")


def flash_reads(spi, orion_hal, n=5):
    "n TR pulses at the current sig gen state, returns list of flash codes"
    codes = []
    for _ in range(n):
        spi.tr_reset()
        time.sleep(tr_low_s)
        spi.tr_set()
        time.sleep(tr_high_s)
        codes.append(orion_hal.read_flash_adc_output(det_mask))
    spi.tr_reset()
    return codes


def dump_det_regs(orion_csr):
    for name in ['TR_CFG', 'TR_CTRL_2', 'POWER_DET_CFG', 'DET_0_1_ADC_OUT_BIN', 'DET_2_3_ADC_OUT_BIN']:
        r = getattr(orion_csr, name)
        print(f'    {name:20s} @0x{r._addr:02X} = 0x{r.read():02X}')


def preflight(spi, orion_hal, sgen):
    """3 quick checks before the sweep, so an all-0 flash output is explained:
       A RF off, B continuous RF (no pulse), C triggered pulse with 0 delay."""
    print('\n--- pre-check (DET mask 0x%X, %g GHz, %g dBm) ---' % (det_mask, freq_ghz, pin_dbm))
    sgen_cmd(sgen, ':OUTP:STAT OFF')
    a = flash_reads(spi, orion_hal)
    sgen_cmd(sgen, ':PULM:STAT OFF')
    sgen_cmd(sgen, ':OUTP:STAT ON')
    time.sleep(0.2)
    b = flash_reads(spi, orion_hal)
    sgen_cmd(sgen, f':PULM:INT:DEL {0:.9e}')
    sgen_cmd(sgen, ':PULM:STAT ON')
    time.sleep(0.2)
    c = flash_reads(spi, orion_hal)
    print(f'  A  RF off              : flash ADC = {a}')
    print(f'  B  RF on, continuous   : flash ADC = {b}')
    print(f'  C  RF pulsed, delay 0  : flash ADC = {c}')
    dump_det_regs(orion_hal.orion_csr)

    if max(b) == 0:
        msg = ('flash ADC stays 0 even with continuous RF -> problem is on the chip / cable side, '
               'not the trigger: check RF is reaching the DET port selected by det_mask '
               '(measure at the chip-end of the cable), pin_dbm, det_mask vs the port cabled, '
               'and that bfm_DETx_Flash_ADC_Test.py gives non-zero with CW RF on this port.')
    elif max(c) == 0:
        msg = ('flash ADC responds to continuous RF but not to the triggered pulse -> the sig gen '
               'is not being triggered by TR: check the TR -> sig gen trigger cable, the trigger '
               'input/polarity in the Pulse menu, and the TR voltage level.')
    elif min(b) == max(a):
        msg = 'RF on and RF off give the same flash code -> raise pin_dbm.'
    else:
        print('  pre-check OK')
        return
    print('  PRE-CHECK FAILED: ' + msg)
    if preflight_stop_on_fail:
        raise RuntimeError('pre-check failed, sweep not started (see message above)')


def characterise_case(spi, orion_hal, sgen, case, data, writer, regs):
    print(f'\n=== HAL case {case} (nominal {hal_nominal_us.get(case, "?")} us) ===')
    orion_hal.set_det_flash_adc_samp_delay(case)
    regs[case] = read_delay_regs(orion_hal.orion_csr)
    reg_cols[case] = reg_to_cols(regs[case])
    print('  ' + fmt_regs(regs[case]))
    data[case] = {}

    step = fine_step_us if full_fine else coarse_step_us
    run_sweep(spi, orion_hal, sgen, delay_grid(delay_start_us, delay_stop_us, step), data, case, writer)

    no_rf, rf = ref_codes(data[case])
    if no_rf == rf:
        print(f'  case {case}: flash code does not change across the sweep ({no_rf}). '
              f'Check pin_dbm / cabling / trigger.')
        return None, no_rf, rf

    flip = find_flip(data[case], no_rf, rf)
    if flip is None:
        print(f'  case {case}: no clean flip found')
        return None, no_rf, rf

    if not full_fine:
        lo = max(delay_stop_us, round(flip - fine_span_us, 2))
        hi = min(delay_start_us, round(flip + fine_span_us, 2))
        run_sweep(spi, orion_hal, sgen, delay_grid(hi, lo, fine_step_us), data, case, writer)
        # only use the fine region for the final interpolation
        fine_pts = {d: c for d, c in data[case].items() if lo - 1e-9 <= d <= hi + 1e-9}
        flip = find_flip(fine_pts, no_rf, rf) or flip

    meas = round(flip + sgen_trig_latency_us, 2)
    print(f'  case {case}: no-RF code {no_rf}, RF code {rf} -> sample delay {meas:.2f} us')
    return meas, no_rf, rf


def plot_results(data, refs, summary, png_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    for case in data:
        no_rf, rf = refs[case]
        if no_rf == rf:
            continue
        ds, frac = detect_fraction(data[case], no_rf, rf)
        meas = summary[case]['meas_us']
        lbl = f'case {case}: ' + (f'{meas:.2f} us' if meas is not None else 'n/a')
        line, = ax.plot(ds + sgen_trig_latency_us, frac, '.-', label=lbl)
        if meas is not None:
            ax.axvline(meas, color=line.get_color(), ls='--', lw=0.8)
    ax.axhline(0.5, color='grey', lw=0.6)
    ax.set_xlabel('RF arrival delay after TR edge (us)')
    ax.set_ylabel('Fraction of reads with RF detected')
    ax.set_title(f'Flash ADC sample delay, chip {chip_name}, DET mask {hex(det_mask)}, '
                 f'{freq_ghz} GHz, {pin_dbm} dBm')
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(png_path, dpi=150)
    print('Plot:', png_path)
    plt.show()


def main():
    if not (delay_start_us > delay_stop_us >= 0):
        raise ValueError('need delay_start_us > delay_stop_us >= 0')
    if pulse_width_us <= delay_start_us:
        raise ValueError('pulse_width_us must be > delay_start_us (RF must still be on at the sample)')

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = (f'chip{chip_name}__{version}__vdd{fmt_num(vdd)}'
            f'__det_flash_adc_samp_char__pin{fmt_num(pin_dbm)}__temp{fmt_num(temp)}__{ts}')
    os.makedirs(results_dir, exist_ok=True)
    raw_path = os.path.join(results_dir, f'{base}__raw.csv')
    sum_path = os.path.join(results_dir, f'{base}__summary.csv')
    png_path = os.path.join(results_dir, f'{base}.png')
    print(f'Delay sweep: {delay_start_us:.2f} -> {delay_stop_us:.2f} us')

    rm = pyvisa.ResourceManager()
    sgen = rm.open_resource(sgen_addr)
    sgen.timeout = 10000
    print('Sig gen:', sgen.query('*IDN?').strip())

    spi = SPI()
    orion_csr = ORION_8G_12G(spi)
    orion_lut = ORION_8G_12G_lut(spi)
    orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

    orion_csr.DEVICE_ID.read()
    print('device_id = ' + hex(orion_csr.DEVICE_ID.device_id))

    data, refs, summary, regs = {}, {}, {}, {}
    try:
        sgen_init(sgen)

        # external TR: chip follows the TR pin driven by spi.tr_set()/tr_reset()
        # TR_CFG (0xAC) bit0 tr_mode_sel: 0 = EXT_TR (TR pin), 1 = INT_TR (TR_SW_CTRL register)
        # TR_CFG bit1 data_path_en: 1 = data path enabled
        orion_hal.set_tr_mode('EXT_TR')
        orion_hal.en_data_path(1)
        tr_cfg = orion_csr.TR_CFG.read()
        print(f'TR_CFG @0x{orion_csr.TR_CFG._addr:02X} = 0x{tr_cfg:02X} '
              f'(tr_mode_sel = {orion_csr.TR_CFG.tr_mode_sel} -> '
              f'{"EXT_TR" if orion_csr.TR_CFG.tr_mode_sel == 0 else "INT_TR"}, '
              f'data_path_en = {orion_csr.TR_CFG.data_path_en})')
        if orion_csr.TR_CFG.tr_mode_sel != 0 or orion_csr.TR_CFG.data_path_en != 1:
            raise RuntimeError('TR_CFG readback wrong: expected tr_mode_sel = 0 (EXT_TR), data_path_en = 1')

        orion_hal.set_detector_channel(det_mask, det_sel)
        orion_hal.set_enable_pkdet(det_mask)
        spi.tr_reset()

        orion_hal.set_det_flash_adc_samp_delay(5)   # default delay for the pre-check
        if run_preflight:
            preflight(spi, orion_hal, sgen)

        with open(raw_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['hal_case', 'expected_us', *REG_HDR, 'sgen_delay_us', 'read_idx', 'flash_code'])
            for case in hal_cases:
                meas, no_rf, rf = characterise_case(spi, orion_hal, sgen, case, data, writer, regs)
                refs[case] = (no_rf, rf)
                nom = hal_nominal_us.get(case)
                summary[case] = {'meas_us': meas, 'nom_us': nom, 'no_rf': no_rf, 'rf': rf}
                f.flush()

                exp_s = f'{nom:.5f} us' if nom is not None else 'n/a'
                act_s = f'{meas:.2f} us' if meas is not None else 'n/a'
                diff_s = f'  (diff {round(meas - nom, 2) + 0.0:+.2f} us)' if meas is not None and nom is not None else ''
                print(f'\n---------------- case {case} done ----------------')
                print(f'  case id        : {case}')
                print(f'  expected delay : {exp_s}')
                print(f'  actual delay   : {act_s}{diff_s}')
                print(f'  registers      : {fmt_regs(regs[case])}')
                print('-------------------------------------------------')
    finally:
        sgen.write(':OUTP:STAT OFF')
        orion_hal.set_det_flash_adc_samp_delay(5)   # back to default
        orion_hal.reset_all_det_sel()
        orion_hal.set_enable_pkdet(0)
        spi.tr_reset()

        if summary:
            with open(sum_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['hal_case', 'expected_us', 'actual_us', 'actual_minus_expected_us',
                                 *REG_HDR, 'no_rf_code', 'rf_code', 'sgen_trig_latency_us'])
                for case, s in summary.items():
                    diff = (round(s['meas_us'] - s['nom_us'], 2)
                            if s['meas_us'] is not None and s['nom_us'] is not None else '')
                    writer.writerow([case, s['nom_us'],
                                     f"{s['meas_us']:.2f}" if s['meas_us'] is not None else '',
                                     diff, *reg_cols[case], s['no_rf'], s['rf'], sgen_trig_latency_us])

            print('\n case | expected (us) | actual (us) | diff (us) | REG0_TX1 (addr=val) | REG0_TX0 (addr=val) | ctrl[3:0]')
            for case, s in summary.items():
                m = f"{s['meas_us']:.2f}" if s['meas_us'] is not None else 'n/a'
                d = (f"{round(s['meas_us'] - s['nom_us'], 2) + 0.0:+.2f}"
                     if s['meas_us'] is not None and s['nom_us'] is not None else '')
                e = f"{s['nom_us']:.5f}" if s['nom_us'] is not None else 'n/a'
                c = reg_cols[case]
                print(f' {case:4d} | {e:>13} | {m:>11} | {d:>9} | {c[0]}={c[1]:<13} | {c[3]}={c[4]:<13} | {c[6]}')
            print('\nRaw:    ', raw_path)
            print('Summary:', sum_path)

        spi.close()
        sgen.close()

    if summary:
        plot_results(data, refs, summary, png_path)


if __name__ == '__main__':
    main()
