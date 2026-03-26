import pyvisa
import time

class vna:
    def __init__(self, rm_vna):
        self.rm_vna = rm_vna

    def query(self, command):
        return self.rm_vna.query(command)

    def write(self, command):
        return self.rm_vna.write(command)

    def init(self, num_win=2):
        self.rm_vna.write(':SYSTem:FPR')
        # time.sleep(1)

        for i in range(1, num_win + 1):
            self.rm_vna.write(f':DISP:WIND{i}:STATe ON')
            # time.sleep(0.5)

    def cfg(self, win_id, mode):
        if mode == 'S21_GAIN':
            self.rm_vna.write(f':CALC:MEAS{win_id}:DEF "S21"')
            self.rm_vna.write(f':DISP:MEAS{win_id}:FEED 1')
            # time.sleep(0.5)
        if mode == 'S21_PHASE':
            # time.sleep(0.5)
            self.rm_vna.write(f':CALC:MEAS{win_id}:DEF "S21"')
            self.rm_vna.write(f':CALC:MEAS{win_id}:FORM PHASe')
            self.rm_vna.write(f':DISP:MEAS{win_id}:FEED 2')
        if mode == 'S12_GAIN':
            self.rm_vna.write(f':CALC:MEAS{win_id}:DEF "S12"')
            self.rm_vna.write(f':DISP:MEAS{win_id}:FEED 1')
            # time.sleep(0.5)
        if mode == 'S12_PHASE':
            # time.sleep(0.5)
            self.rm_vna.write(f':CALC:MEAS{win_id}:DEF "S12"')
            self.rm_vna.write(f':CALC:MEAS{win_id}:FORM PHASe')
            self.rm_vna.write(f':DISP:MEAS{win_id}:FEED 2')

    def cfg_freq(self, start=7e9, stop=13e9, step=250e6):
        self.rm_vna.write(f':SENS:FREQ:STAR {start}')
        self.rm_vna.write(f':SENS:FREQ:STOP {stop}')
        self.rm_vna.write(f':SENS:SWE:STEP {step}')
        # time.sleep(0.5)

    def cfg_pwr(self, pwr=-20):
        self.rm_vna.write(f':SOUR:POW1 {pwr}')
        # time.sleep(0.5)

    def add_marker(self, win_id, marker_id, val):
        self.rm_vna.write(f':CALC:MEAS{win_id}:MARK{marker_id} ON')
        self.rm_vna.write(f':CALC:MEAS{win_id}:MARK{marker_id}:X {val}')
        # time.sleep(0.5)

    def set_y_axis(self, win_id=1, trace_id=1, ref_level=0, scale_per_div=10):
        self.rm_vna.write(f':DISP:WIND{win_id}:TRAC{trace_id}:Y:RLEV {ref_level}')
        self.rm_vna.write(f':DISP:WIND{win_id}:TRAC{trace_id}:Y:PDIV {scale_per_div}')
        # time.sleep(0.5)

    def norm(self, win_id=1):
        self.rm_vna.write(f':CALC:MEAS{win_id}:MATH:NORM')

class instruments:
    def __init__(self, required_instruments=None):
        if required_instruments:
            print(f'Instruments Required: {required_instruments}')
        self.rm = pyvisa.ResourceManager()
        print('\nInstruments Available: ', self.rm.list_resources())

        try:
            rm_vna = self.rm.open_resource('USB0::0x2A8D::0x2A01::MY63057316::0::INSTR')
            print('VNA: ', rm_vna.query('*IDN?'))
            self.vna = vna(rm_vna)
        except Exception as e:
            self.vna = None
            print(f"Failed to connect to VNA: {e}")
            if 'vna' in required_instruments:
                print('ERR: VNA not found, exiting...')
                exit(1)

        try:
            rm_supply = self.rm.open_resource('USB0::0x1AB1::0xA4A8::DP9D264601288::INSTR')
            print('DC Supply: ', rm_supply.query('*IDN?'))
        except Exception as e:
            self.supply = None
            print(f"Failed to connect to DC Supply: {e}")
            if 'supply' in required_instruments:
                print('ERR: DC Supply not found, exiting...')
                exit(1)

if __name__ == "__main__":
    instruments = instruments(required_instruments=['vna'])
    instruments.vna.init()
    instruments.vna.cfg(1, 'S21_GAIN')
    instruments.vna.cfg(2, 'S21_PHASE')
    instruments.vna.cfg_freq(start=7e9, stop=13e9, step=250e6)
    instruments.vna.cfg_pwr(pwr=-20)

    instruments.vna.add_marker(win_id=1, marker_id=1, val=8e9)
    instruments.vna.add_marker(win_id=1, marker_id=2, val=10e9)
    instruments.vna.add_marker(win_id=1, marker_id=3, val=12e9)

    instruments.vna.add_marker(win_id=2, marker_id=1, val=8e9)
    instruments.vna.add_marker(win_id=2, marker_id=2, val=10e9)
    instruments.vna.add_marker(win_id=2, marker_id=3, val=12e9)

    instruments.vna.set_y_axis(win_id=1, ref_level=-20, scale_per_div=5)
    instruments.vna.set_y_axis(win_id=2, ref_level=0, scale_per_div=45)

    instruments.vna.norm(win_id=2)
