sanity - basic sanity check (device id, revision values, register r/w)

rx_gain_sweep_low_bias_0deg_averaging, rx_phase_sweep_low_bias_0dbm_averaging - gain/phase sweep automation through luts
									      - line no 2: give proper ant_sel value (0x1:RX0, 0X2:RX1, 0X4:RX2, 0X8:RX3)

For v2:
RXx_Gain_Phase_Single_Point_Set_Nom_Bias_4ch_v2 - NF, single point gain/phase test through direct I/Q force
						- change the bias mode at line no 7 (NOM/LOW)
						- line no 516-530: directly force the I/Q values for each channel [eg: (255,0) for iphase, (0,255) for qphase, (511,0) for -							iphase,(0,511) for -qphase]

TXx_Gain_Phase_Single_Point_Set_Nom_Bias_4ch_v2 - PSAT, single point gain/phase test through direct I/Q force
						- change the bias mode at line no 7 (MAX/LOW)
						- line no 157: for channel selection (0x1:TX0, 0X2:TX1, 0X4:TX2, 0X8:TX3)
					        - tune line no:117 "tx_final_gain_val[i] = 0-31" for your desired PSAT value (31 - high psat, reduce this value for low psat)
						- line no 268-278: directly force the I/Q values for each channel [eg: (255,0) for iphase, (0,255) for qphase, (511,0) for -							iphase,(0,511) for -qphase]

tx_phase_sweep_nombias_v2 - phase sweep automation of tx
			  - line no 2: give proper ant_sel value (0x1:TX0, 0X2:TX1, 0X4:TX2, 0X8:TX3)

tr_switch_with_tx_rx_bias_with_lut_10W - for EXT PRT signal
				       - tune line no: 489 for rx ant_sel value, line no: 490: for tx ant_sel value


tr_switch_with_power_on_programming_v2 - for PA/LNA bias check - for INT PRT signal
 
bfm_DETx_test - detector test