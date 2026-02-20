class DEVICE_ID:
	def __init__(self,dev):
		self.dev = dev
		self._addr = addr
		self.device_id = 0
	def write(self):
		val = 0
		val |= self.device_id << 0
		self.dev.write(self._addr,val)
	def read(self):
		val = self.dev.read(self._addr)
		self.device_id = (val & 0xFF) >> 0
		return val

class REVISION:
	def __init__(self,dev):
		self.dev = dev
		self._addr = addr
		self.major_rev = 0
		self.minor_rev = 0
	def write(self):
		val = 0
		val |= self.major_rev << 0
		val |= self.minor_rev << 4
		self.dev.write(self._addr,val)
	def read(self):
		val = self.dev.read(self._addr)
		self.major_rev = (val & 0x0F) >> 0
		self.minor_rev = (val & 0xF0) >> 4
		return val

class PHASE_CODE_TX0:
	def __init__(self,dev):
		self.dev = dev
		self._addr = addr
		self.phase_code_tx0 = 0
	def write(self):
		val = 0
		val |= self.phase_code_tx0 << 0
		self.dev.write(self._addr,val)
	def read(self):
		val = self.dev.read(self._addr)
		self.phase_code_tx0 = (val & 0x7F) >> 0
		return val

class GAIN_CODE_TX0:
	def __init__(self,dev):
		self.dev = dev
		self._addr = addr
		self.gain_code_tx0 = 0
	def write(self):
		val = 0
		val |= self.gain_code_tx0 << 0
		self.dev.write(self._addr,val)
	def read(self):
		val = self.dev.read(self._addr)
		self.gain_code_tx0 = (val & 0x3F) >> 0
		return val

class temp:
	def __init__(self,dev):
		self.REVISION = REVISION(dev)
		self.PHASE_CODE_TX0 = PHASE_CODE_TX0(dev)
		self.GAIN_CODE_TX0 = GAIN_CODE_TX0(dev)