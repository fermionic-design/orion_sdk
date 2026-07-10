import sys

# from include.ORION_8G_12G import ORION_8G_12G
# from include.ORION_8G_12G_lut import ORION_8G_12G_lut

sys.path.append('../include')

import os
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

spi = None
orion = None
orion_lut = None
orion_hal = None

status = {}


def update_status_bar():
    global status_bar
    status_bar_text = ''
    for i in status.items():
        # print(f'{i[0]}: {i[1]}')
        status_bar_text += f'{i[0]}: {i[1]}\t'
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

    if trx_mode == 'TX':
        print(f'Enable TX: {bin(ch_en)}')
        orion_hal.enable_tx(ch_en)
    else:
        print(f'Enable RX: {bin(ch_en)}')
        orion_hal.enable_rx(ch_en)

    # TEMP
    if tr_mode == 'Register':
        orion_hal.set_tr_mode('INT_TR')
    else:
        orion_hal.set_tr_mode('EXT_TR')

    if trx_mode == 'TX':
        orion_hal.set_trx_mode(1)
    else:
        orion_hal.set_trx_mode(0)

    orion_hal.set_tr_mask(rx_mask=0x1)
    orion_hal.cfg_stg2_load('REG' if stg2_load_cfg == 'Register' else 'PIN')
    orion_hal.enable_rx_correction(1)
    orion_hal.en_data_path(1)

    status['RF'] = f'Initialized @ {bias_mode}'
    update_status_bar()


def change_tr_mode(tr_mode):
    print(f'TR Control Mode: {tr_mode}')
    if tr_mode=='Register':
        orion_hal.set_tr_mode('INT_TR')
    else:
        orion_hal.set_tr_mode('EXT_TR')


def change_trx_mode(trx_mode):
    print(f'TRX Mode: {trx_mode}')
    if trx_mode=='RX':
        orion_hal.set_trx_mode(0)
    else:
        orion_hal.set_trx_mode(1)


def change_stg2_load_cfg(stg2_load_cfg):
    print(f'STG2 Load Cfg: {stg2_load_cfg}')
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
            # orion_hal.set_lut_idx(round(float(rf_phase_entries[i].get()) / 2.975) + 4,
            #                       round((float(rf_gain_entries[i].get())) / 0.5), ant_sel)
            orion_hal.set_lut_idx(round(int(rf_phase_entries[0].get()) / 2.975) + 4,
                                  round(int(rf_gain_entries[0].get()) / 0.5), ant_sel)
            orion_hal.set_lut_idx(round(int(rf_phase_entries[0].get()) / 2.975) + 4,
                                  round(int(rf_gain_entries[0].get()) / 0.5), ant_sel<<1)
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


def read_register_manual(addr, val):
    # print(f'Read Register Manual: {addr}, {val}')
    global spi
    spi.read(int(addr, 16))


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
               command=lambda: read_register_manual(entry__reg_addr.get(), entry__reg_val.get())).grid(column=5, row=2,
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
            rw_attr = row[4]

            ttk.Label(scrollable_frame, text=register_name).grid(column=0, row=row_index + 1, padx=5, pady=5,
                                                                 sticky="nsew")
            ttk.Label(scrollable_frame, text=field_name).grid(column=1, row=row_index + 1, padx=5, pady=5,
                                                              sticky="nsew")

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


def display__tab_rf():
    rf_en = []
    rf_chk = []
    rf_gain_entries = []
    rf_phase_entries = []
    pa_on_bias_entries = []
    pa_off_bias_entries = []
    lna_on_bias_entries = []
    lna_off_bias_entries = []

    ttk.Label(tab_rf, text='Bias Mode').grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
    combobox__bias_mode = ttk.Combobox(tab_rf, values=['Normal', 'Low Power'], state="readonly")
    combobox__bias_mode.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
    combobox__bias_mode.current(0)

    ttk.Label(tab_rf, text='TR Control Mode').grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
    combobox__tr_mode = ttk.Combobox(tab_rf, values=['Register', 'TR Pin'], state="readonly")
    combobox__tr_mode.grid(column=3, row=0, padx=5, pady=5, sticky="nsew")
    combobox__tr_mode.current(0)
    combobox__tr_mode.bind("<<ComboboxSelected>>", lambda event: change_tr_mode(combobox__tr_mode.get()))
    ttk.Label(tab_rf, text='TRX Mode').grid(column=4, row=0, padx=5, pady=5, sticky="nsew")
    combobox__trx_mode = ttk.Combobox(tab_rf, values=['TX', 'RX'], state="readonly")
    combobox__trx_mode.grid(column=5, row=0, padx=5, pady=5, sticky="nsew")
    combobox__trx_mode.current(1)
    combobox__trx_mode.bind("<<ComboboxSelected>>", lambda event: change_trx_mode(combobox__trx_mode.get()))

    ttk.Label(tab_rf, text='STG2 Load Config').grid(column=6, row=0, padx=5, pady=5, sticky="nsew")
    combobox__stg2_load_cfg = ttk.Combobox(tab_rf, values=['Register', 'Load Pin'], state="readonly")
    combobox__stg2_load_cfg.grid(column=7, row=0, padx=5, pady=5, sticky="nsew")
    combobox__stg2_load_cfg.current(0)
    combobox__stg2_load_cfg.bind("<<ComboboxSelected>>",
                                  lambda event: change_stg2_load_cfg(combobox__stg2_load_cfg.get()))

    ttk.Button(tab_rf, text="Initialize RF",
               command=lambda: init_rf(combobox__bias_mode.get(), combobox__tr_mode.get(), combobox__trx_mode.get(),
                                       combobox__stg2_load_cfg.get(), rf_en)).grid(column=8, row=0, padx=5, pady=5,
                                                                                   sticky="nsew")

    ttk.Separator(tab_rf, orient='horizontal').grid(column=0, row=1, columnspan=8, sticky='ew', pady=5)

    for i in range(4):
        rf_en.append(tk.IntVar(value=0))
        rf_chk.append(ttk.Checkbutton(tab_rf, text=f"CH{i} Enable", state="!selected", variable=rf_en[i]))
        rf_chk[i].grid(column=2 * i, row=2, padx=5, pady=5, sticky="w")

        rf_gain_entries.append(ttk.Entry(tab_rf, state="normal"))
        rf_gain_entries[i].insert(0, "0")
        rf_gain_entries[i].grid(column=2 * i + 1, row=3, padx=5, pady=5)
        ttk.Label(tab_rf, text=f"CH{i} Gain").grid(column=2 * i, row=3, padx=5, pady=5, sticky="w")

        rf_phase_entries.append(ttk.Entry(tab_rf, state="normal"))
        rf_phase_entries[i].grid(column=2 * i + 1, row=4, padx=5, pady=5)
        rf_phase_entries[i].insert(0, "0")
        ttk.Label(tab_rf, text=f"CH{i} Phase").grid(column=2 * i, row=4, padx=5, pady=5, sticky="w")

        ttk.Separator(tab_rf, orient='horizontal').grid(column=0, row=6, columnspan=8, sticky='ew', pady=5)

        ttk.Label(tab_rf, text=f"CH{i} PA ON Bias").grid(column=2 * i, row=7, padx=5, pady=5, sticky="w")
        pa_on_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        pa_on_bias_entries[i].insert(0, "100")
        pa_on_bias_entries[i].grid(column=2 * i + 1, row=7, padx=5, pady=5)

        ttk.Label(tab_rf, text=f"CH{i} PA OFF Bias").grid(column=2 * i, row=8, padx=5, pady=5, sticky="w")
        pa_off_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        pa_off_bias_entries[i].insert(0, "200")
        pa_off_bias_entries[i].grid(column=2 * i + 1, row=8, padx=5, pady=5)

        ttk.Label(tab_rf, text=f"CH{i} LNA ON Bias").grid(column=2 * i, row=9, padx=5, pady=5, sticky="w")
        lna_on_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        lna_on_bias_entries[i].insert(0, "100")
        lna_on_bias_entries[i].grid(column=2 * i + 1, row=9, padx=5, pady=5)

        ttk.Label(tab_rf, text=f"CH{i} LNA OFF Bias").grid(column=2 * i, row=10, padx=5, pady=5, sticky="w")
        lna_off_bias_entries.append(ttk.Entry(tab_rf, state="normal"))
        lna_off_bias_entries[i].insert(0, "200")
        lna_off_bias_entries[i].grid(column=2 * i + 1, row=10, padx=5, pady=5)

    ttk.Button(tab_rf, text="Load RF",
               command=lambda: load_rf(rf_en, rf_gain_entries, rf_phase_entries, pa_on_bias_entries,
                                       pa_off_bias_entries, lna_on_bias_entries,
                                       lna_off_bias_entries)).grid(column=0, row=5, padx=5, pady=5, sticky="nsew")

    ttk.Button(tab_rf, text="Update Bias",
               command=lambda: update_bias(rf_en, pa_on_bias_entries, pa_off_bias_entries, lna_on_bias_entries,
                                           lna_off_bias_entries)).grid(column=0, row=11, padx=5, pady=5,
                                                                       sticky="nsew")

    tab_rf.after(100, lambda: remove_chkbox_selection(rf_chk))

def display__tab_misc():
    osc_en = tk.IntVar(value=0)
    chk__osc_en = (ttk.Checkbutton(tab_misc, text="Oscillator Enable", variable=osc_en,
                                   command=lambda: adc_setup(osc_en.get(), combobox__adc_sel.get())))
    chk__osc_en.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

    ttk.Label(tab_misc, text="ADC Input Select").grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
    combobox__adc_sel = ttk.Combobox(tab_misc, values=['DET0', 'DET1', 'DET2', 'DET3', 'TEMP', 'GP7'], state="readonly")
    combobox__adc_sel.grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
    combobox__adc_sel.current(5)
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

root = tk.Tk()
root.title("FD3R4411 Control Software @ FermionIC Design Pvt Ltd")
root.geometry('1300x800')

# Tab - START
style = ttk.Style()
style.configure("TNotebook.Tab", padding=[10, 5])
tabControl = ttk.Notebook(root, style='TNotebook')

tab_setup = ttk.Frame(tabControl)
tab_rf = ttk.Frame(tabControl)
tab_misc = ttk.Frame(tabControl)
tab_registers = ttk.Frame(tabControl)
tab_scripts = ttk.Frame(tabControl)

tabControl.add(tab_setup, text='Setup')
tabControl.add(tab_rf, text='RF Control')
tabControl.add(tab_misc, text='Misc Control')
tabControl.add(tab_registers, text='Registers')
tabControl.add(tab_scripts, text='Scripts')

tabControl.pack(expand=1, fill="both")
tabControl.select(tab_setup)

display__tab_setup()
display__tab_rf()
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

