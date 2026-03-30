Demo

Code: [satcom_tx_gain_phase_single_point_test.py](satcom_tx_gain_phase_single_point_test.py)
Lines: 2 (ant_sel), 5,6 (ph/gain index)
1. TX Psat (set g_idx to 0)
2. Tx P1dB (set g_idx to 0)
3. TX Gain Change
4. TX Phase Change

Code: [satcom_rx_gain_phase_single_point_test.py](satcom_rx_gain_phase_single_point_test.py)
Lines: 8 (ant_sel), 12,13 (ph/gain index)
5. RX NF (set g_idx to 0)
6. RX Gain Change
7. RX Phase Change
8. RX P1dB (set g_idx to 0)

Code: [sar_adc.py](sar_adc.py)
9. SAR ADC (Along with VDD2p7 connection, connect the JP13(GP7) pin to external Vin supply, run the code, sar adc code will get displayed)
           (to change the adc input you can select either of one gp4/gp5/gp6/gp7)
           (SAR ADC output will vary from 0 to 511 depending upon Vin)