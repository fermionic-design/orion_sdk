Code: "\marine\sanity.py"
1. basic sanity check (device id, revision values, register r/w)

Code: "\marine\tx_gain_phase_single_point_test_demo.py"
Lines: 2 (ant_sel), 3,4 (ph/gain index)
1. TX Psat (set g_idx to 0)
2. Tx P1dB (set g_idx to 0)
3. TX Gain Change
4. TX Phase Change

Code: "\marine\tx_gain_phase_single_point_test_loop_demo.py"
Lines: 2 (ant_sel), 3,4 (ph/gain index)
1. TX phase sweep across all p_idx

Code: "\marine\sar_adc.py"
1. SAR ADC (Along with VDD2p7 connection, connect the JP13(GP7) pin to external Vin supply, run the code, sar adc code will get displayed)
(to change the adc input you can select either of one gp4/gp5/gp6/gp7)
(SAR ADC output will vary from 0 to 511 depending upon Vin)

Code: "\marine\bfm_pa_bias_test.py"
1. Setup: VDD_2P7-2.7V, VDD_NEG-m5V
2. Connections: Connect the PA_BIASx pin to a multimeter to observe the voltage change before and after pressing enter (x can be 0,1,2,3)