Code: [sanity.py](C:\\\\Users\\\\anany\\\\Github\\\\orion_sdk\\\\tests\\\\gamma\\\\sanity.py)

basic sanity check \[device id(0xf2), revision values(major \& minor revision 0x1), register r/w(5a)]



Code: [tx\_gain\_phase\_single\_point\_test.py](alpha_tx_gain_phase_single_point_test.py)
Lines: 2 (ant\_sel), 5,6 (ph/gain index)

1. TX Psat (set g\_idx to 0)
2. Tx P1dB (set g\_idx to 0)
3. TX Gain Change
4. TX Phase Change



Code: [rx\_gain\_phase\_single\_point\_test.py](alpha_rx_gain_phase_single_point_test.py)
Lines: 8 (ant\_sel), 12,13 (ph/gain index)
5. RX NF (set g\_idx to 0)
6. RX Gain Change
7. RX Phase Change
8. RX P1dB (set g\_idx to 0)



Code: [sar\_adc.py](sar_adc.py)
SAR ADC (Along with VDD2p7 connection, connect the JP13(GP7) pin to external Vin supply, run the code, sar adc code will get displayed)
(to change the adc input you can select either of one gp4/gp5/gp6/gp7)
(SAR ADC output will vary from 0 to 511 depending upon Vin)



Code: [sar\_adc\_code\_vs\_temp\_across\_state.py"](sar_adc.py)

sar\_adc code versus the chip\_backside\_temperature change

Setup: Connect the VDD 2P7V to the BFM chip. It is also better to observe the chip's temperature by probing a thermometer at the exposed portion of the BFM chip. Change the temperature using a chamber, observe the probed temperature and run the code to see the SAR ADC code at that temperature.

You can change the mode (line 1 in the code) from idle to tx or rx to observe the SAR ADC code change across biases.



Code: [bfm\_lna\_bias\_test.py](C:\\\\Users\\\\anany\\\\Github\\\\orion_sdk\\\\tests\\\\gamma)

Setup: VDD\_2P7-2.7V, VDD\_NEG-m5V

Connections with DSO: Connect the soldered TR wire, PA\_BIASx, LNA BIASx to three respective DSO channel (x can be 0,1,2,3)

Run the code and observe the waveforms in DSO



Code: [bfm\_pa\_bias\_test.py](C:\\\\Users\\\\anany\\\\Github\\\\orion_sdk\\\\tests\\\\gamma\\\\bfm_pa_bias_test.py)

Line: 22 0x1 for TX0, 0x2 for TX1, 0x4 for TX2, 0x8 for TX3

Setup: VDD\_2P7-2.7V, VDD\_NEG-m5V

Connections: Connect the PA\_BIASx pin to a multimeter to observe the voltage change before and after pressing enter (x can be 0,1,2,3)



Code: [bfm\_DETx\_test.py](C:\\\\Users\\\\anany\\\\OneDrive\\\\Github\\\\orion_sdk\\\\tests\\\\gamma\\\\bfm_DETx_test.py)

Line no: 112, give proper detector channel as input -  0 for DET0, 1 for DET1, 2 for DET2 and 3 for DET3

Setup:

Vsup = 2.5-3.3V (nominal - 2.7V)

Feed any input power from -20dBm to 16dBm through Signal generator to DETx port,set any freq from 8-12GHz

and record the SAR ADC output, Flash ADC output

