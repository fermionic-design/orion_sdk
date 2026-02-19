class DEVICE_ID:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 0
		self.device_id = 0
	def write(self):
		val = 0
		val |= self.device_id << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.device_id = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REVISION:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 1
		self.major_rev = 0
		self.minor_rev = 0
	def write(self):
		val = 0
		val |= self.major_rev << 0
		val |= self.minor_rev << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.major_rev = (val & 0x0F) >> 0
		self.minor_rev = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_TX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 2
		self.phase_code_tx0 = 0
	def write(self):
		val = 0
		val |= self.phase_code_tx0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_tx0 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_TX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 3
		self.gain_code_tx0 = 0
	def write(self):
		val = 0
		val |= self.gain_code_tx0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_tx0 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_TX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 4
		self.phase_code_tx1 = 0
	def write(self):
		val = 0
		val |= self.phase_code_tx1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_tx1 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_TX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 5
		self.gain_code_tx1 = 0
	def write(self):
		val = 0
		val |= self.gain_code_tx1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_tx1 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_TX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 6
		self.phase_code_tx2 = 0
	def write(self):
		val = 0
		val |= self.phase_code_tx2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_tx2 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_TX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 7
		self.gain_code_tx2 = 0
	def write(self):
		val = 0
		val |= self.gain_code_tx2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_tx2 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_TX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 8
		self.phase_code_tx3 = 0
	def write(self):
		val = 0
		val |= self.phase_code_tx3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_tx3 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_TX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 9
		self.gain_code_tx3 = 0
	def write(self):
		val = 0
		val |= self.gain_code_tx3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_tx3 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_RX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 10
		self.phase_code_rx0 = 0
	def write(self):
		val = 0
		val |= self.phase_code_rx0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_rx0 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_RX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 11
		self.gain_code_rx0 = 0
	def write(self):
		val = 0
		val |= self.gain_code_rx0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_rx0 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_RX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 12
		self.phase_code_rx1 = 0
	def write(self):
		val = 0
		val |= self.phase_code_rx1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_rx1 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_RX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 13
		self.gain_code_rx1 = 0
	def write(self):
		val = 0
		val |= self.gain_code_rx1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_rx1 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_RX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 14
		self.phase_code_rx2 = 0
	def write(self):
		val = 0
		val |= self.phase_code_rx2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_rx2 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_RX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 15
		self.gain_code_rx2 = 0
	def write(self):
		val = 0
		val |= self.gain_code_rx2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_rx2 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PHASE_CODE_RX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 16
		self.phase_code_rx3 = 0
	def write(self):
		val = 0
		val |= self.phase_code_rx3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.phase_code_rx3 = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class GAIN_CODE_RX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 17
		self.gain_code_rx3 = 0
	def write(self):
		val = 0
		val |= self.gain_code_rx3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.gain_code_rx3 = (val & 0x3F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class UPDATE_CODE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 18
		self.update_code = 0
	def write(self):
		val = 0
		val |= self.update_code << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.update_code = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RSVD0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 19
		self.rsvd0 = 0
	def write(self):
		val = 0
		val |= self.rsvd0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd0 = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class BEAM_CODE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 20
		self.beam_code = 0
	def write(self):
		val = 0
		val |= self.beam_code << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.beam_code = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RSVD1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 21
		self.rsvd1 = 0
	def write(self):
		val = 0
		val |= self.rsvd1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd1 = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class BEAM_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 22
		self.use_beam_lut = 0
		self.beam_cfg_done = 0
		self.tx_beam_seq_en = 0
		self.rx_beam_seq_en = 0
	def write(self):
		val = 0
		val |= self.use_beam_lut << 0
		val |= self.beam_cfg_done << 1
		val |= self.tx_beam_seq_en << 2
		val |= self.rx_beam_seq_en << 3
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.use_beam_lut = (val & 0x01) >> 0
		self.beam_cfg_done = (val & 0x02) >> 1
		self.tx_beam_seq_en = (val & 0x04) >> 2
		self.rx_beam_seq_en = (val & 0x08) >> 3
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class STG2_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 23
		self.use_reg_for_stg2_update = 0
	def write(self):
		val = 0
		val |= self.use_reg_for_stg2_update << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.use_reg_for_stg2_update = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class FREQ_ID:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 24
		self.freq_id = 0
	def write(self):
		val = 0
		val |= self.freq_id << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.freq_id = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RSVD2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 25
		self.rsvd2 = 0
	def write(self):
		val = 0
		val |= self.rsvd2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd2 = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RSVD3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 26
		self.rsvd3 = 0
	def write(self):
		val = 0
		val |= self.rsvd3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd3 = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class CORR_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 27
		self.en_phase_corr = 0
		self.en_gain_corr = 0
	def write(self):
		val = 0
		val |= self.en_phase_corr << 0
		val |= self.en_gain_corr << 1
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_phase_corr = (val & 0x01) >> 0
		self.en_gain_corr = (val & 0x02) >> 1
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class COPY_MODE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 28
		self.copy_mode = 0
	def write(self):
		val = 0
		val |= self.copy_mode << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.copy_mode = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class SPI_MODE_CTRL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 29
		self.spi_3_wire_mode = 0
	def write(self):
		val = 0
		val |= self.spi_3_wire_mode << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.spi_3_wire_mode = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_I_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 30
		self.tx0_i_lsb = 0
	def write(self):
		val = 0
		val |= self.tx0_i_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_i_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_Q_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 31
		self.tx0_q_lsb = 0
	def write(self):
		val = 0
		val |= self.tx0_q_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_q_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_AV_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 32
		self.tx0_av_lsb = 0
	def write(self):
		val = 0
		val |= self.tx0_av_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_av_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_MSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 33
		self.tx0_i_msb = 0
		self.tx0_q_msb = 0
		self.tx0_av_msb = 0
	def write(self):
		val = 0
		val |= self.tx0_i_msb << 0
		val |= self.tx0_q_msb << 1
		val |= self.tx0_av_msb << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_i_msb = (val & 0x01) >> 0
		self.tx0_q_msb = (val & 0x02) >> 1
		self.tx0_av_msb = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_FINAL_AV:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 34
		self.tx0_final_av = 0
	def write(self):
		val = 0
		val |= self.tx0_final_av << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_final_av = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_I_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 35
		self.rx0_i_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_Q_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 36
		self.rx0_q_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx0_q_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_q_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_AV_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 37
		self.rx0_av_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx0_av_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_av_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_MSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 38
		self.rx0_i_msb_temp0 = 0
		self.rx0_q_msb_temp0 = 0
		self.rx0_av_msb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_msb_temp0 << 0
		val |= self.rx0_q_msb_temp0 << 1
		val |= self.rx0_av_msb_temp0 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_msb_temp0 = (val & 0x01) >> 0
		self.rx0_q_msb_temp0 = (val & 0x02) >> 1
		self.rx0_av_msb_temp0 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_I_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 39
		self.rx0_i_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_Q_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 40
		self.rx0_q_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx0_q_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_q_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_AV_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 41
		self.rx0_av_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx0_av_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_av_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_MSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 42
		self.rx0_i_msb_temp1 = 0
		self.rx0_q_msb_temp1 = 0
		self.rx0_av_msb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_msb_temp1 << 0
		val |= self.rx0_q_msb_temp1 << 1
		val |= self.rx0_av_msb_temp1 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_msb_temp1 = (val & 0x01) >> 0
		self.rx0_q_msb_temp1 = (val & 0x02) >> 1
		self.rx0_av_msb_temp1 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_I_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 43
		self.rx0_i_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_Q_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 44
		self.rx0_q_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx0_q_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_q_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_AV_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 45
		self.rx0_av_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx0_av_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_av_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_MSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 46
		self.rx0_i_msb_temp2 = 0
		self.rx0_q_msb_temp2 = 0
		self.rx0_av_msb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_msb_temp2 << 0
		val |= self.rx0_q_msb_temp2 << 1
		val |= self.rx0_av_msb_temp2 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_msb_temp2 = (val & 0x01) >> 0
		self.rx0_q_msb_temp2 = (val & 0x02) >> 1
		self.rx0_av_msb_temp2 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_I_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 47
		self.rx0_i_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_Q_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 48
		self.rx0_q_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx0_q_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_q_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_AV_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 49
		self.rx0_av_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx0_av_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_av_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX0_MSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 50
		self.rx0_i_msb_temp3 = 0
		self.rx0_q_msb_temp3 = 0
		self.rx0_av_msb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx0_i_msb_temp3 << 0
		val |= self.rx0_q_msb_temp3 << 1
		val |= self.rx0_av_msb_temp3 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_i_msb_temp3 = (val & 0x01) >> 0
		self.rx0_q_msb_temp3 = (val & 0x02) >> 1
		self.rx0_av_msb_temp3 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_I_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 51
		self.tx1_i_lsb = 0
	def write(self):
		val = 0
		val |= self.tx1_i_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_i_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_Q_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 52
		self.tx1_q_lsb = 0
	def write(self):
		val = 0
		val |= self.tx1_q_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_q_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_AV_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 53
		self.tx1_av_lsb = 0
	def write(self):
		val = 0
		val |= self.tx1_av_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_av_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_MSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 54
		self.tx1_i_msb = 0
		self.tx1_q_msb = 0
		self.tx1_av_msb = 0
	def write(self):
		val = 0
		val |= self.tx1_i_msb << 0
		val |= self.tx1_q_msb << 1
		val |= self.tx1_av_msb << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_i_msb = (val & 0x01) >> 0
		self.tx1_q_msb = (val & 0x02) >> 1
		self.tx1_av_msb = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_FINAL_AV:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 55
		self.tx1_final_av = 0
	def write(self):
		val = 0
		val |= self.tx1_final_av << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_final_av = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_I_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 56
		self.rx1_i_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_Q_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 57
		self.rx1_q_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx1_q_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_q_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_AV_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 58
		self.rx1_av_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx1_av_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_av_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_MSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 59
		self.rx1_i_msb_temp0 = 0
		self.rx1_q_msb_temp0 = 0
		self.rx1_av_msb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_msb_temp0 << 0
		val |= self.rx1_q_msb_temp0 << 1
		val |= self.rx1_av_msb_temp0 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_msb_temp0 = (val & 0x01) >> 0
		self.rx1_q_msb_temp0 = (val & 0x02) >> 1
		self.rx1_av_msb_temp0 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_I_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 60
		self.rx1_i_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_Q_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 61
		self.rx1_q_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx1_q_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_q_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_AV_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 62
		self.rx1_av_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx1_av_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_av_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_MSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 63
		self.rx1_i_msb_temp1 = 0
		self.rx1_q_msb_temp1 = 0
		self.rx1_av_msb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_msb_temp1 << 0
		val |= self.rx1_q_msb_temp1 << 1
		val |= self.rx1_av_msb_temp1 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_msb_temp1 = (val & 0x01) >> 0
		self.rx1_q_msb_temp1 = (val & 0x02) >> 1
		self.rx1_av_msb_temp1 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_I_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 64
		self.rx1_i_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_Q_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 65
		self.rx1_q_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx1_q_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_q_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_AV_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 66
		self.rx1_av_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx1_av_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_av_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_MSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 67
		self.rx1_i_msb_temp2 = 0
		self.rx1_q_msb_temp2 = 0
		self.rx1_av_msb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_msb_temp2 << 0
		val |= self.rx1_q_msb_temp2 << 1
		val |= self.rx1_av_msb_temp2 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_msb_temp2 = (val & 0x01) >> 0
		self.rx1_q_msb_temp2 = (val & 0x02) >> 1
		self.rx1_av_msb_temp2 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_I_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 68
		self.rx1_i_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_Q_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 69
		self.rx1_q_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx1_q_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_q_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_AV_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 70
		self.rx1_av_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx1_av_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_av_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX1_MSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 71
		self.rx1_i_msb_temp3 = 0
		self.rx1_q_msb_temp3 = 0
		self.rx1_av_msb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx1_i_msb_temp3 << 0
		val |= self.rx1_q_msb_temp3 << 1
		val |= self.rx1_av_msb_temp3 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_i_msb_temp3 = (val & 0x01) >> 0
		self.rx1_q_msb_temp3 = (val & 0x02) >> 1
		self.rx1_av_msb_temp3 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_I_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 72
		self.tx2_i_lsb = 0
	def write(self):
		val = 0
		val |= self.tx2_i_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_i_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_Q_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 73
		self.tx2_q_lsb = 0
	def write(self):
		val = 0
		val |= self.tx2_q_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_q_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_AV_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 74
		self.tx2_av_lsb = 0
	def write(self):
		val = 0
		val |= self.tx2_av_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_av_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_MSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 75
		self.tx2_i_msb = 0
		self.tx2_q_msb = 0
		self.tx2_av_msb = 0
	def write(self):
		val = 0
		val |= self.tx2_i_msb << 0
		val |= self.tx2_q_msb << 1
		val |= self.tx2_av_msb << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_i_msb = (val & 0x01) >> 0
		self.tx2_q_msb = (val & 0x02) >> 1
		self.tx2_av_msb = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_FINAL_AV:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 76
		self.tx2_final_av = 0
	def write(self):
		val = 0
		val |= self.tx2_final_av << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_final_av = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_I_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 77
		self.rx2_i_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_Q_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 78
		self.rx2_q_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx2_q_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_q_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_AV_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 79
		self.rx2_av_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx2_av_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_av_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_MSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 80
		self.rx2_i_msb_temp0 = 0
		self.rx2_q_msb_temp0 = 0
		self.rx2_av_msb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_msb_temp0 << 0
		val |= self.rx2_q_msb_temp0 << 1
		val |= self.rx2_av_msb_temp0 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_msb_temp0 = (val & 0x01) >> 0
		self.rx2_q_msb_temp0 = (val & 0x02) >> 1
		self.rx2_av_msb_temp0 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_I_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 81
		self.rx2_i_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_Q_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 82
		self.rx2_q_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx2_q_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_q_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_AV_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 83
		self.rx2_av_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx2_av_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_av_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_MSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 84
		self.rx2_i_msb_temp1 = 0
		self.rx2_q_msb_temp1 = 0
		self.rx2_av_msb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_msb_temp1 << 0
		val |= self.rx2_q_msb_temp1 << 1
		val |= self.rx2_av_msb_temp1 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_msb_temp1 = (val & 0x01) >> 0
		self.rx2_q_msb_temp1 = (val & 0x02) >> 1
		self.rx2_av_msb_temp1 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_I_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 85
		self.rx2_i_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_Q_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 86
		self.rx2_q_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx2_q_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_q_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_AV_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 87
		self.rx2_av_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx2_av_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_av_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_MSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 88
		self.rx2_i_msb_temp2 = 0
		self.rx2_q_msb_temp2 = 0
		self.rx2_av_msb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_msb_temp2 << 0
		val |= self.rx2_q_msb_temp2 << 1
		val |= self.rx2_av_msb_temp2 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_msb_temp2 = (val & 0x01) >> 0
		self.rx2_q_msb_temp2 = (val & 0x02) >> 1
		self.rx2_av_msb_temp2 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_I_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 89
		self.rx2_i_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_Q_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 90
		self.rx2_q_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx2_q_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_q_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_AV_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 91
		self.rx2_av_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx2_av_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_av_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX2_MSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 92
		self.rx2_i_msb_temp3 = 0
		self.rx2_q_msb_temp3 = 0
		self.rx2_av_msb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx2_i_msb_temp3 << 0
		val |= self.rx2_q_msb_temp3 << 1
		val |= self.rx2_av_msb_temp3 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_i_msb_temp3 = (val & 0x01) >> 0
		self.rx2_q_msb_temp3 = (val & 0x02) >> 1
		self.rx2_av_msb_temp3 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_I_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 93
		self.tx3_i_lsb = 0
	def write(self):
		val = 0
		val |= self.tx3_i_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_i_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_Q_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 94
		self.tx3_q_lsb = 0
	def write(self):
		val = 0
		val |= self.tx3_q_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_q_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_AV_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 95
		self.tx3_av_lsb = 0
	def write(self):
		val = 0
		val |= self.tx3_av_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_av_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_MSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 96
		self.tx3_i_msb = 0
		self.tx3_q_msb = 0
		self.tx3_av_msb = 0
	def write(self):
		val = 0
		val |= self.tx3_i_msb << 0
		val |= self.tx3_q_msb << 1
		val |= self.tx3_av_msb << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_i_msb = (val & 0x01) >> 0
		self.tx3_q_msb = (val & 0x02) >> 1
		self.tx3_av_msb = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_FINAL_AV:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 97
		self.tx3_final_av = 0
	def write(self):
		val = 0
		val |= self.tx3_final_av << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_final_av = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_I_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 98
		self.rx3_i_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_Q_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 99
		self.rx3_q_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx3_q_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_q_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_AV_LSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 100
		self.rx3_av_lsb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx3_av_lsb_temp0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_av_lsb_temp0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_MSB_TEMP0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 101
		self.rx3_i_msb_temp0 = 0
		self.rx3_q_msb_temp0 = 0
		self.rx3_av_msb_temp0 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_msb_temp0 << 0
		val |= self.rx3_q_msb_temp0 << 1
		val |= self.rx3_av_msb_temp0 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_msb_temp0 = (val & 0x01) >> 0
		self.rx3_q_msb_temp0 = (val & 0x02) >> 1
		self.rx3_av_msb_temp0 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_I_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 102
		self.rx3_i_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_Q_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 103
		self.rx3_q_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx3_q_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_q_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_AV_LSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 104
		self.rx3_av_lsb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx3_av_lsb_temp1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_av_lsb_temp1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_MSB_TEMP1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 105
		self.rx3_i_msb_temp1 = 0
		self.rx3_q_msb_temp1 = 0
		self.rx3_av_msb_temp1 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_msb_temp1 << 0
		val |= self.rx3_q_msb_temp1 << 1
		val |= self.rx3_av_msb_temp1 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_msb_temp1 = (val & 0x01) >> 0
		self.rx3_q_msb_temp1 = (val & 0x02) >> 1
		self.rx3_av_msb_temp1 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_I_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 106
		self.rx3_i_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_Q_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 107
		self.rx3_q_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx3_q_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_q_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_AV_LSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 108
		self.rx3_av_lsb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx3_av_lsb_temp2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_av_lsb_temp2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_MSB_TEMP2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 109
		self.rx3_i_msb_temp2 = 0
		self.rx3_q_msb_temp2 = 0
		self.rx3_av_msb_temp2 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_msb_temp2 << 0
		val |= self.rx3_q_msb_temp2 << 1
		val |= self.rx3_av_msb_temp2 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_msb_temp2 = (val & 0x01) >> 0
		self.rx3_q_msb_temp2 = (val & 0x02) >> 1
		self.rx3_av_msb_temp2 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_I_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 110
		self.rx3_i_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_Q_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 111
		self.rx3_q_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx3_q_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_q_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_AV_LSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 112
		self.rx3_av_lsb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx3_av_lsb_temp3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_av_lsb_temp3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX3_MSB_TEMP3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 113
		self.rx3_i_msb_temp3 = 0
		self.rx3_q_msb_temp3 = 0
		self.rx3_av_msb_temp3 = 0
	def write(self):
		val = 0
		val |= self.rx3_i_msb_temp3 << 0
		val |= self.rx3_q_msb_temp3 << 1
		val |= self.rx3_av_msb_temp3 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_i_msb_temp3 = (val & 0x01) >> 0
		self.rx3_q_msb_temp3 = (val & 0x02) >> 1
		self.rx3_av_msb_temp3 = (val & 0x1C) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class PAGE_ID:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 114
		self.page_id = 0
	def write(self):
		val = 0
		val |= self.page_id << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.page_id = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class POWER_DET_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 115
		self.det0_sel = 0
		self.det1_sel = 0
		self.det2_sel = 0
		self.det3_sel = 0
	def write(self):
		val = 0
		val |= self.det0_sel << 0
		val |= self.det1_sel << 2
		val |= self.det2_sel << 4
		val |= self.det3_sel << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.det0_sel = (val & 0x03) >> 0
		self.det1_sel = (val & 0x0C) >> 2
		self.det2_sel = (val & 0x30) >> 4
		self.det3_sel = (val & 0xC0) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 116
		self.DAC_CTRL_PA0 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 117
		self.DAC_CTRL_PA1 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 118
		self.DAC_CTRL_PA2 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 119
		self.DAC_CTRL_PA3 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA0_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 120
		self.DAC_CTRL_PA0_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA0_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA0_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA1_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 121
		self.DAC_CTRL_PA1_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA1_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA1_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA2_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 122
		self.DAC_CTRL_PA2_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA2_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA2_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_PA3_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 123
		self.DAC_CTRL_PA3_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_PA3_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_PA3_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 124
		self.DAC_CTRL_LNA0 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 125
		self.DAC_CTRL_LNA1 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA1 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 126
		self.DAC_CTRL_LNA2 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA2 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 127
		self.DAC_CTRL_LNA3 = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA3 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA0_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 128
		self.DAC_CTRL_LNA0_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA0_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA0_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA1_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 129
		self.DAC_CTRL_LNA1_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA1_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA1_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA2_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 130
		self.DAC_CTRL_LNA2_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA2_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA2_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DAC_CTRL_LNA3_PDN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 131
		self.DAC_CTRL_LNA3_PDN = 0
	def write(self):
		val = 0
		val |= self.DAC_CTRL_LNA3_PDN << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.DAC_CTRL_LNA3_PDN = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_TX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 132
		self.tx0_cmb_icurr_ctrl = 0
		self.tx0_cmb_qcurr_ctrl = 0
		self.tr_clk_delay_ctrl_3_2 = 0
		self.tx0_obs_9_8 = 0
	def write(self):
		val = 0
		val |= self.tx0_cmb_icurr_ctrl << 0
		val |= self.tx0_cmb_qcurr_ctrl << 2
		val |= self.tr_clk_delay_ctrl_3_2 << 4
		val |= self.tx0_obs_9_8 << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.tx0_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.tr_clk_delay_ctrl_3_2 = (val & 0x30) >> 4
		self.tx0_obs_9_8 = (val & 0xC0) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_TX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 133
		self.tx0_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.tx0_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_TX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 134
		self.tx1_cmb_icurr_ctrl = 0
		self.tx1_cmb_qcurr_ctrl = 0
		self.tr_clk_delay_ctrl_1_0 = 0
		self.tx1_obs_9_8 = 0
	def write(self):
		val = 0
		val |= self.tx1_cmb_icurr_ctrl << 0
		val |= self.tx1_cmb_qcurr_ctrl << 2
		val |= self.tr_clk_delay_ctrl_1_0 << 4
		val |= self.tx1_obs_9_8 << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.tx1_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.tr_clk_delay_ctrl_1_0 = (val & 0x30) >> 4
		self.tx1_obs_9_8 = (val & 0xC0) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_TX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 135
		self.tx1_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.tx1_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_TX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 136
		self.tx2_cmb_icurr_ctrl = 0
		self.tx2_cmb_qcurr_ctrl = 0
		self.rsvd4 = 0
		self.tx2_obs_9_8 = 0
	def write(self):
		val = 0
		val |= self.tx2_cmb_icurr_ctrl << 0
		val |= self.tx2_cmb_qcurr_ctrl << 2
		val |= self.rsvd4 << 4
		val |= self.tx2_obs_9_8 << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.tx2_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.rsvd4 = (val & 0x30) >> 4
		self.tx2_obs_9_8 = (val & 0xC0) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_TX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 137
		self.tx2_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.tx2_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_TX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 138
		self.tx3_cmb_icurr_ctrl = 0
		self.tx3_cmb_qcurr_ctrl = 0
		self.rsvd5 = 0
		self.tx3_obs_9_8 = 0
	def write(self):
		val = 0
		val |= self.tx3_cmb_icurr_ctrl << 0
		val |= self.tx3_cmb_qcurr_ctrl << 2
		val |= self.rsvd5 << 4
		val |= self.tx3_obs_9_8 << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.tx3_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.rsvd5 = (val & 0x30) >> 4
		self.tx3_obs_9_8 = (val & 0xC0) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_TX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 139
		self.tx3_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.tx3_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_RX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 140
		self.rx0_cmb_icurr_ctrl = 0
		self.rx0_cmb_qcurr_ctrl = 0
		self.rx0_obs_11_8 = 0
	def write(self):
		val = 0
		val |= self.rx0_cmb_icurr_ctrl << 0
		val |= self.rx0_cmb_qcurr_ctrl << 2
		val |= self.rx0_obs_11_8 << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.rx0_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.rx0_obs_11_8 = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_RX0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 141
		self.rx0_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.rx0_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx0_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_RX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 142
		self.rx1_cmb_icurr_ctrl = 0
		self.rx1_cmb_qcurr_ctrl = 0
		self.rx1_obs_11_8 = 0
	def write(self):
		val = 0
		val |= self.rx1_cmb_icurr_ctrl << 0
		val |= self.rx1_cmb_qcurr_ctrl << 2
		val |= self.rx1_obs_11_8 << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.rx1_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.rx1_obs_11_8 = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_RX1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 143
		self.rx1_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.rx1_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx1_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_RX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 144
		self.rx2_cmb_icurr_ctrl = 0
		self.rx2_cmb_qcurr_ctrl = 0
		self.rx2_obs_11_8 = 0
	def write(self):
		val = 0
		val |= self.rx2_cmb_icurr_ctrl << 0
		val |= self.rx2_cmb_qcurr_ctrl << 2
		val |= self.rx2_obs_11_8 << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.rx2_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.rx2_obs_11_8 = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_RX2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 145
		self.rx2_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.rx2_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx2_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_RX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 146
		self.rx3_cmb_icurr_ctrl = 0
		self.rx3_cmb_qcurr_ctrl = 0
		self.rx3_obs_11_8 = 0
	def write(self):
		val = 0
		val |= self.rx3_cmb_icurr_ctrl << 0
		val |= self.rx3_cmb_qcurr_ctrl << 2
		val |= self.rx3_obs_11_8 << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_cmb_icurr_ctrl = (val & 0x03) >> 0
		self.rx3_cmb_qcurr_ctrl = (val & 0x0C) >> 2
		self.rx3_obs_11_8 = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_RX3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 147
		self.rx3_obs_7_0 = 0
	def write(self):
		val = 0
		val |= self.rx3_obs_7_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx3_obs_7_0 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 148
		self.ext_bias_top_obs = 0
	def write(self):
		val = 0
		val |= self.ext_bias_top_obs << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.ext_bias_top_obs = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 149
		self.ext_bias_neg_sw_polarity = 0
		self.ext_bias_neg_sw_isink = 0
		self.ext_bias_neg_sw_highZ_en = 0
		self.ext_bias_pos_sw_highZ_en = 0
		self.ext_bias_pos_sw_polarity = 0
		self.rsvd6 = 0
	def write(self):
		val = 0
		val |= self.ext_bias_neg_sw_polarity << 0
		val |= self.ext_bias_neg_sw_isink << 1
		val |= self.ext_bias_neg_sw_highZ_en << 2
		val |= self.ext_bias_pos_sw_highZ_en << 3
		val |= self.ext_bias_pos_sw_polarity << 4
		val |= self.rsvd6 << 5
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.ext_bias_neg_sw_polarity = (val & 0x01) >> 0
		self.ext_bias_neg_sw_isink = (val & 0x02) >> 1
		self.ext_bias_neg_sw_highZ_en = (val & 0x04) >> 2
		self.ext_bias_pos_sw_highZ_en = (val & 0x08) >> 3
		self.ext_bias_pos_sw_polarity = (val & 0x10) >> 4
		self.rsvd6 = (val & 0xE0) >> 5
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG2_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 150
		self.pa0_bias_highZ_en = 0
		self.pa1_bias_highZ_en = 0
		self.pa2_bias_highZ_en = 0
		self.pa3_bias_highZ_en = 0
		self.lna0_bias_highZ_en = 0
		self.lna1_bias_highZ_en = 0
		self.lna2_bias_highZ_en = 0
		self.lna3_bias_highZ_en = 0
	def write(self):
		val = 0
		val |= self.pa0_bias_highZ_en << 0
		val |= self.pa1_bias_highZ_en << 1
		val |= self.pa2_bias_highZ_en << 2
		val |= self.pa3_bias_highZ_en << 3
		val |= self.lna0_bias_highZ_en << 4
		val |= self.lna1_bias_highZ_en << 5
		val |= self.lna2_bias_highZ_en << 6
		val |= self.lna3_bias_highZ_en << 7
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.pa0_bias_highZ_en = (val & 0x01) >> 0
		self.pa1_bias_highZ_en = (val & 0x02) >> 1
		self.pa2_bias_highZ_en = (val & 0x04) >> 2
		self.pa3_bias_highZ_en = (val & 0x08) >> 3
		self.lna0_bias_highZ_en = (val & 0x10) >> 4
		self.lna1_bias_highZ_en = (val & 0x20) >> 5
		self.lna2_bias_highZ_en = (val & 0x40) >> 6
		self.lna3_bias_highZ_en = (val & 0x80) >> 7
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG3_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 151
		self.pa0_test_mode_en = 0
		self.pa1_test_mode_en = 0
		self.pa2_test_mode_en = 0
		self.pa3_test_mode_en = 0
		self.lna0_test_mode_en = 0
		self.lna1_test_mode_en = 0
		self.lna2_test_mode_en = 0
		self.lna3_test_mode_en = 0
	def write(self):
		val = 0
		val |= self.pa0_test_mode_en << 0
		val |= self.pa1_test_mode_en << 1
		val |= self.pa2_test_mode_en << 2
		val |= self.pa3_test_mode_en << 3
		val |= self.lna0_test_mode_en << 4
		val |= self.lna1_test_mode_en << 5
		val |= self.lna2_test_mode_en << 6
		val |= self.lna3_test_mode_en << 7
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.pa0_test_mode_en = (val & 0x01) >> 0
		self.pa1_test_mode_en = (val & 0x02) >> 1
		self.pa2_test_mode_en = (val & 0x04) >> 2
		self.pa3_test_mode_en = (val & 0x08) >> 3
		self.lna0_test_mode_en = (val & 0x10) >> 4
		self.lna1_test_mode_en = (val & 0x20) >> 5
		self.lna2_test_mode_en = (val & 0x40) >> 6
		self.lna3_test_mode_en = (val & 0x80) >> 7
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG4_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 152
		self.rsvd7 = 0
	def write(self):
		val = 0
		val |= self.rsvd7 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd7 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG5_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 153
		self.rsvd8 = 0
	def write(self):
		val = 0
		val |= self.rsvd8 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd8 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG6_EXT_BIAS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 154
		self.rsvd9 = 0
	def write(self):
		val = 0
		val |= self.rsvd9 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rsvd9 = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_BGR:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 155
		self.bgr_ptat_amp_ibias_ctrl = 0
		self.bgr_hard_startup_en = 0
		self.bgr_to_adc_ztat_volt_en = 0
		self.bgr_to_adc_ptat_volt_en = 0
		self.rsvd10 = 0
	def write(self):
		val = 0
		val |= self.bgr_ptat_amp_ibias_ctrl << 0
		val |= self.bgr_hard_startup_en << 4
		val |= self.bgr_to_adc_ztat_volt_en << 5
		val |= self.bgr_to_adc_ptat_volt_en << 6
		val |= self.rsvd10 << 7
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.bgr_ptat_amp_ibias_ctrl = (val & 0x0F) >> 0
		self.bgr_hard_startup_en = (val & 0x10) >> 4
		self.bgr_to_adc_ztat_volt_en = (val & 0x20) >> 5
		self.bgr_to_adc_ptat_volt_en = (val & 0x40) >> 6
		self.rsvd10 = (val & 0x80) >> 7
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_ADC:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 156
		self.adc_osc_cap_ctrl = 0
		self.en_pkdet_to_adc_sw = 0
		self.en_temp_sense_to_adc_sw = 0
		self.en_atb_to_adc_sw = 0
		self.en_gp7_to_adc_sw = 0
	def write(self):
		val = 0
		val |= self.adc_osc_cap_ctrl << 0
		val |= self.en_pkdet_to_adc_sw << 4
		val |= self.en_temp_sense_to_adc_sw << 5
		val |= self.en_atb_to_adc_sw << 6
		val |= self.en_gp7_to_adc_sw << 7
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.adc_osc_cap_ctrl = (val & 0x0F) >> 0
		self.en_pkdet_to_adc_sw = (val & 0x10) >> 4
		self.en_temp_sense_to_adc_sw = (val & 0x20) >> 5
		self.en_atb_to_adc_sw = (val & 0x40) >> 6
		self.en_gp7_to_adc_sw = (val & 0x80) >> 7
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_ADC:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 157
		self.en_bypass_clk_for_adc = 0
		self.bypass_clk_for_adc = 0
		self.rsvd11 = 0
	def write(self):
		val = 0
		val |= self.en_bypass_clk_for_adc << 0
		val |= self.bypass_clk_for_adc << 1
		val |= self.rsvd11 << 2
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_bypass_clk_for_adc = (val & 0x01) >> 0
		self.bypass_clk_for_adc = (val & 0x02) >> 1
		self.rsvd11 = (val & 0xFC) >> 2
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class ADC_CTRL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 158
		self.en_adc_osc = 0
		self.en_adc = 0
	def write(self):
		val = 0
		val |= self.en_adc_osc << 0
		val |= self.en_adc << 1
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_adc_osc = (val & 0x01) >> 0
		self.en_adc = (val & 0x02) >> 1
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class ADC_STS:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 159
		self.eoc = 0
	def write(self):
		val = 0
		val |= self.eoc << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.eoc = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG0_SPARE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 160
		self.ch0_tx_obs_13_10 = 0
		self.ch1_tx_obs_13_10 = 0
	def write(self):
		val = 0
		val |= self.ch0_tx_obs_13_10 << 0
		val |= self.ch1_tx_obs_13_10 << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.ch0_tx_obs_13_10 = (val & 0x0F) >> 0
		self.ch1_tx_obs_13_10 = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG1_SPARE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 161
		self.ch2_tx_obs_13_10 = 0
		self.ch3_tx_obs_13_10 = 0
	def write(self):
		val = 0
		val |= self.ch2_tx_obs_13_10 << 0
		val |= self.ch3_tx_obs_13_10 << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.ch2_tx_obs_13_10 = (val & 0x0F) >> 0
		self.ch3_tx_obs_13_10 = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG2_SPARE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 162
		self.txlna_curr_ctrl = 0
		self.txlna_obs = 0
		self.low_pdn_curr_tx = 0
		self.low_pdn_curr_rx = 0
		self.low_pdn_curr_temp_sns = 0
	def write(self):
		val = 0
		val |= self.txlna_curr_ctrl << 0
		val |= self.txlna_obs << 2
		val |= self.low_pdn_curr_tx << 5
		val |= self.low_pdn_curr_rx << 6
		val |= self.low_pdn_curr_temp_sns << 7
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.txlna_curr_ctrl = (val & 0x03) >> 0
		self.txlna_obs = (val & 0x1C) >> 2
		self.low_pdn_curr_tx = (val & 0x20) >> 5
		self.low_pdn_curr_rx = (val & 0x40) >> 6
		self.low_pdn_curr_temp_sns = (val & 0x80) >> 7
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class REG3_SPARE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 163
		self.pk_det_obs = 0
		self.temp_sense_obs = 0
		self.temp_sense_adc_obs = 0
		self.rsvd12 = 0
	def write(self):
		val = 0
		val |= self.pk_det_obs << 0
		val |= self.temp_sense_obs << 4
		val |= self.temp_sense_adc_obs << 5
		val |= self.rsvd12 << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.pk_det_obs = (val & 0x0F) >> 0
		self.temp_sense_obs = (val & 0x10) >> 4
		self.temp_sense_adc_obs = (val & 0x20) >> 5
		self.rsvd12 = (val & 0xC0) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CTRL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 164
		self.RX_en_force = 0
		self.RX_en_force_val = 0
	def write(self):
		val = 0
		val |= self.RX_en_force << 0
		val |= self.RX_en_force_val << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.RX_en_force = (val & 0x0F) >> 0
		self.RX_en_force_val = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CTRL_1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 165
		self.TX_en_force = 0
		self.TX_en_force_val = 0
	def write(self):
		val = 0
		val |= self.TX_en_force << 0
		val |= self.TX_en_force_val << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX_en_force = (val & 0x0F) >> 0
		self.TX_en_force_val = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CTRL_2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 166
		self.det_en_force = 0
		self.det_en_force_val = 0
	def write(self):
		val = 0
		val |= self.det_en_force << 0
		val |= self.det_en_force_val << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.det_en_force = (val & 0x0F) >> 0
		self.det_en_force_val = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CTRL_3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 167
		self.en_lna_force = 0
		self.en_lna_force_val = 0
	def write(self):
		val = 0
		val |= self.en_lna_force << 0
		val |= self.en_lna_force_val << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_lna_force = (val & 0x0F) >> 0
		self.en_lna_force_val = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CTRL_4:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 168
		self.en_pa_force = 0
		self.en_pa_force_val = 0
	def write(self):
		val = 0
		val |= self.en_pa_force << 0
		val |= self.en_pa_force_val << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_pa_force = (val & 0x0F) >> 0
		self.en_pa_force_val = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CTRL_5:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 169
		self.en_pos_sw_force = 0
		self.en_pos_sw_force_val = 0
		self.TX_lna_en_force = 0
		self.TX_lna_en_force_val = 0
		self.en_neg_sw_force = 0
		self.en_neg_sw_force_val = 0
		self.en_pol = 0
	def write(self):
		val = 0
		val |= self.en_pos_sw_force << 0
		val |= self.en_pos_sw_force_val << 1
		val |= self.TX_lna_en_force << 2
		val |= self.TX_lna_en_force_val << 3
		val |= self.en_neg_sw_force << 4
		val |= self.en_neg_sw_force_val << 5
		val |= self.en_pol << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_pos_sw_force = (val & 0x01) >> 0
		self.en_pos_sw_force_val = (val & 0x02) >> 1
		self.TX_lna_en_force = (val & 0x04) >> 2
		self.TX_lna_en_force_val = (val & 0x08) >> 3
		self.en_neg_sw_force = (val & 0x10) >> 4
		self.en_neg_sw_force_val = (val & 0x20) >> 5
		self.en_pol = (val & 0x40) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_MASK:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 170
		self.tx_mask = 0
		self.rx_mask = 0
	def write(self):
		val = 0
		val |= self.tx_mask << 0
		val |= self.rx_mask << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_mask = (val & 0x0F) >> 0
		self.rx_mask = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_SW_CTRL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 171
		self.tr_reg = 0
	def write(self):
		val = 0
		val |= self.tr_reg << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tr_reg = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TR_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 172
		self.tr_mode_sel = 0
		self.data_path_en = 0
	def write(self):
		val = 0
		val |= self.tr_mode_sel << 0
		val |= self.data_path_en << 1
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tr_mode_sel = (val & 0x01) >> 0
		self.data_path_en = (val & 0x02) >> 1
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_BEAM_START_ADDR:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 173
		self.tx_beam_start_addr = 0
	def write(self):
		val = 0
		val |= self.tx_beam_start_addr << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_beam_start_addr = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_BEAM_STOP_ADDR:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 174
		self.tx_beam_stop_addr = 0
	def write(self):
		val = 0
		val |= self.tx_beam_stop_addr << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_beam_stop_addr = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX_BEAM_START_ADDR:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 175
		self.rx_beam_start_addr = 0
	def write(self):
		val = 0
		val |= self.rx_beam_start_addr << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx_beam_start_addr = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class RX_BEAM_STOP_ADDR:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 176
		self.rx_beam_stop_addr = 0
	def write(self):
		val = 0
		val |= self.rx_beam_stop_addr << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.rx_beam_stop_addr = (val & 0x7F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_GAIN_FORCE:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 177
		self.tx0_final_gain_force = 0
		self.tx1_final_gain_force = 0
		self.tx2_final_gain_force = 0
		self.tx3_final_gain_force = 0
		self.tx0_gain_force = 0
		self.tx1_gain_force = 0
		self.tx2_gain_force = 0
		self.tx3_gain_force = 0
	def write(self):
		val = 0
		val |= self.tx0_final_gain_force << 0
		val |= self.tx1_final_gain_force << 1
		val |= self.tx2_final_gain_force << 2
		val |= self.tx3_final_gain_force << 3
		val |= self.tx0_gain_force << 4
		val |= self.tx1_gain_force << 5
		val |= self.tx2_gain_force << 6
		val |= self.tx3_gain_force << 7
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_final_gain_force = (val & 0x01) >> 0
		self.tx1_final_gain_force = (val & 0x02) >> 1
		self.tx2_final_gain_force = (val & 0x04) >> 2
		self.tx3_final_gain_force = (val & 0x08) >> 3
		self.tx0_gain_force = (val & 0x10) >> 4
		self.tx1_gain_force = (val & 0x20) >> 5
		self.tx2_gain_force = (val & 0x40) >> 6
		self.tx3_gain_force = (val & 0x80) >> 7
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_FINAL_GAIN_FORCE_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 178
		self.tx0_final_gain_force_val = 0
	def write(self):
		val = 0
		val |= self.tx0_final_gain_force_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_final_gain_force_val = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_FINAL_GAIN_FORCE_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 179
		self.tx1_final_gain_force_val = 0
	def write(self):
		val = 0
		val |= self.tx1_final_gain_force_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_final_gain_force_val = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_FINAL_GAIN_FORCE_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 180
		self.tx2_final_gain_force_val = 0
	def write(self):
		val = 0
		val |= self.tx2_final_gain_force_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_final_gain_force_val = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_FINAL_GAIN_FORCE_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 181
		self.tx3_final_gain_force_val = 0
	def write(self):
		val = 0
		val |= self.tx3_final_gain_force_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_final_gain_force_val = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_GAIN_FORCE_LSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 182
		self.tx0_gain_force_lsb_val = 0
	def write(self):
		val = 0
		val |= self.tx0_gain_force_lsb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_gain_force_lsb_val = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_GAIN_FORCE_MSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 183
		self.tx0_gain_force_msb_val = 0
	def write(self):
		val = 0
		val |= self.tx0_gain_force_msb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx0_gain_force_msb_val = (val & 0x07) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_GAIN_FORCE_LSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 184
		self.tx1_gain_force_lsb_val = 0
	def write(self):
		val = 0
		val |= self.tx1_gain_force_lsb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_gain_force_lsb_val = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX1_GAIN_FORCE_MSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 185
		self.tx1_gain_force_msb_val = 0
	def write(self):
		val = 0
		val |= self.tx1_gain_force_msb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx1_gain_force_msb_val = (val & 0x07) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_GAIN_FORCE_LSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 186
		self.tx2_gain_force_lsb_val = 0
	def write(self):
		val = 0
		val |= self.tx2_gain_force_lsb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_gain_force_lsb_val = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX2_GAIN_FORCE_MSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 187
		self.tx2_gain_force_msb_val = 0
	def write(self):
		val = 0
		val |= self.tx2_gain_force_msb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx2_gain_force_msb_val = (val & 0x07) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_GAIN_FORCE_LSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 188
		self.tx3_gain_force_lsb_val = 0
	def write(self):
		val = 0
		val |= self.tx3_gain_force_lsb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_gain_force_lsb_val = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX3_GAIN_FORCE_MSB_VAL:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 189
		self.tx3_gain_force_msb_val = 0
	def write(self):
		val = 0
		val |= self.tx3_gain_force_msb_val << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx3_gain_force_msb_val = (val & 0x07) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_GAIN_CORR_COEF_0:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 190
		self.tx_gain_corr_coef_0 = 0
	def write(self):
		val = 0
		val |= self.tx_gain_corr_coef_0 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_gain_corr_coef_0 = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_GAIN_CORR_COEF_1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 191
		self.tx_gain_corr_coef_1 = 0
	def write(self):
		val = 0
		val |= self.tx_gain_corr_coef_1 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_gain_corr_coef_1 = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_GAIN_CORR_COEF_2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 192
		self.tx_gain_corr_coef_2 = 0
	def write(self):
		val = 0
		val |= self.tx_gain_corr_coef_2 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_gain_corr_coef_2 = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_GAIN_CORR_COEF_3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 193
		self.tx_gain_corr_coef_3 = 0
	def write(self):
		val = 0
		val |= self.tx_gain_corr_coef_3 << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.tx_gain_corr_coef_3 = (val & 0x1F) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DET_0_1_ADC_OUT_BIN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 194
		self.det0_adc_out_bin = 0
		self.det1_adc_out_bin = 0
	def write(self):
		val = 0
		val |= self.det0_adc_out_bin << 0
		val |= self.det1_adc_out_bin << 3
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.det0_adc_out_bin = (val & 0x07) >> 0
		self.det1_adc_out_bin = (val & 0x38) >> 3
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class DET_2_3_ADC_OUT_BIN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 195
		self.det2_adc_out_bin = 0
		self.det3_adc_out_bin = 0
	def write(self):
		val = 0
		val |= self.det2_adc_out_bin << 0
		val |= self.det3_adc_out_bin << 3
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.det2_adc_out_bin = (val & 0x07) >> 0
		self.det3_adc_out_bin = (val & 0x38) >> 3
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class SPARE_ADC_TEMP_ADC_OUT_BIN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 196
		self.spare_adc_out_bin = 0
		self.temp_adc_out_bin = 0
	def write(self):
		val = 0
		val |= self.spare_adc_out_bin << 0
		val |= self.temp_adc_out_bin << 3
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.spare_adc_out_bin = (val & 0x07) >> 0
		self.temp_adc_out_bin = (val & 0x78) >> 3
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TEMP_CORR_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 197
		self.force_ana_temp = 0
		self.force_ana_temp_val = 0
		self.en_rx_temp_corr = 0
		self.en_tx_temp_corr = 0
	def write(self):
		val = 0
		val |= self.force_ana_temp << 0
		val |= self.force_ana_temp_val << 1
		val |= self.en_rx_temp_corr << 3
		val |= self.en_tx_temp_corr << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.force_ana_temp = (val & 0x01) >> 0
		self.force_ana_temp_val = (val & 0x06) >> 1
		self.en_rx_temp_corr = (val & 0x08) >> 3
		self.en_tx_temp_corr = (val & 0x10) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX_LNA_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 198
		self.TX_lna_gain_ctrl = 0
	def write(self):
		val = 0
		val |= self.TX_lna_gain_ctrl << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX_lna_gain_ctrl = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TEMP_IN_BIN:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 199
		self.temp_in_bin = 0
	def write(self):
		val = 0
		val |= self.temp_in_bin << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.temp_in_bin = (val & 0x03) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class SPI_CFG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 200
		self.force_sdio_to_z = 0
		self.force_sdo_to_z = 0
	def write(self):
		val = 0
		val |= self.force_sdio_to_z << 0
		val |= self.force_sdo_to_z << 1
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.force_sdio_to_z = (val & 0x01) >> 0
		self.force_sdo_to_z = (val & 0x02) >> 1
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class ADC_IN_LSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 201
		self.adc_in_lsb = 0
	def write(self):
		val = 0
		val |= self.adc_in_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.adc_in_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class ADC_IN_MSB:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 202
		self.adc_in_msb = 0
	def write(self):
		val = 0
		val |= self.adc_in_msb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.adc_in_msb = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class SYNC_RST:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 203
		self.sync_rst = 0
	def write(self):
		val = 0
		val |= self.sync_rst << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.sync_rst = (val & 0x01) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_STS_REG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 204
		self.TX0_iphase_ctrl = 0
	def write(self):
		val = 0
		val |= self.TX0_iphase_ctrl << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX0_iphase_ctrl = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_STS_REG_1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 205
		self.TX0_qphase_ctrl = 0
	def write(self):
		val = 0
		val |= self.TX0_qphase_ctrl << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX0_qphase_ctrl = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_STS_REG_2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 206
		self.TX0_sign_i = 0
		self.TX0_sign_q = 0
	def write(self):
		val = 0
		val |= self.TX0_sign_i << 0
		val |= self.TX0_sign_q << 1
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX0_sign_i = (val & 0x01) >> 0
		self.TX0_sign_q = (val & 0x02) >> 1
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_STS_REG_3:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 207
		self.TX0_gain_ctrl_lsb = 0
	def write(self):
		val = 0
		val |= self.TX0_gain_ctrl_lsb << 0
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX0_gain_ctrl_lsb = (val & 0xFF) >> 0
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class TX0_STS_REG_4:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 208
		self.TX0_gain_ctrl_msb = 0
		self.TX0_final_gain_ctrl = 0
	def write(self):
		val = 0
		val |= self.TX0_gain_ctrl_msb << 0
		val |= self.TX0_final_gain_ctrl << 3
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX0_gain_ctrl_msb = (val & 0x07) >> 0
		self.TX0_final_gain_ctrl = (val & 0xF8) >> 3
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class EXT_CTRL_STS_REG:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 209
		self.TX_en = 0
		self.RX_en = 0
	def write(self):
		val = 0
		val |= self.TX_en << 0
		val |= self.RX_en << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.TX_en = (val & 0x0F) >> 0
		self.RX_en = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class EXT_CTRL_STS_REG_1:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 210
		self.en_lna = 0
		self.en_pa = 0
	def write(self):
		val = 0
		val |= self.en_lna << 0
		val |= self.en_pa << 4
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_lna = (val & 0x0F) >> 0
		self.en_pa = (val & 0xF0) >> 4
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class EXT_CTRL_STS_REG_2:
	def __init__(self,dev, slv_addr, bdst):
		self.dev = dev
		self.slv_addr = slv_addr
		self.bdst = bdst
		self._addr = 211
		self.en_neg_sw = 0
		self.en_pos_sw = 0
		self.TX_lna_en = 0
		self.det0_en = 0
		self.det1_en = 0
		self.det2_en = 0
		self.det3_en = 0
	def write(self):
		val = 0
		val |= self.en_neg_sw << 0
		val |= self.en_pos_sw << 1
		val |= self.TX_lna_en << 2
		val |= self.det0_en << 3
		val |= self.det1_en << 4
		val |= self.det2_en << 5
		val |= self.det3_en << 6
		self.dev.write(self._addr,val, self.slv_addr, self.bdst)
	def read(self):
		val = self.dev.read(self._addr, self.slv_addr)
		self.en_neg_sw = (val & 0x01) >> 0
		self.en_pos_sw = (val & 0x02) >> 1
		self.TX_lna_en = (val & 0x04) >> 2
		self.det0_en = (val & 0x08) >> 3
		self.det1_en = (val & 0x10) >> 4
		self.det2_en = (val & 0x20) >> 5
		self.det3_en = (val & 0x40) >> 6
		return val
	def display(self):
		for name, value in vars(self).items():
			if name not in ['_addr', 'dev']:
				if isinstance(value, int):
					print(f'{name} = {hex(value)}')
				else:
					print(f'{name} = {value}')

class ORION_8G_12G:
	def __init__(self,dev, slv_addr = None, bdst = None):
		self.DEVICE_ID = DEVICE_ID(dev, slv_addr, bdst)
		self.REVISION = REVISION(dev, slv_addr, bdst)
		self.PHASE_CODE_TX0 = PHASE_CODE_TX0(dev, slv_addr, bdst)
		self.GAIN_CODE_TX0 = GAIN_CODE_TX0(dev, slv_addr, bdst)
		self.PHASE_CODE_TX1 = PHASE_CODE_TX1(dev, slv_addr, bdst)
		self.GAIN_CODE_TX1 = GAIN_CODE_TX1(dev, slv_addr, bdst)
		self.PHASE_CODE_TX2 = PHASE_CODE_TX2(dev, slv_addr, bdst)
		self.GAIN_CODE_TX2 = GAIN_CODE_TX2(dev, slv_addr, bdst)
		self.PHASE_CODE_TX3 = PHASE_CODE_TX3(dev, slv_addr, bdst)
		self.GAIN_CODE_TX3 = GAIN_CODE_TX3(dev, slv_addr, bdst)
		self.PHASE_CODE_RX0 = PHASE_CODE_RX0(dev, slv_addr, bdst)
		self.GAIN_CODE_RX0 = GAIN_CODE_RX0(dev, slv_addr, bdst)
		self.PHASE_CODE_RX1 = PHASE_CODE_RX1(dev, slv_addr, bdst)
		self.GAIN_CODE_RX1 = GAIN_CODE_RX1(dev, slv_addr, bdst)
		self.PHASE_CODE_RX2 = PHASE_CODE_RX2(dev, slv_addr, bdst)
		self.GAIN_CODE_RX2 = GAIN_CODE_RX2(dev, slv_addr, bdst)
		self.PHASE_CODE_RX3 = PHASE_CODE_RX3(dev, slv_addr, bdst)
		self.GAIN_CODE_RX3 = GAIN_CODE_RX3(dev, slv_addr, bdst)
		self.UPDATE_CODE = UPDATE_CODE(dev, slv_addr, bdst)
		self.RSVD0 = RSVD0(dev, slv_addr, bdst)
		self.BEAM_CODE = BEAM_CODE(dev, slv_addr, bdst)
		self.RSVD1 = RSVD1(dev, slv_addr, bdst)
		self.BEAM_CFG = BEAM_CFG(dev, slv_addr, bdst)
		self.STG2_CFG = STG2_CFG(dev, slv_addr, bdst)
		self.FREQ_ID = FREQ_ID(dev, slv_addr, bdst)
		self.RSVD2 = RSVD2(dev, slv_addr, bdst)
		self.RSVD3 = RSVD3(dev, slv_addr, bdst)
		self.CORR_CFG = CORR_CFG(dev, slv_addr, bdst)
		self.COPY_MODE = COPY_MODE(dev, slv_addr, bdst)
		self.SPI_MODE_CTRL = SPI_MODE_CTRL(dev, slv_addr, bdst)
		self.TX0_I_LSB = TX0_I_LSB(dev, slv_addr, bdst)
		self.TX0_Q_LSB = TX0_Q_LSB(dev, slv_addr, bdst)
		self.TX0_AV_LSB = TX0_AV_LSB(dev, slv_addr, bdst)
		self.TX0_MSB = TX0_MSB(dev, slv_addr, bdst)
		self.TX0_FINAL_AV = TX0_FINAL_AV(dev, slv_addr, bdst)
		self.RX0_I_LSB_TEMP0 = RX0_I_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX0_Q_LSB_TEMP0 = RX0_Q_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX0_AV_LSB_TEMP0 = RX0_AV_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX0_MSB_TEMP0 = RX0_MSB_TEMP0(dev, slv_addr, bdst)
		self.RX0_I_LSB_TEMP1 = RX0_I_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX0_Q_LSB_TEMP1 = RX0_Q_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX0_AV_LSB_TEMP1 = RX0_AV_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX0_MSB_TEMP1 = RX0_MSB_TEMP1(dev, slv_addr, bdst)
		self.RX0_I_LSB_TEMP2 = RX0_I_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX0_Q_LSB_TEMP2 = RX0_Q_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX0_AV_LSB_TEMP2 = RX0_AV_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX0_MSB_TEMP2 = RX0_MSB_TEMP2(dev, slv_addr, bdst)
		self.RX0_I_LSB_TEMP3 = RX0_I_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX0_Q_LSB_TEMP3 = RX0_Q_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX0_AV_LSB_TEMP3 = RX0_AV_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX0_MSB_TEMP3 = RX0_MSB_TEMP3(dev, slv_addr, bdst)
		self.TX1_I_LSB = TX1_I_LSB(dev, slv_addr, bdst)
		self.TX1_Q_LSB = TX1_Q_LSB(dev, slv_addr, bdst)
		self.TX1_AV_LSB = TX1_AV_LSB(dev, slv_addr, bdst)
		self.TX1_MSB = TX1_MSB(dev, slv_addr, bdst)
		self.TX1_FINAL_AV = TX1_FINAL_AV(dev, slv_addr, bdst)
		self.RX1_I_LSB_TEMP0 = RX1_I_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX1_Q_LSB_TEMP0 = RX1_Q_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX1_AV_LSB_TEMP0 = RX1_AV_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX1_MSB_TEMP0 = RX1_MSB_TEMP0(dev, slv_addr, bdst)
		self.RX1_I_LSB_TEMP1 = RX1_I_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX1_Q_LSB_TEMP1 = RX1_Q_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX1_AV_LSB_TEMP1 = RX1_AV_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX1_MSB_TEMP1 = RX1_MSB_TEMP1(dev, slv_addr, bdst)
		self.RX1_I_LSB_TEMP2 = RX1_I_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX1_Q_LSB_TEMP2 = RX1_Q_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX1_AV_LSB_TEMP2 = RX1_AV_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX1_MSB_TEMP2 = RX1_MSB_TEMP2(dev, slv_addr, bdst)
		self.RX1_I_LSB_TEMP3 = RX1_I_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX1_Q_LSB_TEMP3 = RX1_Q_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX1_AV_LSB_TEMP3 = RX1_AV_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX1_MSB_TEMP3 = RX1_MSB_TEMP3(dev, slv_addr, bdst)
		self.TX2_I_LSB = TX2_I_LSB(dev, slv_addr, bdst)
		self.TX2_Q_LSB = TX2_Q_LSB(dev, slv_addr, bdst)
		self.TX2_AV_LSB = TX2_AV_LSB(dev, slv_addr, bdst)
		self.TX2_MSB = TX2_MSB(dev, slv_addr, bdst)
		self.TX2_FINAL_AV = TX2_FINAL_AV(dev, slv_addr, bdst)
		self.RX2_I_LSB_TEMP0 = RX2_I_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX2_Q_LSB_TEMP0 = RX2_Q_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX2_AV_LSB_TEMP0 = RX2_AV_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX2_MSB_TEMP0 = RX2_MSB_TEMP0(dev, slv_addr, bdst)
		self.RX2_I_LSB_TEMP1 = RX2_I_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX2_Q_LSB_TEMP1 = RX2_Q_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX2_AV_LSB_TEMP1 = RX2_AV_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX2_MSB_TEMP1 = RX2_MSB_TEMP1(dev, slv_addr, bdst)
		self.RX2_I_LSB_TEMP2 = RX2_I_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX2_Q_LSB_TEMP2 = RX2_Q_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX2_AV_LSB_TEMP2 = RX2_AV_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX2_MSB_TEMP2 = RX2_MSB_TEMP2(dev, slv_addr, bdst)
		self.RX2_I_LSB_TEMP3 = RX2_I_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX2_Q_LSB_TEMP3 = RX2_Q_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX2_AV_LSB_TEMP3 = RX2_AV_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX2_MSB_TEMP3 = RX2_MSB_TEMP3(dev, slv_addr, bdst)
		self.TX3_I_LSB = TX3_I_LSB(dev, slv_addr, bdst)
		self.TX3_Q_LSB = TX3_Q_LSB(dev, slv_addr, bdst)
		self.TX3_AV_LSB = TX3_AV_LSB(dev, slv_addr, bdst)
		self.TX3_MSB = TX3_MSB(dev, slv_addr, bdst)
		self.TX3_FINAL_AV = TX3_FINAL_AV(dev, slv_addr, bdst)
		self.RX3_I_LSB_TEMP0 = RX3_I_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX3_Q_LSB_TEMP0 = RX3_Q_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX3_AV_LSB_TEMP0 = RX3_AV_LSB_TEMP0(dev, slv_addr, bdst)
		self.RX3_MSB_TEMP0 = RX3_MSB_TEMP0(dev, slv_addr, bdst)
		self.RX3_I_LSB_TEMP1 = RX3_I_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX3_Q_LSB_TEMP1 = RX3_Q_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX3_AV_LSB_TEMP1 = RX3_AV_LSB_TEMP1(dev, slv_addr, bdst)
		self.RX3_MSB_TEMP1 = RX3_MSB_TEMP1(dev, slv_addr, bdst)
		self.RX3_I_LSB_TEMP2 = RX3_I_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX3_Q_LSB_TEMP2 = RX3_Q_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX3_AV_LSB_TEMP2 = RX3_AV_LSB_TEMP2(dev, slv_addr, bdst)
		self.RX3_MSB_TEMP2 = RX3_MSB_TEMP2(dev, slv_addr, bdst)
		self.RX3_I_LSB_TEMP3 = RX3_I_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX3_Q_LSB_TEMP3 = RX3_Q_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX3_AV_LSB_TEMP3 = RX3_AV_LSB_TEMP3(dev, slv_addr, bdst)
		self.RX3_MSB_TEMP3 = RX3_MSB_TEMP3(dev, slv_addr, bdst)
		self.PAGE_ID = PAGE_ID(dev, slv_addr, bdst)
		self.POWER_DET_CFG = POWER_DET_CFG(dev, slv_addr, bdst)
		self.DAC_CTRL_PA0 = DAC_CTRL_PA0(dev, slv_addr, bdst)
		self.DAC_CTRL_PA1 = DAC_CTRL_PA1(dev, slv_addr, bdst)
		self.DAC_CTRL_PA2 = DAC_CTRL_PA2(dev, slv_addr, bdst)
		self.DAC_CTRL_PA3 = DAC_CTRL_PA3(dev, slv_addr, bdst)
		self.DAC_CTRL_PA0_PDN = DAC_CTRL_PA0_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_PA1_PDN = DAC_CTRL_PA1_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_PA2_PDN = DAC_CTRL_PA2_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_PA3_PDN = DAC_CTRL_PA3_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA0 = DAC_CTRL_LNA0(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA1 = DAC_CTRL_LNA1(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA2 = DAC_CTRL_LNA2(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA3 = DAC_CTRL_LNA3(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA0_PDN = DAC_CTRL_LNA0_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA1_PDN = DAC_CTRL_LNA1_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA2_PDN = DAC_CTRL_LNA2_PDN(dev, slv_addr, bdst)
		self.DAC_CTRL_LNA3_PDN = DAC_CTRL_LNA3_PDN(dev, slv_addr, bdst)
		self.REG0_TX0 = REG0_TX0(dev, slv_addr, bdst)
		self.REG1_TX0 = REG1_TX0(dev, slv_addr, bdst)
		self.REG0_TX1 = REG0_TX1(dev, slv_addr, bdst)
		self.REG1_TX1 = REG1_TX1(dev, slv_addr, bdst)
		self.REG0_TX2 = REG0_TX2(dev, slv_addr, bdst)
		self.REG1_TX2 = REG1_TX2(dev, slv_addr, bdst)
		self.REG0_TX3 = REG0_TX3(dev, slv_addr, bdst)
		self.REG1_TX3 = REG1_TX3(dev, slv_addr, bdst)
		self.REG0_RX0 = REG0_RX0(dev, slv_addr, bdst)
		self.REG1_RX0 = REG1_RX0(dev, slv_addr, bdst)
		self.REG0_RX1 = REG0_RX1(dev, slv_addr, bdst)
		self.REG1_RX1 = REG1_RX1(dev, slv_addr, bdst)
		self.REG0_RX2 = REG0_RX2(dev, slv_addr, bdst)
		self.REG1_RX2 = REG1_RX2(dev, slv_addr, bdst)
		self.REG0_RX3 = REG0_RX3(dev, slv_addr, bdst)
		self.REG1_RX3 = REG1_RX3(dev, slv_addr, bdst)
		self.REG0_EXT_BIAS = REG0_EXT_BIAS(dev, slv_addr, bdst)
		self.REG1_EXT_BIAS = REG1_EXT_BIAS(dev, slv_addr, bdst)
		self.REG2_EXT_BIAS = REG2_EXT_BIAS(dev, slv_addr, bdst)
		self.REG3_EXT_BIAS = REG3_EXT_BIAS(dev, slv_addr, bdst)
		self.REG4_EXT_BIAS = REG4_EXT_BIAS(dev, slv_addr, bdst)
		self.REG5_EXT_BIAS = REG5_EXT_BIAS(dev, slv_addr, bdst)
		self.REG6_EXT_BIAS = REG6_EXT_BIAS(dev, slv_addr, bdst)
		self.REG0_BGR = REG0_BGR(dev, slv_addr, bdst)
		self.REG0_ADC = REG0_ADC(dev, slv_addr, bdst)
		self.REG1_ADC = REG1_ADC(dev, slv_addr, bdst)
		self.ADC_CTRL = ADC_CTRL(dev, slv_addr, bdst)
		self.ADC_STS = ADC_STS(dev, slv_addr, bdst)
		self.REG0_SPARE = REG0_SPARE(dev, slv_addr, bdst)
		self.REG1_SPARE = REG1_SPARE(dev, slv_addr, bdst)
		self.REG2_SPARE = REG2_SPARE(dev, slv_addr, bdst)
		self.REG3_SPARE = REG3_SPARE(dev, slv_addr, bdst)
		self.TR_CTRL = TR_CTRL(dev, slv_addr, bdst)
		self.TR_CTRL_1 = TR_CTRL_1(dev, slv_addr, bdst)
		self.TR_CTRL_2 = TR_CTRL_2(dev, slv_addr, bdst)
		self.TR_CTRL_3 = TR_CTRL_3(dev, slv_addr, bdst)
		self.TR_CTRL_4 = TR_CTRL_4(dev, slv_addr, bdst)
		self.TR_CTRL_5 = TR_CTRL_5(dev, slv_addr, bdst)
		self.TR_MASK = TR_MASK(dev, slv_addr, bdst)
		self.TR_SW_CTRL = TR_SW_CTRL(dev, slv_addr, bdst)
		self.TR_CFG = TR_CFG(dev, slv_addr, bdst)
		self.TX_BEAM_START_ADDR = TX_BEAM_START_ADDR(dev, slv_addr, bdst)
		self.TX_BEAM_STOP_ADDR = TX_BEAM_STOP_ADDR(dev, slv_addr, bdst)
		self.RX_BEAM_START_ADDR = RX_BEAM_START_ADDR(dev, slv_addr, bdst)
		self.RX_BEAM_STOP_ADDR = RX_BEAM_STOP_ADDR(dev, slv_addr, bdst)
		self.TX_GAIN_FORCE = TX_GAIN_FORCE(dev, slv_addr, bdst)
		self.TX0_FINAL_GAIN_FORCE_VAL = TX0_FINAL_GAIN_FORCE_VAL(dev, slv_addr, bdst)
		self.TX1_FINAL_GAIN_FORCE_VAL = TX1_FINAL_GAIN_FORCE_VAL(dev, slv_addr, bdst)
		self.TX2_FINAL_GAIN_FORCE_VAL = TX2_FINAL_GAIN_FORCE_VAL(dev, slv_addr, bdst)
		self.TX3_FINAL_GAIN_FORCE_VAL = TX3_FINAL_GAIN_FORCE_VAL(dev, slv_addr, bdst)
		self.TX0_GAIN_FORCE_LSB_VAL = TX0_GAIN_FORCE_LSB_VAL(dev, slv_addr, bdst)
		self.TX0_GAIN_FORCE_MSB_VAL = TX0_GAIN_FORCE_MSB_VAL(dev, slv_addr, bdst)
		self.TX1_GAIN_FORCE_LSB_VAL = TX1_GAIN_FORCE_LSB_VAL(dev, slv_addr, bdst)
		self.TX1_GAIN_FORCE_MSB_VAL = TX1_GAIN_FORCE_MSB_VAL(dev, slv_addr, bdst)
		self.TX2_GAIN_FORCE_LSB_VAL = TX2_GAIN_FORCE_LSB_VAL(dev, slv_addr, bdst)
		self.TX2_GAIN_FORCE_MSB_VAL = TX2_GAIN_FORCE_MSB_VAL(dev, slv_addr, bdst)
		self.TX3_GAIN_FORCE_LSB_VAL = TX3_GAIN_FORCE_LSB_VAL(dev, slv_addr, bdst)
		self.TX3_GAIN_FORCE_MSB_VAL = TX3_GAIN_FORCE_MSB_VAL(dev, slv_addr, bdst)
		self.TX_GAIN_CORR_COEF_0 = TX_GAIN_CORR_COEF_0(dev, slv_addr, bdst)
		self.TX_GAIN_CORR_COEF_1 = TX_GAIN_CORR_COEF_1(dev, slv_addr, bdst)
		self.TX_GAIN_CORR_COEF_2 = TX_GAIN_CORR_COEF_2(dev, slv_addr, bdst)
		self.TX_GAIN_CORR_COEF_3 = TX_GAIN_CORR_COEF_3(dev, slv_addr, bdst)
		self.DET_0_1_ADC_OUT_BIN = DET_0_1_ADC_OUT_BIN(dev, slv_addr, bdst)
		self.DET_2_3_ADC_OUT_BIN = DET_2_3_ADC_OUT_BIN(dev, slv_addr, bdst)
		self.SPARE_ADC_TEMP_ADC_OUT_BIN = SPARE_ADC_TEMP_ADC_OUT_BIN(dev, slv_addr, bdst)
		self.TEMP_CORR_CFG = TEMP_CORR_CFG(dev, slv_addr, bdst)
		self.TX_LNA_CFG = TX_LNA_CFG(dev, slv_addr, bdst)
		self.TEMP_IN_BIN = TEMP_IN_BIN(dev, slv_addr, bdst)
		self.SPI_CFG = SPI_CFG(dev, slv_addr, bdst)
		self.ADC_IN_LSB = ADC_IN_LSB(dev, slv_addr, bdst)
		self.ADC_IN_MSB = ADC_IN_MSB(dev, slv_addr, bdst)
		self.SYNC_RST = SYNC_RST(dev, slv_addr, bdst)
		self.TX0_STS_REG = TX0_STS_REG(dev, slv_addr, bdst)
		self.TX0_STS_REG_1 = TX0_STS_REG_1(dev, slv_addr, bdst)
		self.TX0_STS_REG_2 = TX0_STS_REG_2(dev, slv_addr, bdst)
		self.TX0_STS_REG_3 = TX0_STS_REG_3(dev, slv_addr, bdst)
		self.TX0_STS_REG_4 = TX0_STS_REG_4(dev, slv_addr, bdst)
		self.EXT_CTRL_STS_REG = EXT_CTRL_STS_REG(dev, slv_addr, bdst)
		self.EXT_CTRL_STS_REG_1 = EXT_CTRL_STS_REG_1(dev, slv_addr, bdst)
		self.EXT_CTRL_STS_REG_2 = EXT_CTRL_STS_REG_2(dev, slv_addr, bdst)
	def read_all(self):
		attributes = vars(self)
		for name, value in attributes.items():
			if not name.startswith('__') and not callable(value):
				getattr(self,name).read()
				getattr(self,name).display()
