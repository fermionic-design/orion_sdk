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
dev_addr = [0x00,0x01]

rf_ch_list = {
    0x00: [0, 1, 2, 3],
    0x01: [0, 1, 2, 3],
    # 0x02: [0,3],
    # 0x03: [1,0,3]
}

bias_ch_list = {
    0x00: [0, 1, 2, 3],
    0X01: [0, 1, 2, 3],
    # 0x02: [0,3],
    # 0x03: [1,0,3]
}

lna_current = 60
initial_dac_code = 25
############## END: User Settings ##########################################

spi = SPI()
orion_bdst = ORION_8G_12G(spi, 0, 1)
orion_lut_bdst = ORION_8G_12G_lut(spi, 0, 1)

devices = {f'orion_dev{i}': ORION_8G_12G(spi, addr, 0) for i, addr in enumerate(dev_addr)}
devices_lut = {f'orion_lut{i}': ORION_8G_12G_lut(spi, addr, 0) for i, addr in enumerate(dev_addr)}
hal_devs = {name: ORION_8G_12G_hal(dev, devices_lut[f'orion_lut{i}'], spi,version) for i, (name, dev) in enumerate(devices.items())}
hal_bdst = ORION_8G_12G_hal(orion_bdst, orion_lut_bdst, spi,version)

# Broadcast init
hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)
hal_bdst.init_lut_new(
    r'../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
    r'../results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
    r'../results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
    r'../results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
    r'../results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
    r'../results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

hal_bdst.cfg_stg2_load('REG')
hal_bdst.set_tr_mode('EXT_TR')
hal_bdst.set_trx_mode(0)
hal_bdst.init_rx('NOM')
hal_bdst.set_freq('11G')
hal_bdst.enable_rx_correction(1)
hal_bdst.en_data_path(1)
for (name,hal), addr in zip(hal_devs.items(), dev_addr):
    rx_channels = rf_ch_list[addr]
    rx_mask = sum(1 << ch for ch in rx_channels)
    hal.set_tr_mask(rx_mask=rx_mask)
    hal.stg2_load()    

# -------- PHASE 1: LNA DAC Calibration, default setting gain,phase from VNA (ALL channels first) --------
dac_map = {}
for (name, hal), addr in zip(hal_devs.items(), dev_addr):
    hal.set_trx_mode(0)
    rx_channels = rf_ch_list[addr]
    lna_channels = bias_ch_list[addr]
    lna_keys = [f'LNA{ch}' for ch in lna_channels]
    print(f"🔧 Device: {name} (ADDR: {hex(addr)})")
    
    for rx_ch, lna_key in zip(rx_channels, lna_keys):
        hal_bdst.set_tr_mask(rx_mask=0x00)
        rx_en = 1 << rx_ch
        p_idx = 4
        g_idx = 0
        hal_bdst.dac_cfg(pa_sel=0xF, lna_sel = 0xF)
        hal_bdst.set_iq_val(Av=0, ant_sel=0xF)
        hal.set_tr_mask(rx_mask=rx_en)
        hal.set_lut_idx(p_idx=p_idx, g_idx=g_idx, ant_sel=rx_en)
        hal.stg2_load()

        dac_code = initial_dac_code

        while True:
            hal.dac_cfg(pa_sel=0, lna_sel=rx_en, **{lna_key: dac_code})
            print(f"\n{name} - RX{rx_ch} / {lna_key}: Current DAC code = {dac_code}")
            response = input(f"Is LNA_VDD_current ≈ {lna_current} mA? [y/n]: ").strip().lower()
            if response == 'y':
                input("📝 Note gain & phase, then press Enter...")
                print(f"✅ {name} - RX{rx_ch} / {lna_key} calibrated at DAC = {dac_code}")
                dac_map[(name, rx_ch, lna_key)] = dac_code  # 📥 Save DAC value
                break
            else:
                adj = input("↕️  Enter DAC step (e.g., +2, -1): ").strip()
                try:
                    step = int(adj)
                    dac_code += step
                    if dac_code < 0:
                        dac_code = 256 - abs(dac_code)
                    elif dac_code > 255:
                        dac_code = 255
                except ValueError:
                    print("⚠️ Invalid input. Use format like +2 or -3.")

# -------- PHASE 2: Gain/Phase Tuning (AFTER all DACs are calibrated) --------
lna_dac_log = {}
for (name, hal), addr in zip(hal_devs.items(), dev_addr):
    hal.set_trx_mode(0)
    rx_channels = rf_ch_list[addr]
    lna_channels = bias_ch_list[addr]
    lna_keys = [f'LNA{ch}' for ch in lna_channels]
    lna_dac_log[name] = {}
    
    for rx_ch, lna_key in zip(rx_channels, lna_keys):
        rx_en = 1 << rx_ch
        dac_code = dac_map[(name, rx_ch, lna_key)]  # ✅ Use stored DAC value
        hal_bdst.set_iq_val(Av=0, ant_sel=0xF)

        while True:
            # hal.dac_cfg(pa_sel=0, lna_sel=rx_en, **{lna_key: dac_code})
            try:
                p_input = input(f"Enter p_idx for RX{rx_ch} [range:4 to 124]: ").strip()
                g_input = input(f"Enter g_idx for RX{rx_ch} [range:0 to 31]: ").strip()

                p_idx = max(4, min(124, int(p_input)))
                g_idx = max(0, min(63, int(g_input)))

                hal.set_lut_idx(p_idx=p_idx, g_idx=g_idx, ant_sel=rx_en)
                hal.stg2_load()

                print(f"✅ LUT set: p_idx = {p_idx}, g_idx = {g_idx}")
                satisfied = input("👉 Result OK? (y = done / n = retry): ").strip().lower()
                if satisfied == 'y':
                    lna_dac_log[name][f"RX{rx_ch}_{lna_key}"] = (rx_ch, lna_key, dac_code, p_idx, g_idx)
                    break
                else:
                    print("🔁 Try new values...\n")
            except ValueError:
                print("⚠️ Invalid input. Please enter valid integers.")

# Clean-up
hal_bdst.en_data_path(0)
hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)

# Save CSV
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_filename = f"../RX_LNA_DAC_Calibration_Log_{timestamp}.csv"

with open(log_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Device", "RX_Channel", "LNA_Channel", "DAC_Code", "P_Idx", "G_Idx"])
    for device, channels in lna_dac_log.items():
        for _, (rx_ch, lna_key, code, p_idx, g_idx) in channels.items():
            writer.writerow([device, rx_ch, lna_key, code, p_idx, g_idx])

print(f"\n✅ Calibration log saved as: {log_filename}")
spi.close()
