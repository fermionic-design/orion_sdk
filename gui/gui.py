import sys
import os
import time
import threading

# Anchor the working directory to the app folder so the relative paths
# (../include, ../regs, ../final_lut, ../tests) resolve no matter where the
# app is launched from. When frozen by PyInstaller, that is the exe's folder.
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# from include.ORION_8G_12G import ORION_8G_12G
# from include.ORION_8G_12G_lut import ORION_8G_12G_lut

sys.path.append('../include')
import tkinter as tk
from tkinter import ttk
import csv
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import serial.tools.list_ports
import re
import random
import subprocess
import pyvisa
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from instruments import instruments as instruments_cls

spi = None
orion = None
orion_lut = None
orion_hal = None
rm = None
instruments = None

# VNA frequency sweep settings, also used to derive the trace point frequencies
vna_freq_start = 7e9
vna_freq_stop = 13e9
vna_freq_step = 250e6

# Data captured by the last run_sweep: one gain/phase trace per sweep step
sweep_data = {'mode': None, 'trx_mode': None, 'channel': None, 'idx': [], 'gain': [], 'phase': []}

tx_en = 0
rx_en = 0

status = {}


def update_status_bar():
    global status_bar
    status_bar_text = ''
    for i in status.items():
        # print(f'{i[0]}: {i[1]}')
        status_bar_text += f'{i[0]}: {i[1]}\t\t'
    status_bar.config(text=status_bar_text)


def scan_ports():
    ports = serial.tools.list_ports.comports()
    usb_ports = [port for port in ports if "USB" in port.hwid]
    if usb_ports:
        for port in usb_ports:
            print(f"[{port.device}] {port.description} [{port.hwid}]")
    else:
        print("No USB COM ports available.")
    return usb_ports


def connect(port_string):
    global spi
    global orion
    global orion_lut
    global orion_hal

    print(f'Connect: {port_string}')
    match = re.search(r'\b(COM\d+)\b', port_string)
    good = 1
    if match:
        port = match.group(1)
        spi = SPI(port)
        orion = ORION_8G_12G(spi)
        orion_lut = ORION_8G_12G_lut(spi)
        orion_hal = ORION_8G_12G_hal(orion, orion_lut, spi)

        orion.DEVICE_ID.read()
        # print('device_id = ' + hex(orion.DEVICE_ID.device_id))
        if orion.DEVICE_ID.device_id != 0xF2:
            good = 0

        orion.REVISION.read()
        # print('major_revision = ' + hex(orion.REVISION.major_rev))
        # print('minor_revision = ' + hex(orion.REVISION.minor_rev))
        if orion.REVISION.major_rev != 1 or orion.REVISION.minor_rev != 1:
            good = 0

        # orion.PHASE_CODE_TX0.read()
        # print('phase_code_tx0 = ' + hex(orion.PHASE_CODE_TX0.phase_code_tx0))

        orion.PHASE_CODE_TX0.phase_code_tx0 = 0x5A
        orion.PHASE_CODE_TX0.write()
        orion.PHASE_CODE_TX0.read()
        # print('phase_code_tx0 = ' + hex(orion.PHASE_CODE_TX0.phase_code_tx0))
        if orion.PHASE_CODE_TX0.phase_code_tx0 != 0x5A:
            good = 0

        orion.PHASE_CODE_TX0.phase_code_tx0 = 0x00
        orion.PHASE_CODE_TX0.write()
        orion.PHASE_CODE_TX0.read()
        if orion.PHASE_CODE_TX0.phase_code_tx0 != 0x00:
            good = 0

        if good:
            print('Connection SUCCESS: Sanity Passed')
            status['Status'] = f'Connected @ {port}'
            update_status_bar()
        else:
            print('Sanity Failed')


def disconnect():
    global spi
    spi.close()
    status['Status'] = 'Disconnected'
    update_status_bar()


def connect_vna(resource):
    global instruments

    print(f'Connect VNA: {resource}')
    if not resource:
        print('No instrument selected')
        return

    instruments = instruments_cls(required_instruments=[], vna_id=resource)
    if instruments.vna is None:
        print('VNA connection failed')
        return

    instruments.vna.init()
    instruments.vna.cfg(1, 'S21_GAIN')
    instruments.vna.cfg(2, 'S21_PHASE')
    instruments.vna.cfg_freq(start=vna_freq_start, stop=vna_freq_stop, step=vna_freq_step)
    instruments.vna.cfg_pwr(pwr=-20)

    instruments.vna.add_marker(win_id=1, marker_id=1, val=8e9)
    instruments.vna.add_marker(win_id=1, marker_id=2, val=10e9)
    instruments.vna.add_marker(win_id=1, marker_id=3, val=12e9)

    instruments.vna.add_marker(win_id=2, marker_id=1, val=8e9)
    instruments.vna.add_marker(win_id=2, marker_id=2, val=10e9)
    instruments.vna.add_marker(win_id=2, marker_id=3, val=12e9)

    instruments.vna.set_y_axis(win_id=1, ref_level=-20, scale_per_div=5)
    instruments.vna.set_y_axis(win_id=2, ref_level=0, scale_per_div=45)

    instruments.vna.norm(win_id=2)

    status['VNA'] = 'Connected'
    update_status_bar()


def init_rf(bias_mode, tr_mode, trx_mode, stg2_load_cfg, rf_en):
    global orion_hal
    # print(f'Init RF: {bias_mode}')

    # orion_hal.init_lut(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    #                     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Phase_LUT_10p5GHz.xlsx',
    #                     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/RX_Gain_LUT_9GHz_NomBias.xlsx',
    #                     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/RX_Phase_LUT_11GHz_NomBias.xlsx',
    #                     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/RX_Gain_LUT_9GHz_NomBias.xlsx',
    #                     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/RX_Phase_LUT_11GHz_NomBias.xlsx')
    # orion_hal.init_lut(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/demo/TX_Gain_LUT_10p5GHz_Demo.xlsx',
    #                    r'C:/Users/silic/OneDrive/Documents/GitHub/orion/demo/TX_Phase_LUT_10p5GHz_Demo.xlsx',
    #                    r'C:/Users/silic/OneDrive/Documents/GitHub/orion/demo/RX_Gain_LUT_9GHz_NomBias_Demo.xlsx',
    #                    r'C:/Users/silic/OneDrive/Documents/GitHub/orion/demo/RX_Phase_LUT_9GHz_NomBias_Demo.xlsx',
    #                    r'C:/Users/silic/OneDrive/Documents/GitHub/orion/demo/RX_Gain_LUT_11GHz_NomBias_Demo.xlsx',
    #                    r'C:/Users/silic/OneDrive/Documents/GitHub/orion/demo/RX_Phase_LUT_11GHz_NomBias_Demo.xlsx')

    version = 'v2'  # TODO: put this in a proper place
    #TODO: the paths should not be relative paths
    if version == 'v2':
        orion_hal.init_lut_new(r'../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                               r'../final_lut/tx_v2__phase_lut_freq_14p25_gm_0p5_pm_1p5_pm2_4_abs_gain_8__maxbias__vdd_2p7.xlsx',
                               r'../final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
                               r'../final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
                               r'../final_lut/v2__rx2__gain_lut__9p5GHz__lowbias_00__vdd_2p7_with_avg_for_dual_lut.xlsx',
                               r'../final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_15__lowbias_00__vdd_2p5.xlsx')
    else:
        orion_hal.init_lut_new(r'../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                               r'../results/final_lut/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                               r'../final_lut/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                               r'../final_lut/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
                               r'../final_lut/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                               r'../final_lut/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

    print(f'LUT Initialized')

    print(f'TR Mode: {tr_mode}, TRX Mode: {trx_mode}')
    if (bias_mode == 'Normal'):
        if trx_mode == 'TX':
            print(f'Init TX: {bias_mode}')
            orion_hal.init_tx('NOM')
        else:
            print(f'Init RX: {bias_mode}')
            orion_hal.init_rx('NOM')
    else:
        if trx_mode == 'TX':
            print(f'Init TX: {bias_mode}')
            orion_hal.init_tx('LOW')
        else:
            print(f'Init RX: {bias_mode}')
            orion_hal.init_rx('LOW')

    ch_en = 0
    for i in range(4):
        print(f'CH[{i}]: En: {rf_en[i].get()}')
        ch_en = ch_en + (rf_en[i].get() << i)
    print(f'ch_en = {ch_en}')

    # TEMP
    if tr_mode == 'Register':
        orion_hal.set_tr_mode('INT_TR')
    else:
        orion_hal.set_tr_mode('EXT_TR')

    if trx_mode == 'TX':
        orion_hal.set_trx_mode(1)
    else:
        orion_hal.set_trx_mode(0)

    orion_hal.set_tr_mask(rx_mask=rx_en, tx_mask=tx_en)
    orion_hal.cfg_stg2_load('REG' if stg2_load_cfg == 'Register' else 'PIN')
    orion_hal.enable_rx_correction(1)
    orion_hal.en_data_path(1)

    status['RF'] = f'Initialized @ {bias_mode}'
    update_status_bar()


def change_tr_mode(tr_mode):
    print(f'TR Control Mode: {tr_mode}')
    if orion_hal is None:
        return
    if tr_mode=='Register':
        orion_hal.set_tr_mode('INT_TR')
    else:
        orion_hal.set_tr_mode('EXT_TR')


def update_ch_entry_state(rf_en, entry_lists):
    for i in range(4):
        state = 'normal' if rf_en[i].get() else 'disabled'
        for entries in entry_lists:
            entries[i].config(state=state)


def update_ch_en(trx_mode, rf_en, entry_lists):
    global tx_en, rx_en
    mask = 0
    for i in range(4):
        mask |= rf_en[i].get() << i
    if trx_mode == 'TX':
        tx_en = mask
    else:
        rx_en = mask
    print(f'tx_en = {bin(tx_en)}, rx_en = {bin(rx_en)}')

    update_ch_entry_state(rf_en, entry_lists)

    if orion_hal is not None:
        orion_hal.set_tr_mask(tx_mask=tx_en, rx_mask=rx_en)


def change_trx_mode(trx_mode, rf_en, entry_lists):
    print(f'TRX Mode: {trx_mode}')
    if trx_mode=='RX':
        if orion_hal is not None:
            orion_hal.set_trx_mode(0)
        mask = rx_en
    else:
        if orion_hal is not None:
            orion_hal.set_trx_mode(1)
        mask = tx_en
    for i in range(4):
        rf_en[i].set((mask >> i) & 1)
    update_ch_entry_state(rf_en, entry_lists)


def change_stg2_load_cfg(stg2_load_cfg):
    print(f'STG2 Load Cfg: {stg2_load_cfg}')
    if orion_hal is None:
        return
    orion_hal.cfg_stg2_load('REG' if stg2_load_cfg == 'Register' else 'PIN')


def load_rf(rf_en, rf_gain_entries, rf_phase_entries, pa_on_bias_entries, pa_off_bias_entries, lna_on_bias_entries,
            lna_off_bias_entries):
    global orion_hal
    print('Load RF')
    # print(round(int(rf_phase_entries[0].get()) / 2.975)+4)
    # print(round(int(rf_gain_entries[0].get()) / 0.5))
    # orion_hal.set_lut_idx(round(int(rf_phase_entries[0].get()) / 2.975)+4,round(int(rf_gain_entries[0].get()) / 0.5), 0x1)
    # orion_hal.stg2_load()

    ant_sel = 0
    for i in range(4):
        print(f'CH[{i}]: En: {rf_en[i].get()}\t\tGain:{rf_gain_entries[i].get()}\t\tPhase: {rf_phase_entries[i].get()}'
              f'\t\tPA_ON_Bias: {pa_on_bias_entries[i].get()}\t\tPA_OFF_Bias: {pa_off_bias_entries[i].get()}'
              f'\t\tLNA_ON_Bias: {lna_on_bias_entries[i].get()}\t\tLNA_OFF_Bias: {lna_off_bias_entries[i].get()}')
        ant_sel = rf_en[i].get() << i
        print(f'Phase = {rf_phase_entries[i].get()}, Gain = {rf_gain_entries[i].get()}, ant_sel = {ant_sel}')
        # print(type(round(int(rf_phase_entries[i].get()/2.8))))
        if orion_hal.trx_mode:
            orion_hal.set_lut_idx(round(int(rf_phase_entries[i].get()) / 2.8125),
                                  round(int(rf_gain_entries[i].get()) / 0.5), ant_sel)
        else:
            orion_hal.set_freq('9G')
            # orion_hal.enable_rx_correction(1)
            orion_hal.set_lut_idx(round(float(rf_phase_entries[i].get()) / 2.975) + 4,
                                  round((float(rf_gain_entries[i].get())) / 0.5), ant_sel)
            # orion_hal.set_lut_idx(round(int(rf_phase_entries[0].get()) / 2.975) + 4,
            #                       round(int(rf_gain_entries[0].get()) / 0.5), ant_sel)
            # orion_hal.set_lut_idx(round(int(rf_phase_entries[0].get()) / 2.975) + 4,
            #                       round(int(rf_gain_entries[0].get()) / 0.5), ant_sel<<1)
            # orion_hal.set_lut_idx(round(abs(rf_phase_entries[i].get())/2.975)+4, round((int(rf_gain_entries[i].get())+1)/0.5), ant_sel)
        orion_hal.stg2_load()


def update_bias(rf_en, pa_on_bias_entries, pa_off_bias_entries, lna_on_bias_entries, lna_off_bias_entries):
    global orion_hal
    print('Update Bias')

    ch_sel = 0
    dac_vals = {}
    for i in range(4):
        ch_sel |= rf_en[i].get() << i
        dac_vals[f'PA{i}'] = int(pa_on_bias_entries[i].get())
        dac_vals[f'PA{i}_PDN'] = int(pa_off_bias_entries[i].get())
        dac_vals[f'LNA{i}'] = int(lna_on_bias_entries[i].get())
        dac_vals[f'LNA{i}_PDN'] = int(lna_off_bias_entries[i].get())
        print(f'CH[{i}]: En: {rf_en[i].get()}\t\tPA_ON: {dac_vals[f"PA{i}"]}\t\tPA_OFF: {dac_vals[f"PA{i}_PDN"]}'
              f'\t\tLNA_ON: {dac_vals[f"LNA{i}"]}\t\tLNA_OFF: {dac_vals[f"LNA{i}_PDN"]}')

    print(f'ch_sel = {bin(ch_sel)}')
    orion_hal.dac_cfg(ch_sel, ch_sel, **dac_vals)


def adc_setup(osc_en, adc_sel):
    print(f'ADC Setup: OSC_EN = {osc_en}, ADC_SEL = {adc_sel}')


def adc_read(entry__adc_val):
    print('ADC Read')
    entry__adc_val.config(state='normal')
    entry__adc_val.delete(0, tk.END)
    entry__adc_val.insert(0, random.randint(0, 255))
    entry__adc_val.config(state='readonly')


def write_register_manual(addr, val):
    # print(f'Write Register Manual: {addr}, {val}')
    global spi
    spi.write(int(addr, 16), int(val, 16))


def read_register_manual(addr, entry__reg_val):
    # print(f'Read Register Manual: {addr}')
    global spi
    val = spi.read(int(addr, 16))
    entry__reg_val.delete(0, tk.END)
    entry__reg_val.insert(0, hex(val))


def read_all_registers(entries, field_reg_dict):
    global orion
    orion.read_all()
    for field_name, entry in entries.items():

        # This is a hack for tkinter timing issue
        # with open(os.devnull, 'w') as f:
        #     sys.stdout = f  # Redirect stdout
        #     print(f'{field_name}, {entry.cget('state')}')
        #     sys.stdout = sys.__stdout__  # Restore stdout
        #     f.close()

        state = str(entry.cget('state')).strip()
        # if entry.cget('state') == 'readonly':
        if state == 'readonly':
            entry.config(state='normal')
            entry.delete(0, tk.END)
            register_name = field_reg_dict.get(field_name)
            # print(register_name)
            entry.insert(0, hex(getattr(getattr(orion, register_name), field_name)))
            entry.config(state='readonly')
        else:
            entry.delete(0, tk.END)
            register_name = field_reg_dict.get(field_name)
            # print(register_name)
            entry.insert(0, hex(getattr(getattr(orion, register_name), field_name)))


def write_register(entries, register_name):
    global orion
    for name, value in vars(getattr(orion, register_name)).items():
        if not name.startswith('_') and name not in ['dev']:
            setattr(getattr(orion, register_name), name, int(entries[name].get(), 16))
    getattr(orion, register_name).write()


def read_register(entries, register_name):
    global orion
    getattr(orion, register_name).read()
    for name, value in vars(getattr(orion, register_name)).items():
        if not name.startswith('_') and name not in ['dev']:
            # This is a hack for tkinter timing issue
            # with open(os.devnull, 'w') as f:
            #     sys.stdout = f  # Redirect stdout
            #     print(f'{name}, {entries[name].cget('state')}')
            #     sys.stdout = sys.__stdout__  # Restore stdout
            #     f.close()

            state = str(entries[name].cget('state')).strip()
            # print(f'state = {state}')
            # if entries[name].cget('state') == 'readonly':
            if state == 'readonly':
                # print('readonly')
                entries[name].config(state='normal')
                entries[name].delete(0, tk.END)
                entries[name].insert(0, hex(value))
                entries[name].config(state='readonly')
            else:
                # print('normal')
                entries[name].delete(0, tk.END)
                entries[name].insert(0, hex(value))


def sync_reset():
    global orion
    orion.SYNC_RST.sync_rst = 0x01
    orion.SYNC_RST.write()
    orion.SYNC_RST.sync_rst = 0x00
    orion.SYNC_RST.write()
    status['RF'] = 'Not Initialized @ Sync Reset Done'
    update_status_bar()
    print('Sync Reset Done')


def run_script(script):
    global script_dir
    print(f'Run Script: {script}')
    subprocess.run(["python", f"{script_dir}/{script}"], shell=True)
    print(f'Script {script} executed')


def display__tab_setup():
    # ttk.Label(tab_setup, text ="Setup the Device").grid(column = 0, row = 0, padx = 30,pady = 30)
    usb_ports = scan_ports()

    ttk.Label(tab_setup, text="PORT").grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

    options = usb_ports
    combobox__ports = ttk.Combobox(tab_setup, values=options, state="readonly", width=30)
    combobox__ports.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")
    if options != []:
        combobox__ports.current(0)  # Set default selection

    ttk.Button(tab_setup, text="Connect", command=lambda: connect(combobox__ports.get())).grid(column=2, row=0, padx=10,
                                                                                               pady=10, sticky="nsew")
    ttk.Button(tab_setup, text="Disconnect", command=lambda: disconnect()).grid(column=3, row=0, padx=10, pady=10,
                                                                                sticky="nsew")
    ttk.Button(tab_setup, text="Scan", command=scan_ports).grid(column=4, row=0, padx=10, pady=10, sticky="nsew")

    ttk.Separator(tab_setup, orient='horizontal').grid(column=0, row=1, columnspan=5, sticky='ew', pady=5)

    global rm
    visa_resources = ()
    try:
        rm = pyvisa.ResourceManager()
        visa_resources = rm.list_resources()
        print('\nInstruments Available: ', visa_resources)
    except Exception as e:
        print(f'VISA not available: {e}')

    ttk.Label(tab_setup, text="VISA Instruments").grid(column=0, row=2, padx=10, pady=10, sticky="nsew")
    combobox__visa = ttk.Combobox(tab_setup, values=list(visa_resources), state="readonly", width=40)
    combobox__visa.grid(column=1, row=2, padx=10, pady=10, sticky="nsew")
    if visa_resources:
        combobox__visa.current(0)

    ttk.Button(tab_setup, text="Connect VNA",
               command=lambda: connect_vna(combobox__visa.get())).grid(column=2, row=2, padx=10, pady=10,
                                                                       sticky="nsew")


def display__tab_registers():
    global orion

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(tab_registers, borderwidth=0)  # Set borderwidth to 0
    scrollbar = ttk.Scrollbar(tab_registers, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, borderwidth=0)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    # Bind mouse scroll event
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    entries = {}
    field_reg_dict = {}

    # Add a button to read all registers
    ttk.Button(scrollable_frame, text="Read All Registers",
               command=lambda: read_all_registers(entries, field_reg_dict)).grid(column=0, row=0, padx=5, pady=5,
                                                                                 sticky="nsew")
    ttk.Button(scrollable_frame, text="Sync Reset", command=lambda: sync_reset()).grid(column=1, row=0, padx=5, pady=5,
                                                                                       sticky="nsew")

    ttk.Separator(scrollable_frame, orient='horizontal').grid(column=0, row=1, columnspan=8, sticky='ew', pady=5)

    ttk.Label(scrollable_frame, text="Address", anchor="center").grid(column=0, row=2, padx=5, pady=5, sticky="ew")
    entry__reg_addr = ttk.Entry(scrollable_frame)
    entry__reg_addr.grid(column=1, row=2, padx=5, pady=5, sticky="nsew")
    entry__reg_addr.insert(0, "0x00")

    ttk.Label(scrollable_frame, text="Data", anchor="center").grid(column=2, row=2, padx=5, pady=5, sticky="ew")
    entry__reg_val = ttk.Entry(scrollable_frame)
    entry__reg_val.grid(column=3, row=2, padx=5, pady=5, sticky="nsew")
    entry__reg_val.insert(0, "0x00")

    ttk.Button(scrollable_frame, text="Register Write",
               command=lambda: write_register_manual(entry__reg_addr.get(), entry__reg_val.get())).grid(column=4, row=2,
                                                                                                        padx=5, pady=5,
                                                                                                        sticky="nsew")
    ttk.Button(scrollable_frame, text="Register Read",
               command=lambda: read_register_manual(entry__reg_addr.get(), entry__reg_val)).grid(column=5, row=2,
                                                                                                       padx=5, pady=5,
                                                                                                       sticky="nsew")

    ttk.Separator(scrollable_frame, orient='horizontal').grid(column=0, row=3, columnspan=8, sticky='ew', pady=5)

    with open('../regs/ORION_8G_12G_csr.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row

        prev_register_name = None
        entries = {}
        rw_attr = None
        field_name = None
        register_name = None
        entry = None

        for row_index, row in enumerate(reader):
            row_index = row_index + 3
            prev_rw_attr = rw_attr
            prev_field_name = field_name
            prev_register_name = register_name
            prev_entry = entry

            register_name = row[0]
            field_name = row[1]
            field_bits = row[2]
            reg_addr = int(row[3])
            rw_attr = row[4]

            ttk.Label(scrollable_frame, text=f'(0x{reg_addr:02X}) {register_name}',
                      font=('Consolas', 9)).grid(column=0, row=row_index + 1, padx=5, pady=5, sticky="w")
            ttk.Label(scrollable_frame, text=f'{f"[{field_bits}]":<7} {field_name}',
                      font=('Consolas', 9)).grid(column=1, row=row_index + 1, padx=5, pady=5, sticky="w")

            entry = ttk.Entry(scrollable_frame, state="normal" if rw_attr != 'r' else "readonly")
            if rw_attr == 'r':
                entry.configure(background="#f0f0f0")  # Set a lighter background color for read-only entries
            entry.grid(column=2, row=row_index + 1, padx=5, pady=5, sticky="nsew")
            entries[field_name] = entry
            field_reg_dict[field_name] = register_name

            if prev_register_name != register_name:
                if prev_register_name is not None:
                    # print(f'Adding buttons for {prev_register_name}')
                    write_button = ttk.Button(scrollable_frame, text="Write",
                                              command=lambda rn=prev_register_name, fn=prev_field_name: write_register(
                                                  entries, rn),
                                              state="normal")
                    write_button.grid(column=3, row=row_index, padx=5, pady=5, sticky="nsew")
                    read_button = ttk.Button(scrollable_frame, text="Read",
                                             command=lambda rn=prev_register_name, fn=prev_field_name,
                                                            attr=prev_rw_attr, e=prev_entry: read_register(entries, rn))
                    read_button.grid(column=4, row=row_index, padx=5, pady=5, sticky="nsew")
                prev_register_name = register_name
                # entries = {field_name: entry}
            else:
                pass
                # entries[field_name] = entry

            # Read the value from the device and update the entry
            if hasattr(orion, register_name):
                register = getattr(orion, register_name)
                # register.read()
                if hasattr(register, field_name):
                    value = getattr(register, field_name)
                    if (rw_attr == 'r'):
                        # print('readonly')
                        entry.config(state='normal')
                        entry.insert(0, hex(value))
                        entry.config(state='readonly')
                    else:
                        entry.insert(0, hex(value))
                    # print(f'entry_state_end = {entry_state}')

        # Add write and read buttons for the last register
        if register_name is not None:
            write_button = ttk.Button(scrollable_frame, text="Write",
                                      command=lambda rn=register_name, fn=field_name: write_register(entries, rn),
                                      state="normal")
            write_button.grid(column=3, row=row_index + 1, padx=5, pady=5, sticky="nsew")
            read_button = ttk.Button(scrollable_frame, text="Read",
                                     command=lambda rn=register_name, fn=field_name, attr=rw_attr,
                                                    e=entry: read_register(entries, rn))
            read_button.grid(column=4, row=row_index + 1, padx=5, pady=5, sticky="nsew")


# LUT file selection widgets, populated by display__tab_rf. Not wired into
# init_rf yet — GUI elements only for now.
lut_select = {}

# Pre-curated LUT sets: group name -> the six LUT files (keys tx_gain,
# tx_phase, rx_f1_gain, rx_f1_phase, rx_f2_gain, rx_f2_phase)
lut_groups = {
    # 'Example 9.5 GHz Low Bias': {
    #     'tx_gain': 'TX_Gain_LUT_10p5GHz.xlsx',
    #     'tx_phase': 'TX_Phase_LUT_10p5GHz.xlsx',
    #     'rx_f1_gain': 'RX_Gain_LUT_9GHz_LowBias.xlsx',
    #     'rx_f1_phase': 'RX_Phase_LUT_9GHz_LowBias.xlsx',
    #     'rx_f2_gain': 'RX_Gain_LUT_11GHz_LowBias.xlsx',
    #     'rx_f2_phase': 'RX_Phase_LUT_11GHz_LowBias.xlsx',
    # },
}


def select_lut_group(name):
    print(f'LUT Set: {name}')
    group = lut_groups.get(name)
    if group is None:
        return
    for key, fname in group.items():
        lut_select[key].set(fname)


def update_lut_select_state():
    default = lut_select['use_default'].get()
    use_set = lut_select['use_lut_set'].get()
    same = lut_select['same_rx_lut'].get()

    # Priority: default LUTs > LUT set > individual files
    lut_select['use_lut_set_chk'].config(state='disabled' if default else 'normal')
    lut_select['group'].config(state='readonly' if (use_set and not default) else 'disabled')
    individual = 'disabled' if (default or use_set) else 'readonly'
    lut_select['same_rx_lut_chk'].config(state='disabled' if (default or use_set) else 'normal')
    for key in ('tx_gain', 'tx_phase', 'rx_f1_gain', 'rx_f1_phase'):
        lut_select[key].config(state=individual)
    rx_f2_state = 'disabled' if (default or use_set or same) else 'readonly'
    lut_select['rx_f2_gain'].config(state=rx_f2_state)
    lut_select['rx_f2_phase'].config(state=rx_f2_state)


# Chip version selection: display name -> internal version tag
chip_versions = {'FD3R4411A': 'v1', 'FD3R4411B': 'v2', 'FD3RB0444': 'leo_v1'}
combobox__chip_version = None


def get_chip_version():
    return chip_versions[combobox__chip_version.get()]


def lut_file_matches_version(fname, version):
    f = fname.lower()
    if version == 'leo_v1':
        return 'leo_v1' in f
    # 'v1' must not match the 'v1' inside 'leo_v1'
    return version in f and 'leo' not in f


def update_lut_file_lists():
    version = get_chip_version()

    lut_files = []
    if os.path.isdir('../final_lut'):
        lut_files = sorted((f for f in os.listdir('../final_lut') if f.lower().endswith('.xlsx')), key=str.lower)
    else:
        print('final_lut folder not found, LUT selection lists are empty')

    # Offer only the files matching each cell (TX/RX, gain/phase) and the
    # selected chip version
    for key in ('tx_gain', 'tx_phase', 'rx_f1_gain', 'rx_f1_phase', 'rx_f2_gain', 'rx_f2_phase'):
        trx, kind = key.split('_')[0], key.split('_')[-1]
        values = [f for f in lut_files
                  if trx in f.lower() and kind in f.lower() and lut_file_matches_version(f, version)]
        cb = lut_select[key]
        cb.config(values=values)
        if cb.get() not in values:
            cb.set('')


def display__tab_rf():
    rf_en = []
    rf_chk = []
    rf_gain_entries = []
    rf_phase_entries = []
    pa_on_bias_entries = []
    pa_off_bias_entries = []
    lna_on_bias_entries = []
    lna_off_bias_entries = []
    ch_entry_lists = [rf_gain_entries, rf_phase_entries, pa_on_bias_entries, pa_off_bias_entries,
                      lna_on_bias_entries, lna_off_bias_entries]

    ttk.Label(tab_rf, text='Version').grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
    global combobox__chip_version
    combobox__chip_version = ttk.Combobox(tab_rf, values=list(chip_versions), state="readonly")
    combobox__chip_version.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
    combobox__chip_version.current(list(chip_versions).index('FD3R4411B'))
    combobox__chip_version.bind("<<ComboboxSelected>>", lambda event: update_lut_file_lists())

    ttk.Label(tab_rf, text='Bias Mode').grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
    combobox__bias_mode = ttk.Combobox(tab_rf, values=['Normal', 'Low Power'], state="readonly")
    combobox__bias_mode.grid(column=3, row=0, padx=5, pady=5, sticky="nsew")
    combobox__bias_mode.current(0)

    ttk.Label(tab_rf, text='TR Control Mode').grid(column=4, row=0, padx=5, pady=5, sticky="nsew")
    combobox__tr_mode = ttk.Combobox(tab_rf, values=['Register', 'TR Pin'], state="readonly")
    combobox__tr_mode.grid(column=5, row=0, padx=5, pady=5, sticky="nsew")
    combobox__tr_mode.current(0)
    combobox__tr_mode.bind("<<ComboboxSelected>>", lambda event: change_tr_mode(combobox__tr_mode.get()))
    ttk.Label(tab_rf, text='TRX Mode').grid(column=6, row=0, padx=5, pady=5, sticky="nsew")
    combobox__trx_mode = ttk.Combobox(tab_rf, values=['TX', 'RX'], state="readonly")
    combobox__trx_mode.grid(column=7, row=0, padx=5, pady=5, sticky="nsew")
    combobox__trx_mode.current(1)
    combobox__trx_mode.bind("<<ComboboxSelected>>",
                            lambda event: change_trx_mode(combobox__trx_mode.get(), rf_en, ch_entry_lists))

    ttk.Label(tab_rf, text='STG2 Load Config').grid(column=8, row=0, padx=5, pady=5, sticky="nsew")
    combobox__stg2_load_cfg = ttk.Combobox(tab_rf, values=['Register', 'Load Pin'], state="readonly")
    combobox__stg2_load_cfg.grid(column=9, row=0, padx=5, pady=5, sticky="nsew")
    combobox__stg2_load_cfg.current(0)
    combobox__stg2_load_cfg.bind("<<ComboboxSelected>>",
                                  lambda event: change_stg2_load_cfg(combobox__stg2_load_cfg.get()))

    ttk.Button(tab_rf, text="Initialize RF",
               command=lambda: init_rf(combobox__bias_mode.get(), combobox__tr_mode.get(), combobox__trx_mode.get(),
                                       combobox__stg2_load_cfg.get(), rf_en)).grid(column=0, row=1, padx=5, pady=5,
                                                                                   sticky="nsew")

    frame__lut = ttk.LabelFrame(tab_rf, text='LUT Selection')
    frame__lut.grid(column=1, row=1, columnspan=9, padx=5, pady=5, sticky="nsew")

    lut_select['use_default'] = tk.IntVar(value=1)
    ttk.Checkbutton(frame__lut, text="Use Default LUTs", variable=lut_select['use_default'],
                    command=update_lut_select_state).grid(column=0, row=0, columnspan=2, padx=5, pady=2, sticky="w")

    ttk.Label(frame__lut, text='LUT Set').grid(column=0, row=1, padx=5, pady=2, sticky="w")
    lut_select['group'] = ttk.Combobox(frame__lut, values=list(lut_groups), state="readonly", width=45)
    lut_select['group'].grid(column=1, row=1, padx=5, pady=2, sticky="nsew")
    lut_select['group'].bind("<<ComboboxSelected>>", lambda event: select_lut_group(lut_select['group'].get()))

    lut_select['use_lut_set'] = tk.IntVar(value=0)
    lut_select['use_lut_set_chk'] = ttk.Checkbutton(frame__lut, text="Use LUT Set",
                                                    variable=lut_select['use_lut_set'],
                                                    command=update_lut_select_state)
    lut_select['use_lut_set_chk'].grid(column=2, row=1, padx=5, pady=2, sticky="w")

    ttk.Label(frame__lut, text='Gain LUT').grid(column=1, row=2, padx=5, pady=2, sticky="w")
    ttk.Label(frame__lut, text='Phase LUT').grid(column=2, row=2, padx=5, pady=2, sticky="w")

    for r, (key, text) in enumerate([('tx', 'TX'), ('rx_f1', 'RX F1'), ('rx_f2', 'RX F2')], start=3):
        ttk.Label(frame__lut, text=text).grid(column=0, row=r, padx=5, pady=2, sticky="w")
        for c, kind in enumerate(['gain', 'phase'], start=1):
            cb = ttk.Combobox(frame__lut, values=[], state="readonly", width=45)
            cb.grid(column=c, row=r, padx=5, pady=2, sticky="nsew")
            lut_select[f'{key}_{kind}'] = cb

    lut_select['same_rx_lut'] = tk.IntVar(value=1)
    lut_select['same_rx_lut_chk'] = ttk.Checkbutton(frame__lut, text="Use same LUT for RX F1 and F2",
                                                    variable=lut_select['same_rx_lut'],
                                                    command=update_lut_select_state)
    lut_select['same_rx_lut_chk'].grid(column=1, row=6, padx=5, pady=2, sticky="w")

    frame__lut.grid_columnconfigure(1, weight=1)
    frame__lut.grid_columnconfigure(2, weight=1)
    update_lut_file_lists()
    update_lut_select_state()

    ttk.Separator(tab_rf, orient='horizontal').grid(column=0, row=2, columnspan=10, sticky='ew', pady=5)

    for i in range(4):
        rf_en.append(tk.IntVar(value=0))
        rf_chk.append(ttk.Checkbutton(tab_rf, text=f"CH{i} Enable", state="!selected", variable=rf_en[i],
                                      command=lambda: update_ch_en(combobox__trx_mode.get(), rf_en, ch_entry_lists)))
        rf_chk[i].grid(column=2 * i, row=3, padx=5, pady=5, sticky="w")

        rf_gain_entries.append(ttk.Entry(tab_rf, state="normal"))
        rf_gain_entries[i].insert(0, "0")
        rf_gain_entries[i].grid(column=2 * i + 1, row=4, padx=5, pady=5)
        ttk.Label(tab_rf, text=f"CH{i} Gain").grid(column=2 * i, row=4, padx=5, pady=5, sticky="w")

        rf_phase_entries.append(ttk.Entry(tab_rf, state="normal"))
        rf_phase_entries[i].grid(column=2 * i + 1, row=5, padx=5, pady=5)
        rf_phase_entries[i].insert(0, "0")
        ttk.Label(tab_rf, text=f"CH{i} Phase").grid(column=2 * i, row=5, padx=5, pady=5, sticky="w")

        ttk.Separator(tab_rf, orient='horizontal').grid(column=0, row=7, columnspan=10, sticky='ew', pady=5)

        ttk.Label(tab_rf, text=f"CH{i} PA ON Bias").grid(column=2 * i, row=8, padx=5, pady=5, sticky="w")
        pa_on_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        pa_on_bias_entries[i].insert(0, "100")
        pa_on_bias_entries[i].grid(column=2 * i + 1, row=8, padx=5, pady=5)

        ttk.Label(tab_rf, text=f"CH{i} PA OFF Bias").grid(column=2 * i, row=9, padx=5, pady=5, sticky="w")
        pa_off_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        pa_off_bias_entries[i].insert(0, "200")
        pa_off_bias_entries[i].grid(column=2 * i + 1, row=9, padx=5, pady=5)

        ttk.Label(tab_rf, text=f"CH{i} LNA ON Bias").grid(column=2 * i, row=10, padx=5, pady=5, sticky="w")
        lna_on_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        lna_on_bias_entries[i].insert(0, "100")
        lna_on_bias_entries[i].grid(column=2 * i + 1, row=10, padx=5, pady=5)

        ttk.Label(tab_rf, text=f"CH{i} LNA OFF Bias").grid(column=2 * i, row=11, padx=5, pady=5, sticky="w")
        lna_off_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        lna_off_bias_entries[i].insert(0, "200")
        lna_off_bias_entries[i].grid(column=2 * i + 1, row=11, padx=5, pady=5)

    ttk.Button(tab_rf, text="Load RF",
               command=lambda: load_rf(rf_en, rf_gain_entries, rf_phase_entries, pa_on_bias_entries,
                                       pa_off_bias_entries, lna_on_bias_entries,
                                       lna_off_bias_entries)).grid(column=0, row=6, padx=5, pady=5, sticky="nsew")

    ttk.Button(tab_rf, text="Update Bias",
               command=lambda: update_bias(rf_en, pa_on_bias_entries, pa_off_bias_entries, lna_on_bias_entries,
                                           lna_off_bias_entries)).grid(column=0, row=12, padx=5, pady=5,
                                                                       sticky="nsew")

    update_ch_entry_state(rf_en, ch_entry_lists)
    tab_rf.after(100, lambda: remove_chkbox_selection(rf_chk))

def change_sweep_mode(mode, trx_mode, channel, entry__sweep_phase, entry__sweep_gain, verbose=True):
    if verbose:
        print(f'Sweep Mode: {mode}, TRX Mode = {trx_mode}, Channel = {channel}')
    if mode == 'Phase':
        entry__sweep_phase.config(state='disabled')
        entry__sweep_gain.config(state='normal')
    else:
        entry__sweep_phase.config(state='normal')
        entry__sweep_gain.config(state='disabled')


def read_vna_s21():
    s21m = np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
    s21p = np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)
    return s21m, s21p


def store_sweep_point(idx, s21m, s21p):
    sweep_data['idx'].append(idx)
    sweep_data['gain'].append(s21m)
    sweep_data['phase'].append(s21p)
    print(f'S21 Gain (mid) = {s21m[len(s21m) // 2]}, S21 Phase (mid) = {s21p[len(s21p) // 2]}')


def run_sweep(mode, trx_mode, channel, phase, gain):
    print(f'Run Sweep: Mode = {mode}, TRX Mode = {trx_mode}, Channel = {channel}, Phase = {phase}, Gain = {gain}')

    global orion_hal

    if orion_hal is None:
        print('Device not connected, connect first')
        return

    capture = instruments is not None and instruments.vna is not None
    if not capture:
        print('VNA not connected, sweeping without capture')

    if capture:
        instruments.vna.cfg_pwr(pwr=-20)
        instruments.vna.write(":OUTP ON")

    if trx_mode == 'TX':
        orion_hal.set_trx_mode(1)
    else:
        orion_hal.set_trx_mode(0)

    ch_en = 1<<int(channel)
    print(ch_en)
    orion_hal.set_tr_mask(rx_mask=ch_en, tx_mask=ch_en)

    if capture:
        sweep_data['mode'] = mode
        sweep_data['trx_mode'] = trx_mode
        sweep_data['channel'] = channel
        sweep_data['idx'] = []
        sweep_data['gain'] = []
        sweep_data['phase'] = []

    if mode=='Phase':
        g_idx = round(int(gain)/0.5)
        p_idxs = range(4,125)
        for i, p_idx in enumerate(p_idxs):
            print(f'p_idx = {p_idx}')
            orion_hal.set_lut_idx(p_idx, g_idx, ch_en)
            orion_hal.set_lut_idx(p_idx, g_idx, ch_en << 1)
            orion_hal.stg2_load()
            time.sleep(0.5)
            if capture:
                s21m, s21p = read_vna_s21()
                store_sweep_point(p_idx, s21m, s21p)
            update_sweep_progress((i + 1) / len(p_idxs) * 100)
    else:
        if trx_mode=='TX':
            p_idx = round(int(phase)/2.8125)
        else:
            p_idx = round(int(phase)/2.975) + 4
        g_idxs = range(0,64)
        for i, g_idx in enumerate(g_idxs):
            print(f'g_idx = {g_idx}')
            orion_hal.set_lut_idx(p_idx, g_idx, ch_en)
            orion_hal.set_lut_idx(p_idx, g_idx, ch_en << 1)
            orion_hal.stg2_load()
            time.sleep(0.5)
            if capture:
                s21m, s21p = read_vna_s21()
                store_sweep_point(g_idx, s21m, s21p)
            update_sweep_progress((i + 1) / len(g_idxs) * 100)

    if capture:
        instruments.vna.cfg_pwr(pwr=-60)
        instruments.vna.write(":OUTP OFF")


# Run the sweep on a worker thread so the Tk event loop keeps servicing the
# window; the Run button is disabled until the sweep finishes.
sweep_thread = None


def update_sweep_progress(pct):
    # Called from the sweep worker thread, so hand the widget update to the
    # Tk main loop
    root.after(0, lambda: progressbar__sweep.config(value=pct))


def start_sweep(mode, trx_mode, channel, phase, gain):
    global sweep_thread

    if sweep_thread is not None and sweep_thread.is_alive():
        print('Sweep already in progress')
        return

    button__sweep_run.config(state='disabled')
    progressbar__sweep.config(value=0)

    def worker():
        try:
            run_sweep(mode, trx_mode, channel, phase, gain)
        finally:
            root.after(0, lambda: button__sweep_run.config(state='normal'))

    sweep_thread = threading.Thread(target=worker, daemon=True)
    sweep_thread.start()


def get_sweep_traces():
    # Gain/phase traces (sweep steps x frequencies), referenced to the first
    # sweep step, phase wrapped into +/-180
    gain = np.array(sweep_data['gain'])
    phase = np.array(sweep_data['phase'])
    gain = gain - gain[0]
    phase = (phase - phase[0] + 180) % 360 - 180
    return gain, phase


def get_sweep_errors():
    # Error = measured delta vs the ideal LUT step response.
    # Phase LSB matches the idx conversion in run_sweep; gain LSB is -0.5 dB
    # per index (target_gain_dB = -g_idx * 0.5 in the HAL).
    gain, phase = get_sweep_traces()
    idx = np.array(sweep_data['idx'])

    if sweep_data['mode'] == 'Phase':
        phase_lsb = 2.8125 if sweep_data['trx_mode'] == 'TX' else 2.975
        phase_ideal = (idx - idx[0]) * phase_lsb
        gain_ideal = np.zeros_like(idx, dtype=float)
    else:
        phase_ideal = np.zeros_like(idx, dtype=float)
        gain_ideal = -(idx - idx[0]) * 0.5

    gain_err = gain - gain_ideal[:, None]
    phase_err = (phase - phase_ideal[:, None] + 180) % 360 - 180

    # Reference the errors to the per-frequency mean rather than the first
    # sweep step, so an offset at the first point doesn't bias the stats
    gain_err = gain_err - np.mean(gain_err, axis=0)
    phase_err = phase_err - np.mean(phase_err, axis=0)
    return gain_err, phase_err


def show_sweep_figure(fig):
    for child in frame__sweep_plot.winfo_children():
        child.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame__sweep_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)


def sweep_plot_ready():
    if not sweep_data['idx']:
        print('No sweep data available, run a sweep first')
        return False
    return True


def sweep_title():
    return f"{sweep_data['mode']} Sweep: {sweep_data['trx_mode']} CH{sweep_data['channel']}"


def sweep_x_label():
    return f"{sweep_data['mode']} LUT Index"


def plot_sweep(freq_mhz):
    print(f'Plot Sweep: Frequency = {freq_mhz} MHz')

    if not sweep_plot_ready():
        return

    freqs_mhz = np.arange(vna_freq_start, vna_freq_stop + vna_freq_step, vna_freq_step) / 1e6
    freq_idx = int(np.argmin(np.abs(freqs_mhz - float(freq_mhz))))

    gain, phase = get_sweep_traces()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax_g = fig.add_subplot(211)
    ax_p = fig.add_subplot(212, sharex=ax_g)

    ax_g.plot(sweep_data['idx'], gain[:, freq_idx], marker='.')
    ax_g.set_ylabel('Gain (dB)')
    if sweep_data['mode'] == 'Gain':
        ax_g.set_ylim(-32, 0)
    ax_g.grid(True)
    ax_g.set_title(f"{sweep_title()} @ {freqs_mhz[freq_idx]:g} MHz")

    ax_p.plot(sweep_data['idx'], phase[:, freq_idx], marker='.', color='tab:orange')
    ax_p.set_ylabel('Phase (deg)')
    if sweep_data['mode'] == 'Phase':
        ax_p.set_ylim(-200, 200)
    ax_p.set_xlabel(sweep_x_label())
    ax_p.grid(True)

    fig.tight_layout()
    show_sweep_figure(fig)


def plot_sweep_errors(freq_mhz):
    print(f'Plot Sweep Errors: Frequency = {freq_mhz} MHz')

    if not sweep_plot_ready():
        return

    freqs_mhz = np.arange(vna_freq_start, vna_freq_stop + vna_freq_step, vna_freq_step) / 1e6
    freq_idx = int(np.argmin(np.abs(freqs_mhz - float(freq_mhz))))

    gain_err, phase_err = get_sweep_errors()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax_g = fig.add_subplot(211)
    ax_p = fig.add_subplot(212, sharex=ax_g)

    ax_g.plot(sweep_data['idx'], gain_err[:, freq_idx], marker='.')
    ax_g.set_ylabel('Gain Error (dB)')
    ax_g.grid(True)
    ax_g.set_title(f"{sweep_title()} Errors @ {freqs_mhz[freq_idx]:g} MHz")

    ax_p.plot(sweep_data['idx'], phase_err[:, freq_idx], marker='.', color='tab:orange')
    ax_p.set_ylabel('Phase Error (deg)')
    ax_p.set_xlabel(sweep_x_label())
    ax_p.grid(True)

    fig.tight_layout()
    show_sweep_figure(fig)


def plot_sweep_rms_errors(freq_mhz):
    print(f'Plot Sweep RMS Errors: Frequency = {freq_mhz} MHz')

    if not sweep_plot_ready():
        return

    freqs_mhz = np.arange(vna_freq_start, vna_freq_stop + vna_freq_step, vna_freq_step) / 1e6

    # Restrict the stats to a 1 GHz band centered on the chosen frequency
    band = np.abs(freqs_mhz - float(freq_mhz)) <= 500
    freqs_mhz = freqs_mhz[band]

    gain_err, phase_err = get_sweep_errors()
    gain_err = gain_err[:, band]
    phase_err = phase_err[:, band]

    # Per-frequency statistics across all sweep steps
    gain_peak = np.max(np.abs(gain_err), axis=0)
    gain_std = np.std(gain_err, axis=0)
    phase_peak = np.max(np.abs(phase_err), axis=0)
    phase_std = np.std(phase_err, axis=0)

    fig = Figure(figsize=(8, 5), dpi=100)
    ax_g = fig.add_subplot(211)
    ax_p = fig.add_subplot(212, sharex=ax_g)

    ax_g.plot(freqs_mhz, gain_peak, marker='.', label='Peak')
    ax_g.plot(freqs_mhz, gain_std, marker='.', label='Std Dev')
    ax_g.set_ylabel('Gain Error (dB)')
    ax_g.grid(True)
    ax_g.legend()
    ax_g.set_title(f"{sweep_title()} Error, 1 GHz band @ {float(freq_mhz):g} MHz")

    ax_p.plot(freqs_mhz, phase_peak, marker='.', label='Peak')
    ax_p.plot(freqs_mhz, phase_std, marker='.', label='Std Dev')
    ax_p.set_ylabel('Phase Error (deg)')
    ax_p.set_xlabel('Frequency (MHz)')
    ax_p.grid(True)
    ax_p.legend()

    fig.tight_layout()
    show_sweep_figure(fig)


def analyze_sweep(freq_mhz):
    print(f'Analyze Sweep: Frequency = {freq_mhz} MHz')

    if not sweep_plot_ready():
        return

    freqs_mhz = np.arange(vna_freq_start, vna_freq_stop + vna_freq_step, vna_freq_step) / 1e6
    gain_err, phase_err = get_sweep_errors()

    lines = []
    for f in (float(freq_mhz) - 500, float(freq_mhz), float(freq_mhz) + 500):
        if f < freqs_mhz[0] or f > freqs_mhz[-1]:
            continue
        fi = int(np.argmin(np.abs(freqs_mhz - f)))
        g_peak = np.max(np.abs(gain_err[:, fi]))
        g_std = np.std(gain_err[:, fi])
        p_peak = np.max(np.abs(phase_err[:, fi]))
        p_std = np.std(phase_err[:, fi])
        line = (f'{freqs_mhz[fi]:g} MHz: Gain Err peak = {g_peak:.2f} dB, std = {g_std:.2f} dB | '
                f'Phase Err peak = {p_peak:.2f} deg, std = {p_std:.2f} deg')
        print(line)
        lines.append(line)

    label__sweep_stats.config(text='\n'.join(lines))


def display__tab_sweep():
    ttk.Label(tab_sweep, text='Mode').grid(column=0, row=0, padx=5, pady=5, sticky="w")
    combobox__sweep_mode = ttk.Combobox(tab_sweep, values=['Phase', 'Gain'], state="readonly")
    combobox__sweep_mode.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
    combobox__sweep_mode.current(0)
    combobox__sweep_mode.bind("<<ComboboxSelected>>",
                              lambda event: change_sweep_mode(combobox__sweep_mode.get(), combobox__sweep_trx_mode.get(),
                                                              combobox__sweep_ch.get(), entry__sweep_phase,
                                                              entry__sweep_gain))

    ttk.Label(tab_sweep, text='TRX Mode').grid(column=2, row=0, padx=5, pady=5, sticky="w")
    combobox__sweep_trx_mode = ttk.Combobox(tab_sweep, values=['TX', 'RX'], state="readonly")
    combobox__sweep_trx_mode.grid(column=3, row=0, padx=5, pady=5, sticky="nsew")
    combobox__sweep_trx_mode.current(0)

    ttk.Label(tab_sweep, text='Channel').grid(column=4, row=0, padx=5, pady=5, sticky="w")
    combobox__sweep_ch = ttk.Combobox(tab_sweep, values=['0', '1', '2', '3'], state="readonly")
    combobox__sweep_ch.grid(column=5, row=0, padx=5, pady=5, sticky="nsew")
    combobox__sweep_ch.current(0)

    ttk.Label(tab_sweep, text='Phase').grid(column=0, row=1, padx=5, pady=5, sticky="w")
    entry__sweep_phase = ttk.Entry(tab_sweep)
    entry__sweep_phase.grid(column=1, row=1, padx=5, pady=5, sticky="nsew")
    entry__sweep_phase.insert(0, "0")

    ttk.Label(tab_sweep, text='Gain').grid(column=2, row=1, padx=5, pady=5, sticky="w")
    entry__sweep_gain = ttk.Entry(tab_sweep)
    entry__sweep_gain.grid(column=3, row=1, padx=5, pady=5, sticky="nsew")
    entry__sweep_gain.insert(0, "0")

    global progressbar__sweep
    progressbar__sweep = ttk.Progressbar(tab_sweep, orient='horizontal', mode='determinate', maximum=100)
    progressbar__sweep.grid(column=4, row=1, padx=5, pady=5, sticky="nsew")

    global button__sweep_run
    button__sweep_run = ttk.Button(tab_sweep, text="Run",
                                   command=lambda: start_sweep(combobox__sweep_mode.get(),
                                                               combobox__sweep_trx_mode.get(),
                                                               combobox__sweep_ch.get(), entry__sweep_phase.get(),
                                                               entry__sweep_gain.get()))
    button__sweep_run.grid(column=5, row=1, padx=5, pady=5, sticky="nsew")

    ttk.Separator(tab_sweep, orient='horizontal').grid(column=0, row=2, columnspan=6, sticky='ew', pady=5)

    ttk.Label(tab_sweep, text='Frequency (MHz)').grid(column=0, row=3, padx=5, pady=5, sticky="w")
    freqs_mhz = [f'{f / 1e6:g}' for f in np.arange(vna_freq_start, vna_freq_stop + vna_freq_step, vna_freq_step)]
    combobox__sweep_freq = ttk.Combobox(tab_sweep, values=freqs_mhz, state="readonly")
    combobox__sweep_freq.grid(column=1, row=3, padx=5, pady=5, sticky="nsew")
    combobox__sweep_freq.current(len(freqs_mhz) // 2)

    ttk.Button(tab_sweep, text="Plot",
               command=lambda: plot_sweep(combobox__sweep_freq.get())).grid(column=2, row=3, padx=5, pady=5,
                                                                            sticky="nsew")
    ttk.Button(tab_sweep, text="Plot Errors",
               command=lambda: plot_sweep_errors(combobox__sweep_freq.get())).grid(column=3, row=3, padx=5, pady=5,
                                                                                   sticky="nsew")
    ttk.Button(tab_sweep, text="Plot RMS Errors",
               command=lambda: plot_sweep_rms_errors(combobox__sweep_freq.get())).grid(column=4, row=3, padx=5,
                                                                                       pady=5, sticky="nsew")
    ttk.Button(tab_sweep, text="Analyze",
               command=lambda: analyze_sweep(combobox__sweep_freq.get())).grid(column=5, row=3, padx=5, pady=5,
                                                                               sticky="nsew")

    # Stats readout above the plot container
    global label__sweep_stats
    label__sweep_stats = ttk.Label(tab_sweep, text='Stats: -')
    label__sweep_stats.grid(column=0, row=4, columnspan=6, padx=5, pady=5, sticky="w")

    # Placeholder container for the sweep plot
    global frame__sweep_plot
    frame__sweep_plot = ttk.Frame(tab_sweep, relief='groove', borderwidth=1)
    frame__sweep_plot.grid(column=0, row=5, columnspan=6, padx=5, pady=10, sticky="nsew")
    tab_sweep.grid_rowconfigure(5, weight=1)
    for col in range(6):
        tab_sweep.grid_columnconfigure(col, weight=1)

    change_sweep_mode(combobox__sweep_mode.get(), combobox__sweep_trx_mode.get(), combobox__sweep_ch.get(),
                      entry__sweep_phase, entry__sweep_gain, verbose=False)


def display__tab_misc():
    osc_en = tk.IntVar(value=0)
    chk__osc_en = (ttk.Checkbutton(tab_misc, text="Oscillator Enable", variable=osc_en,
                                   command=lambda: adc_setup(osc_en.get(), combobox__adc_sel.get())))
    chk__osc_en.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

    ttk.Label(tab_misc, text="ADC Input Select").grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
    combobox__adc_sel = ttk.Combobox(tab_misc, values=['DET0', 'DET1', 'DET2', 'DET3', 'TEMP', 'GP4', 'GP5', 'GP6',
                                                       'GP7'], state="readonly")
    combobox__adc_sel.grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
    combobox__adc_sel.current(8)
    combobox__adc_sel.bind("<<ComboboxSelected>>", lambda event: adc_setup(osc_en.get(), combobox__adc_sel.get()))

    ttk.Button(tab_misc, text="ADC Read", command=lambda: adc_read(entry__adc_val)).grid(column=3, row=0, padx=5,
                                                                                         pady=5, sticky="nsew")
    entry__adc_val = ttk.Entry(tab_misc, state='normal')
    entry__adc_val.grid(column=4, row=0, padx=5, pady=5, sticky="nsew")
    entry__adc_val.insert(0, "0x00")
    entry__adc_val.config(state='readonly')

    tab_misc.after(100, lambda: chk__osc_en.state(['!alternate', '!selected']))


def display__tab_scripts():
    def update_script_listbox(*args):
        # print(f'Update Script Listbox {args}')
        # print(f'{search_entry.get()}')
        script_listbox.delete(0, tk.END)
        for item in options:
            # print(item)
            if search_entry.get().lower() in item.lower():
                script_listbox.insert(tk.END, item)
            else:
                pass

    global script_dir
    options = [file for file in os.listdir(script_dir) if file.endswith('.py')]

    ttk.Label(tab_scripts, text="Choose a Script and click RUN").grid(column=0, row=0, padx=10, pady=5, sticky="nsew")

    search_entry = ttk.Entry(tab_scripts, width=50)
    search_entry.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")
    search_entry.bind("<KeyRelease>", update_script_listbox)

    ttk.Button(tab_scripts, text='Run',
               command=lambda: run_script(script_listbox.get(script_listbox.curselection()))).grid(column=1, row=1,
                                                                                                   padx=5, pady=5,
                                                                                                   sticky="nsew")

    script_listbox = tk.Listbox(tab_scripts, height=30, width=30)
    scrollbar = ttk.Scrollbar(tab_scripts, orient="vertical", command=script_listbox.yview)
    script_listbox.config(yscrollcommand=scrollbar.set)
    script_listbox.grid(column=0, row=2, padx=10, pady=5, sticky="nsew")
    scrollbar.grid(column=1, row=2, padx=0, pady=5, sticky="ns")
    # script_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    for script in options:
        script_listbox.insert(tk.END, script)


def remove_chkbox_selection(chk):
    for i in range(4):
        chk[i].state(['!alternate', '!selected'])


# Main - START
script_dir = '../tests'

status['Status'] = 'Disconnected'
status['RF'] = 'Not Initialized'

# Give the process its own taskbar identity so Windows shows the window icon
# instead of the python.exe icon
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('FermionIC.FD3R4411.ControlSoftware')

root = tk.Tk()
root.title("FD3R4411 Control Software @ FermionIC Design Pvt Ltd")
root.geometry('1376x1008')

window_icon = tk.PhotoImage(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Favicon Logo.png'))
root.iconphoto(True, window_icon)

# Tab - START
style = ttk.Style()
style.configure("TNotebook.Tab", padding=[10, 5])
tabControl = ttk.Notebook(root, style='TNotebook')

tab_setup = ttk.Frame(tabControl)
tab_rf = ttk.Frame(tabControl)
tab_sweep = ttk.Frame(tabControl)
tab_misc = ttk.Frame(tabControl)
tab_registers = ttk.Frame(tabControl)
tab_scripts = ttk.Frame(tabControl)

tabControl.add(tab_setup, text='Setup')
tabControl.add(tab_rf, text='RF Control')
tabControl.add(tab_sweep, text='Phase/Gain Sweep')
tabControl.add(tab_misc, text='Misc Control')
tabControl.add(tab_registers, text='Registers')
tabControl.add(tab_scripts, text='Scripts')

tabControl.pack(expand=1, fill="both")
tabControl.select(tab_setup)

display__tab_setup()
display__tab_rf()
display__tab_sweep()
display__tab_registers()
display__tab_misc()
display__tab_scripts()
# Tab - END

status_bar_text = ''
for i in status.items():
    # print(f'{i[0]}: {i[1]}')
    status_bar_text += f'{i[0]}: {i[1]}\t'
status_bar = ttk.Label(root, text=status_bar_text, relief="sunken", anchor="w", padding=(10, 5))
status_bar.pack(side="bottom", fill="x")

# while(1) loop
root.mainloop()

# Main - END

