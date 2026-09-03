import sys
import time
import csv
sys.path.append('../include')
from ORION_8G_12G import *
from SPI import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *

############### User Settings ##############################################
version = 'v2'
dev_addr = [0x00, 0x03]

rf_ch_list = {
    0x00: [0, 1, 2],
    0x03: [0, 1, 2]
}

bias_ch_list = {
    0x00: [0, 1, 2],
    0x03: [0, 1, 2]
}
cal_file = r"C:\Users\silic\OneDrive\Documents\GitHub\orion\demo\rci\Cal results\RX_LNA_DAC_Calibration_Log_20250814_111756.csv"
############## END: User Settings ##########################################  

spi = SPI()
orion_bdst = ORION_8G_12G(spi, 0, 1)
orion_lut_bdst = ORION_8G_12G_lut(spi, 0, 1)

devices = {f'orion_dev{i}': ORION_8G_12G(spi, addr, 0) for i, addr in enumerate(dev_addr)}
devices_lut = {f'orion_lut{i}': ORION_8G_12G_lut(spi, addr, 0) for i, addr in enumerate(dev_addr)}
hal_devs = {name: ORION_8G_12G_hal(dev, devices_lut[f'orion_lut{i}'], spi, version) for i, (name, dev) in enumerate(devices.items())}
hal_bdst = ORION_8G_12G_hal(orion_bdst, orion_lut_bdst, spi, version)

# === Load calibration data ===
cal_data = {}
try:
    with open(cal_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dev = row["Device"].strip()
            rx_ch = int(row["RX_Channel"])
            cal_data[(dev, rx_ch)] = {
                "dac_code": int(row["DAC_Code"]),
                "p_idx": int(row["P_Idx"]),
                "g_idx": int(row["G_Idx"])
            }
    print(f"Loaded calibration from: {cal_file}")
except FileNotFoundError:
    print(f"⚠️ No calibration file found at {cal_file}")

    
hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)
hal_bdst.init_lut_new(
    r'../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    r'../results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
    r'../results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
    r'../results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
    r'../results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
    r'../results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx'
)
hal_bdst.cfg_stg2_load('REG')
hal_bdst.set_tr_mode('EXT_TR')
hal_bdst.set_trx_mode(0)
hal_bdst.en_data_path(1)
hal_bdst.init_rx('LOW')
hal_bdst.set_freq('9G')
hal_bdst.enable_rx_correction(1)

for (name, hal), addr in zip(hal_devs.items(), dev_addr):
    rx_channels = rf_ch_list[addr]
    lna_channels = bias_ch_list[addr]
    lna_keys = [f'LNA{ch}' for ch in lna_channels]
    rx_mask = sum(1 << ch for ch in rx_channels)
    hal.set_tr_mask(rx_mask=rx_mask)
    print(f"Device: {name} (ADDR: {hex(addr)})")
    for rx_ch, lna_key in zip(rx_channels, lna_keys):
        # hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)
        rx_en = 1 << rx_ch 
        initial_vals = cal_data[(name, rx_ch)]
        base_p_idx = initial_vals["p_idx"]
        base_g_idx = initial_vals["g_idx"]
        dac_code = initial_vals["dac_code"]
        hal.set_lut_idx(p_idx=base_p_idx, g_idx=base_g_idx, ant_sel=rx_en)
        hal.stg2_load()
        hal.dac_cfg(pa_sel=0, lna_sel=rx_en, **{lna_key: dac_code})
        print(f"✅ {name} - RX{rx_ch} / {lna_key}: DAC={dac_code}, "
              f"P_Idx={base_p_idx}, G_Idx={base_g_idx}")
input("Check the calibrated gain, phase of all device, all channels at this point..")

prev_p_delta = [
    [0, 0, 0],
    [0, 0, 0]
]
prev_g_delta = [
    [0, 0, 0],
    [0, 0, 0]
]          
# === Get deltas for each device and channel from user===
while True:
    delta_p = []
    delta_g = []
    
    for dev_idx, addr in enumerate(dev_addr):
        ch_count = len(rf_ch_list[addr])
        while True:
            try:
                raw_p = input(f"Enter p_idx deltas for Device {dev_idx} (space separated for {ch_count} channels): ")
                p_list = list(map(int, raw_p.strip().split()))
                if len(p_list) != ch_count:
                    raise ValueError(f"Expected {ch_count} values.")
                
                raw_g = input(f"Enter g_idx deltas for Device {dev_idx} (space separated for {ch_count} channels): ")
                g_list = list(map(int, raw_g.strip().split()))
                if len(g_list) != ch_count:
                    raise ValueError(f"Expected {ch_count} values.")
                
                delta_p.append(p_list)
                delta_g.append(g_list)
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.")  
            
    for dev_idx, ((name, hal), addr) in enumerate(zip(hal_devs.items(), dev_addr)):
        rx_channels = rf_ch_list[addr]
        lna_channels = bias_ch_list[addr]
        lna_keys = [f'LNA{ch}' for ch in lna_channels]
        print(f"Device: {name} (ADDR: {hex(addr)})")
        for ch_idx, (rx_ch, lna_key) in enumerate(zip(rx_channels, lna_keys)):
            rx_en = 1 << rx_ch            
            initial_vals = cal_data[(name, rx_ch)]
            base_p_idx = initial_vals["p_idx"]
            base_g_idx = initial_vals["g_idx"]
            dac = initial_vals["dac_code"]
            delta_p[dev_idx][ch_idx] = delta_p[dev_idx][ch_idx] + prev_p_delta[dev_idx][ch_idx]
            delta_g[dev_idx][ch_idx] = delta_g[dev_idx][ch_idx] + prev_g_delta[dev_idx][ch_idx]
             # Apply delta for this device & channel
            p_idx = base_p_idx + delta_p[dev_idx][ch_idx]
            g_idx = base_g_idx + delta_g[dev_idx][ch_idx]
    
            # Wrap/limit values as per your original constraints
            if p_idx < 4:
                p_idx = base_p_idx
            if p_idx >= 125:
                offset = p_idx-125
                p_idx = 4 + offset
            if g_idx > 63:
                g_idx = 63
            if g_idx <= 0:
                g_idx = base_g_idx
            # Apply settings
            hal.set_lut_idx(p_idx=p_idx, g_idx=g_idx, ant_sel=rx_en)
            hal.stg2_load()
            prev_p_delta[dev_idx][ch_idx] = delta_p[dev_idx][ch_idx]
            prev_g_delta[dev_idx][ch_idx] = delta_g[dev_idx][ch_idx]
            print(f"✅ {name} - RX{rx_ch} / {lna_key}: DAC={dac}, "
                  f"P_Idx={p_idx}, G_Idx={g_idx}")
            input("Check the new gain, phase at this point and press enter to see other channel")
              
    # Ask user if they want to repeat with new deltas or exit
    cont = input("Do you want to enter another set of delta values? (y/n): ").strip().lower()
    if cont != 'y':
        break
    
# Clean-up
hal_bdst.en_data_path(0)
hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)
spi.close()