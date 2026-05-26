Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\sanity.py](sanity.py)
basic sanity check \[device id(0xf2), revision values(major \& minor revision 0x1), register r/w(5a)]

Code: [c:\Users\silic\GitHub\orion_sdk\tests\zeta\tx_gain_phase_single_point_test.py](tx_gain_phase_single_point_test.py)
1. TX Psat (set g\_idx to 0) in CW mode
2. Tx P1dB (set g\_idx to 0)
3. TX Gain Change
4. TX Phase Change

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\rx_gain_phase_single_point_test.py](rx_gain_phase_single_point_test.py)
Lines: 8 (ant\_sel), 12,13 (ph/gain index)
1. RX NF (set g\_idx to 0)
2. RX Gain Change
3. RX Phase Change
4. RX P1dB (set g\_idx to 0)

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\sar_adc.py](sar_adc.py)
SAR ADC (Along with VDD2p7 connection, connect the JP13(GP7) pin to external Vin supply, run the code, sar adc code will get displayed)
(to change the adc input you can select either of one gp4/gp5/gp6/gp7)
(SAR ADC output will vary from 0 to 511 depending upon Vin)

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\sar_adc_code_vs_temp_across_state](sar_adc_code_vs_temp_across_state.py)
Run this code to see sar_adc code versus the chip_backside_temperature change
Setup: Connect the VDD 2P7V to the BFM chip. It is also better to observe the chip's temperature by probing a thermometer at the exposed portion of the BFM chip. Change the temperature using a chamber, observe the probed temperature and run the code to see the SAR ADC code at that temperature.
You can change the mode (line 1 in the code) from idle to tx or rx to observe the SAR ADC code change across biases.

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\bfm_lna_bias_test.py](bfm_lna_bias_test,.py)
Setup: VDD_2P7-2.7V, VDD_NEG-m5V
Connections with DSO: Connect the soldered TR wire, PA\_BIASx, LNA BIASx to three respective DSO channel (x can be 0,1,2,3)
Run the code and observe the waveforms in DSO

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\bfm_pa_bias_test.py](bfm_pa_bias_test.py)
Line: 22 0x1 for TX0, 0x2 for TX1, 0x4 for TX2, 0x8 for TX3
Setup: VDD_2P7-2.7V, VDD_NEG-m5V
Connections: Connect the PA\_BIASx pin to a multimeter to observe the voltage change before and after pressing enter (x can be 0,1,2,3)

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\bfm_DETx_test.py](bfm_DETx_test.py)
Line no: 112, give proper detector channel as input -  0 for DET0, 1 for DET1, 2 for DET2 and 3 for DET3
Setup: Vsup = 2.5-3.3V (nominal - 2.7V)
Feed any input power from -20dBm to 16dBm through Signal generator to DETx port,set any freq from 8-12GHz and record the SAR ADC output, Flash ADC output

Code: [C:\Users\silic\GitHub\orion_sdk\tests\zeta\tr_switch_with_power_on_programming_v2.py](tr_switch_with_power_on_programming_v2.py)
Run this we you want to check the tr,lna,pa bias switching and delays
Line no: 30 and 31 give proper ant sel input, PA_BIAS0 means 0x1 at 31 and LNA_BIAS0 means 0x1 at 30 and so for other channels

Code: [c:\Users\silic\GitHub\orion_sdk\tests\zeta\tr_switch_with_tx_rx_bias_with_lut_10W_v2.py](tr_switch_with_tx_rx_bias_with_lut_10W_v2.py)
This code should be run when you are using external TR signal
Line no 492, give ant sel no
Droop was seen to be 0.04dB and PSat was 16.9+1.7dBm

Download Pycharm: https://www.jetbrains.com/pycharm/download/?section=windows exe file for windows
Github access to be given by Fermionic
Please work on the zeta folder for your validation
Download Github: https://desktop.github.com/download/
Setup Github by referring this document: [Get started with GITHUB account and repository.pdf](Get%20started%20with%20GITHUB%20account%20and%20repository.pdf)
