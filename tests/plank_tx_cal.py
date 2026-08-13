import sys
import time

sys.path.append('../include')

from ORION_8G_12G import *
from SPI import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
import csv
import time
############### User Settings ##############################################
version = 'v2'
dev_addr = [0x00, 0x03]

rf_ch_list = {
    0x00: [0, 1, 2, 3],
    0x03: [0, 1, 2, 3]
}

bias_ch_list = {
    0x00: [0, 1, 2, 3],
    0x03: [0, 1, 2, 3]
}
psat=38
initial_dac_code = 65
initial_Av_val = 25
############## END: User Settings - do NOT Modify anything after this ######

spi = SPI()
orion_bdst = ORION_8G_12G(spi, 0, 1)
orion_lut_bdst = ORION_8G_12G_lut(spi,0,1)

devices = {f'orion_dev{i}': ORION_8G_12G(spi, addr, 0) for i, addr in enumerate(dev_addr)}
devices_lut = {
    f'orion_lut{i}': ORION_8G_12G_lut(spi, addr, 0)
    for i, addr in enumerate(dev_addr)
}
hal_devs = {
    name: ORION_8G_12G_hal(dev, devices_lut[f'orion_lut{i}'], spi, version)
    for i, (name, dev) in enumerate(devices.items())
}
hal_bdst = ORION_8G_12G_hal(orion_bdst,orion_lut_bdst,spi,version)

# Write DACs and reset TR configs via broadcast
hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)
hal_bdst.init_lut_new(r'../final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                        r'../results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                        r'../results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                        r'../results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
                        r'../results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
                        r'../results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

hal_bdst.cfg_stg2_load('REG')
hal_bdst.set_tr_mode('EXT_TR')
hal_bdst.set_trx_mode(1)
hal_bdst.en_data_path(1)
hal_bdst.init_tx('5W_FEM')
spi.pa_set()
for (name,hal), addr in zip(hal_devs.items(), dev_addr):
    hal.set_trx_mode(1)
    tx_channels = rf_ch_list[addr]
    tx_mask = sum(1 << ch for ch in tx_channels)
    hal.set_tr_mask(tx_mask=tx_mask) 
    hal.en_data_path(1)
    
pwr_meter_reading = psat-30    
# -------- PHASE 1: PA DAC Calibration, default setting gain,phase from VNA (ALL channels first) --------
dac_map = {}
Av_map = {}
for (name,hal), addr in zip(hal_devs.items(), dev_addr):
    hal.set_trx_mode(1)
    tx_channels = rf_ch_list[addr]
    pa_channels = bias_ch_list[addr]
    pa_keys = [f'PA{ch}' for ch in pa_channels]  # Dynamically mapped            
    print(f"🔧 Device: {name} (ADDR: {hex(addr)})")
        
    for tx_ch, pa_key in zip(tx_channels, pa_keys):
        tx_en = 1 << tx_ch
        p_idx = 0
        g_idx = 0
        hal_bdst.set_iq_val(Av=0, ant_sel=0xF)
        hal.set_lut_idx(p_idx=p_idx, g_idx=g_idx, ant_sel=tx_en)
        # hal.en_data_path(1)
        hal.stg2_load()

        dac_code = initial_dac_code
        Av_val = initial_Av_val
        
        while True:
            hal.dac_cfg(pa_sel=tx_en, lna_sel=0, **{pa_key: dac_code})
            hal.force_tx_Av(Av=Av_val, ant_sel=tx_en)
            print(f"\n{name} - TX{tx_ch} / {pa_key}: Current DAC code = {dac_code}, Current forced Av = {Av_val}")
            response = input(f"Is Power meter reading ≈ {pwr_meter_reading} dBm? [y/n]: ").strip().lower()
            if response == 'y':
                input("📝 Note gain & phase, then press Enter...")
                print(f"✅ {name} - TX{tx_ch} / {pa_key} calibrated at DAC = {dac_code} and forced AV = {Av_val}")
                dac_map[(tx_ch, pa_key)] = dac_code  # 📥 Save DAC value
                Av_map[(tx_ch, pa_key)] = Av_val # 📥 Save Av value
                break
            else:
                adj = input("↕️  Enter DAC step (e.g., +2, -1): ").strip()
                adj_1 = input("↕️  Enter Av_val step (e.g., +2, -1): ").strip()
                try:
                    step = int(adj)
                    dac_code += step
                    
                    step_1 = int(adj_1)                    
                    Av_val += step_1
                    
                    if dac_code < 0:
                        dac_code = 256 - abs(dac_code)
                    elif dac_code > 255:
                        dac_code = 255
                        
                    if Av_val < 0:
                        Av_val = 0
                    elif Av_val > 31:
                        Av_val = 0
                        
                except ValueError:
                    print("⚠️ Invalid input. Use format like +2 or -3.")

# -------- PHASE 2: Gain/Phase Tuning (AFTER all DACs are calibrated) --------
pa_dac_log = {}

for (name,hal), addr in zip(hal_devs.items(), dev_addr):
    pa_dac_log[name] = {}
    hal.set_trx_mode(1)
    tx_channels = rf_ch_list[addr]
    pa_channels = bias_ch_list[addr]
    pa_keys = [f'PA{ch}' for ch in pa_channels]  # Dynamically mapped            
    print(f"🔧 Device: {name} (ADDR: {hex(addr)})")
    
    for tx_ch, pa_key in zip(tx_channels, pa_keys):
        hal_bdst.set_iq_val(Av=0, ant_sel=0xF)
        tx_en = 1 << tx_ch
        dac_code = dac_map[(tx_ch, pa_key)]  # ✅ Use stored DAC value
        Av_val = Av_map[(tx_ch, pa_key)]
        hal.force_tx_Av(Av=Av_val, ant_sel=tx_en)
        while True:           
            try:
                p_input = input(f"Enter p_idx for TX{tx_ch}: ").strip()
                g_input = input(f"Enter g_idx for TX{tx_ch}: ").strip()
    
                p_idx = max(0, min(127, int(p_input)))
                g_idx = max(0, min(63, int(g_input)))
    
                hal.set_lut_idx(p_idx=p_idx, g_idx=g_idx, ant_sel=tx_en)
                hal.stg2_load()
    
                print(f"✅ LUT set: p_idx = {p_idx}, g_idx = {g_idx}")
                satisfied = input("👉 Result OK? (y = done / n = retry): ").strip().lower()
                if satisfied == 'y':
                    pa_dac_log[name][f"TX{tx_ch}_{pa_key}"] = (tx_ch, pa_key, dac_code, p_idx, g_idx, Av_val)
                    break
                else:
                    print("🔁 Try new values...\n")
            except ValueError:
                print("⚠️ Invalid input. Please enter valid integers.")    
        
# Setting data path and tx and rx mask to 0 for safety    
hal_bdst.en_data_path(0)
hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)

# Save log to CSV
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_filename = f"../PA_DAC_Calibration_Log_{timestamp}.csv"

with open(log_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Device", "TX_Channel", "PA_Channel", "DAC_Code", "P_Idx", "G_Idx", "Forced_Av"])
    for device, channels in pa_dac_log.items():
        for _, (tx_ch, pa_key, code, p_idx, g_idx, Av_val) in channels.items():
            writer.writerow([device, tx_ch, pa_key, code, p_idx, g_idx, Av_val])

print(f"\n Calibration log saved as: {log_filename}")

spi.close()
