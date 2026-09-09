import sys

sys.path.append('../../include')
import os
from libs.fd_cmn.instruments.instruments import instruments
import ORION_RF_CONTROL_FUNC as RF_CTRL_FUNC
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *
from SPI import *
import pandas as pd
import numpy as np
import xlsxwriter as xlsw
import time
import datetime

version = 'v2'
ant_sel = 0x1  # Antenna selection for RX0: 0x1, RX1: 0x2, RX2: 0x4, RX3: 0x8
chip_id = 'A1'
mode = "dual_lut"  # single_lut, dual_lut

f = 17
f_min = 12
f_max = 19
f_step = 0.25
freq_array = np.arange(f_min, f_max + f_step, f_step)

target_freqs = [12, 15, 17, 19]
target_idx = [np.argmin(np.abs(freq_array - tf)) for tf in target_freqs]

p_idx_array = [4, 19, 34, 49]  # Corresponding to phase values of [0,45,90,135,180] degrees
phase_values = [0, 45, 90, 135]

d1 = 0.1  # delay after setting IQ
d2 = 0.3  # delay after normalization

# ================= CHANNEL MAPPING =================
ant_to_channel = {
    0x1: 0,
    0x2: 1,
    0x4: 2,
    0x8: 3
}

if ant_sel in ant_to_channel:
    channel_num = ant_to_channel[ant_sel]
else:
    raise ValueError(f"❌ Invalid ant_sel: {ant_sel}")

print(f"Using Channel: RX{channel_num}")

gi = int((f - f_min) / f_step)  # gain index
pi = int((f - f_min) / f_step)  # phase index
freq_pts = int((f_max - f_min) / f_step) + 1
ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
start_time = time.time()

# ---------------- OUTPUT DIRECTORY ----------------
output_dir = r'G:\Shared drives\PRJ_BFM\BFM_Ku\Silicon Validation\Bench Char\bench_char_data\chip_1\rx\rx_freq_vs_gain_across_gaincode'
os.makedirs(output_dir, exist_ok=True)

# ---------------------------SETUP VNA------------------------
instruments = instruments(required_instruments=['vna'])
instruments.vna.init(num_win=4)  # windows 3/4 needed for the S11/S22 traces
instruments.vna.rm_vna.timeout = 15000
instruments.vna.cfg(1, 'S21_GAIN')
instruments.vna.cfg(2, 'S21_PHASE')
instruments.vna.cfg(3, 'S11_GAIN')
instruments.vna.cfg(4, 'S22_GAIN')
instruments.vna.cfg_freq(start=12e9, stop=19e9, step=250e6)
instruments.vna.cfg_pwr(pwr=-30)

instruments.vna.add_marker(win_id=1, marker_id=1, val=f * 1e9)
instruments.vna.add_marker(win_id=1, marker_id=2, val=12e9)
instruments.vna.add_marker(win_id=1, marker_id=3, val=19e9)

instruments.vna.add_marker(win_id=2, marker_id=1, val=f * 1e9)
instruments.vna.add_marker(win_id=2, marker_id=2, val=12e9)
instruments.vna.add_marker(win_id=2, marker_id=3, val=19e9)

instruments.vna.add_marker(win_id=3, marker_id=1, val=f * 1e9)
instruments.vna.add_marker(win_id=3, marker_id=2, val=12e9)
instruments.vna.add_marker(win_id=3, marker_id=3, val=19e9)

instruments.vna.add_marker(win_id=4, marker_id=1, val=f * 1e9)
instruments.vna.add_marker(win_id=4, marker_id=2, val=12e9)
instruments.vna.add_marker(win_id=4, marker_id=3, val=19e9)

instruments.vna.set_y_axis(win_id=1, ref_level=-30, scale_per_div=5)
instruments.vna.set_y_axis(win_id=2, ref_level=0, scale_per_div=45)
instruments.vna.set_y_axis(win_id=3, ref_level=-30, scale_per_div=5)
instruments.vna.set_y_axis(win_id=4, ref_level=-30, scale_per_div=5)

# Averaging
instruments.vna.write(":SENS:AVER:STAT ON")
instruments.vna.write(":SENS:AVER:COUN 128")

spi = SPI()
orion_csr = ORION_8G_12G(spi)
orion_lut = ORION_8G_12G_lut(spi)
orion_hal = ORION_8G_12G_hal(orion_csr, orion_lut, spi, version)

# if version == 'v2':
#     orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx2__gain_lut__9p5GHz__nombias__vdd_2p7_with_avg.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_1_pm_1p5_pm2_5p95_abs_gain_9p0__nom__vdd_2p7.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2__rx2__gain_lut__9p5GHz__lowbias_00__vdd_2p7_with_avg_for_dual_lut.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/v2_rx0_phase_lut_freq_9p5_gm_0p5_pm_1p4_pm2_5_abs_gain_15__lowbias_00__vdd_2p5.xlsx')
# else:
#     orion_hal.init_lut_new(r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
#                            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

init_

# ---------------- NEW EXCEL FILES ----------------
gain_return_loss = xlsw.Workbook(os.path.join(output_dir, f'RX{channel_num}_gain_and_return_loss_vs_freq.xlsx'))
gain_return_loss_sheet = gain_return_loss.add_worksheet()

gain_vs_gaincode = xlsw.Workbook(os.path.join(output_dir, f'RX{channel_num}_gain_vs_gaincode.xlsx'))
gain_vs_gaincode_sheet = gain_vs_gaincode.add_worksheet()

norm_gain_vs_gaincode = xlsw.Workbook(os.path.join(output_dir, f'RX{channel_num}_norm_gain_vs_gaincode.xlsx'))
norm_gain_vs_gaincode_sheet = norm_gain_vs_gaincode.add_worksheet()

phase_vs_gaincode = xlsw.Workbook(os.path.join(output_dir, f'RX{channel_num}_phase_vs_gaincode.xlsx'))
phase_vs_gaincode_sheet = phase_vs_gaincode.add_worksheet()

for i, freq in enumerate(freq_array):
    gain_vs_gaincode_sheet.write(i + 1, 0, freq)

norm_gain_vs_gaincode_sheet.write(0, 0, 'Gain_Code')
for j, fval in enumerate(target_freqs):
    norm_gain_vs_gaincode_sheet.write(0, j + 1, f'Normalised_gain_dB ({fval}GHz)')

phase_vs_gaincode_sheet.write(0, 0, 'Gain_Code')
for k, phase in enumerate(phase_values):
    phase_vs_gaincode_sheet.write(0, k + 1, f'Phase_deg ({phase} degrees)')

gain_vs_gaincode_sheet.write(0, 0, 'Freq_GHz')
for g_idx in range(64):
    gain_vs_gaincode_sheet.write(0, g_idx + 1, f'Gain_dB ({g_idx})')

gain_return_loss_sheet.write(0, 0, 'Freq_GHz')
gain_return_loss_sheet.write(0, 1, 'Gain_and_return_loss_dB (Channel_gain)')
gain_return_loss_sheet.write(0, 2, 'Gain_and_return_loss_dB (S11)')
gain_return_loss_sheet.write(0, 3, 'Gain_and_return_loss_dB (S22)')

# ================= LOSS FILE =================
# loss_file_path = r'C:\Users\silic\GitHub\orion\results\bench_char_010426\Loss_Calib_vs_Freq_VNA/RFIO_RX0_1m.xlsx'
loss_file_path = r'../../loss_file\loss_1m_7_20Ghz.xlsx'
loss_df = pd.read_excel(loss_file_path)

freq_col = loss_df.columns[0]
loss_col = f"S21 @ {25}C"

if loss_col not in loss_df.columns:
    raise ValueError(f"❌ Column {loss_col} not found")

loss_freq = loss_df[freq_col].values
loss_vals = loss_df[loss_col].values


def get_loss(freq_ghz):
    return np.interp(freq_ghz, loss_freq, loss_vals)


orion_csr.DEVICE_ID.read()
print('device_id = ' + hex(orion_csr.DEVICE_ID.device_id))

orion_csr.REVISION.read()
print('major_revision = ' + hex(orion_csr.REVISION.major_rev))
print('minor_revision = ' + hex(orion_csr.REVISION.minor_rev))

orion_hal.set_tr_mode('INT_TR')
orion_hal.set_trx_mode(0)
orion_hal.init_rx('NOM')
orion_hal.set_tr_mask(rx_mask=0xF)
orion_hal.set_freq('9G')
orion_hal.cfg_stg2_load('REG')
orion_hal.enable_rx_correction(1)
orion_hal.en_data_path(1)

orion_hal.set_lut_idx(4, 0, 0xF)
orion_hal.stg2_load()
time.sleep(d1)
instruments.vna.write(":SENS:AVER:CLE")
time.sleep(d2)
instruments.vna.norm(win_id=2)
time.sleep(d2)

ref_gain = None
gain_vs_gaincode_sheet.write(0, 0, 'Freq_GHz')
for k, p_idx in enumerate(p_idx_array):
    print("Running for Phase Index:", p_idx)
    for g_idx in range(0, 64, 1):
        if mode == "dual_lut":
            if g_idx <= 31:
                # band = '9G'
                orion_hal.set_freq('9G')
                orion_hal.init_rx('NOM')
            else:
                # band = "11G"
                orion_hal.set_freq('11G')
                orion_hal.init_rx('LOW')
        else:
            # band = '9G'
            orion_hal.set_freq('9G')
            orion_hal.init_rx('LOW')

        orion_hal.set_lut_idx(p_idx, g_idx, 0xF)
        orion_hal.stg2_load()
        time.sleep(d1)

        instruments.vna.write(":SENS:AVER:CLE")
        time.sleep(d2)  # Wait for averaging to complete

        s21m = np.array(instruments.vna.query(':CALC:MEAS1:DATA:FDATA?').strip().split(","), dtype=float)
        s21p = np.array(instruments.vna.query(':CALC:MEAS2:DATA:FDATA?').strip().split(","), dtype=float)
        s11m = np.array(instruments.vna.query(':CALC:MEAS3:DATA:FDATA?').strip().split(","), dtype=float)
        s22m = np.array(instruments.vna.query(':CALC:MEAS4:DATA:FDATA?').strip().split(","), dtype=float)

        s21m_cal = np.array([s21m[i] - get_loss(freq_array[i]) for i in range(freq_pts)])

        if g_idx == 0 and p_idx == 4:
            ref_gain = s21m_cal.copy()
            print("✅ gain_return_loss_sheet data captured")
            for i, freq in enumerate(freq_array):
                gain_return_loss_sheet.write(i + 1, 0, freq)
                gain_return_loss_sheet.write(i + 1, 1, s21m_cal[i])
                gain_return_loss_sheet.write(i + 1, 2, s11m[i])
                gain_return_loss_sheet.write(i + 1, 3, s22m[i])

        i_lsb = orion_csr.RX0_I_LSB_TEMP0.read()
        q_lsb = orion_csr.RX0_Q_LSB_TEMP0.read()
        av_lsb = orion_csr.RX0_AV_LSB_TEMP0.read()
        msb = orion_csr.RX0_MSB_TEMP0.read()

        phase_val_i = ((msb & 0x1) << 8) | (i_lsb & 0xFF)
        phase_val_q = ((msb & 0x2) << 7) | (q_lsb & 0xFF)
        gain_val = ((msb & 0x1C) << 6) | (av_lsb & 0xFF)

        print(
            f'Gain Code: {g_idx}, Target Gain: {(s21m[pi] + orion_hal.target_gain_dB):.2f}, Observed Gain: {s21m[pi]:.2f}, Observed Phase: {s21p[pi]:.2f}')
        if p_idx == 4:
            norm_gain = s21m_cal - ref_gain

            for i, freq in enumerate(freq_array):
                gain_vs_gaincode_sheet.write(i + 1, g_idx + 1, s21m_cal[i])

            norm_gain_vs_gaincode_sheet.write(g_idx + 1, 0, g_idx)
            for j, idx in enumerate(target_idx):
                norm_gain_vs_gaincode_sheet.write(g_idx + 1, j + 1, norm_gain[idx])

        phase_vs_gaincode_sheet.write(g_idx + 1, 0, g_idx)
        phase_vs_gaincode_sheet.write(g_idx + 1, k + 1, s21p[pi])

gain_return_loss.close()
gain_vs_gaincode.close()
norm_gain_vs_gaincode.close()
phase_vs_gaincode.close()
instruments.vna.cfg_pwr(pwr=-60)
instruments.vna.write(":OUTP OFF")

elapsed = time.time() - start_time
print(f'Elapsed time: {elapsed:.1f} s')
spi.close()