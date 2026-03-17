version = 'v1'
import sys
sys.path.append('../include')

from SPI import *
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tabbed GUI App")
        self.geometry("1000x650")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self._create_layout()
        self._create_tabs()
        self._create_status_bar()

        self.spi = SPI()
        self.orion_bdst = ORION_8G_12G(self.spi, 0, 1)
        self.orion_lut_bdst = ORION_8G_12G_lut(self.spi)
        self.device_count = 0x20  # Scans from 0x00 to 0x1F (32 addresses)
        self.dev_addr = []
        self.dev_csr = []
        self.dev_lut = []
        self.dev_hal = []

        self.hal_bdst = ORION_8G_12G_hal(self.orion_bdst, self.orion_lut_bdst, self.spi, version)

        self.cfg_path = ''
        self.cal_path = ''

    # =========================
    # Layout
    # =========================
    def _create_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ttk.Frame(self, padding=5)
        self.container.grid(row=0, column=0, sticky="nsew")

    # =========================
    # Tabs
    # =========================
    def _create_tabs(self):
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True)

        self.tab_calibration = ttk.Frame(self.notebook)
        self.tab_steering = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calibration, text="Calibration")
        self.notebook.add(self.tab_steering, text="Steering")

        self._build_calibration_tab()

    # =========================
    # Calibration Tab
    # =========================
    def _build_calibration_tab(self):
        self.tab_calibration.grid_rowconfigure(0, weight=1)
        self.tab_calibration.grid_columnconfigure(0, weight=1)

        self.paned = ttk.PanedWindow(self.tab_calibration, orient="horizontal")
        self.paned.grid(row=0, column=0, sticky="nsew")

        self.calib_sidebar = ttk.Frame(self.paned, padding=10, relief="solid", borderwidth=1)
        self.calib_main = ttk.Frame(self.paned, padding=10, relief="solid", borderwidth=1)

        self.paned.add(self.calib_sidebar, weight=1)
        self.paned.add(self.calib_main, weight=4)

        ttk.Button(self.calib_sidebar, text="Sanity", command=self.on_sanity).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Load Plank Cfg", command=self.on_load_plank).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Init Plank", command=self.on_init_plank).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Program Defaults", command=self.on_program_defaults).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Save Cal", command=self.on_save_cal).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Load Cal", command=self.on_load_cal).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Reset Plank", command=self.on_reset).pack(fill="x", pady=5)

        # ---- TR Mode ----
        ttk.Label(self.calib_sidebar, text="TR Mode:").pack(anchor="w", pady=(0, 5))

        self.tr_mode = tk.StringVar(value="RX")  # default

        ttk.Radiobutton(
            self.calib_sidebar,
            text="TX",
            variable=self.tr_mode,
            value="TX"
        ).pack(anchor="w")

        ttk.Radiobutton(
            self.calib_sidebar,
            text="RX",
            variable=self.tr_mode,
            value="RX"
        ).pack(anchor="w", pady=(0, 10))

    # =========================
    # Table
    # =========================
    def populate_calibration_table(self):
        for widget in self.calib_main.winfo_children():
            widget.destroy()

        self.element_controls = {}

        headers = [
            "Sel", "Element", "BFM", "CH",
            "Cal Bias", "Cal Gain", "Cal Phase",
            "Bias", "Gain", "Phase"
        ]

        for col, text in enumerate(headers):
            ttk.Label(self.calib_main, text=text, font=("Arial", 10, "bold")) \
                .grid(row=0, column=col, padx=4, pady=5)

        for row_idx, entry in enumerate(self.mapping["list"], start=1):
            element_id = entry["element_id"]

            vars_dict = {
                "selected": tk.BooleanVar(value=False),

                "cal_bias": tk.IntVar(value=0),
                "cal_gain": tk.IntVar(value=0),
                "cal_phase": tk.IntVar(value=0),

                "bias": tk.IntVar(value=0),
                "gain": tk.IntVar(value=0),
                "phase": tk.IntVar(value=0),
            }

            for name, var in vars_dict.items():
                if name != "selected":
                    self.attach_callback(var, element_id, name)

            vars_dict["selected"].trace_add("write", lambda *args, eid=element_id: self.on_element_select(eid))

            ttk.Checkbutton(self.calib_main, variable=vars_dict["selected"]) \
                .grid(row=row_idx, column=0)

            ttk.Label(self.calib_main, text=str(entry["element_id"])) \
                .grid(row=row_idx, column=1)
            ttk.Label(self.calib_main, text=hex(entry["bfm_id"])) \
                .grid(row=row_idx, column=2)
            ttk.Label(self.calib_main, text=str(entry["ch_id"])) \
                .grid(row=row_idx, column=3)

            ttk.Label(self.calib_main, textvariable=vars_dict["cal_bias"]) \
                .grid(row=row_idx, column=4)
            ttk.Label(self.calib_main, textvariable=vars_dict["cal_gain"]) \
                .grid(row=row_idx, column=5)
            ttk.Label(self.calib_main, textvariable=vars_dict["cal_phase"]) \
                .grid(row=row_idx, column=6)

            ttk.Spinbox(self.calib_main, from_=0, to=255, textvariable=vars_dict["bias"], width=5) \
                .grid(row=row_idx, column=7)
            ttk.Spinbox(self.calib_main, from_=0, to=63, textvariable=vars_dict["gain"], width=5) \
                .grid(row=row_idx, column=8)
            ttk.Spinbox(self.calib_main, from_=4, to=124, textvariable=vars_dict["phase"], width=5) \
                .grid(row=row_idx, column=9)

            self.element_controls[element_id] = vars_dict

    # =========================
    # Status Bar
    # =========================
    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var).grid(row=1, column=0, sticky="ew")

    # =========================
    # Helpers
    # =========================
    def attach_callback(self, var, element_id, field_name):
        def callback(*args):
            try:
                value = var.get()
            except:
                return
            self.on_spinbox_change(element_id, field_name, value)
        var.trace_add("write", callback)

    def load_element_map(self, csv_path):
        data = []
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "element_id": int(row["element_id"]),
                    "bfm_id": int(row["bfm_id"], 16),
                    "ch_id": int(row["ch_id"])
                })
        return {"list": data}

    # =========================
    # Handlers
    # =========================
    def on_element_select(self, element_id):
        selected = self.element_controls[element_id]["selected"].get()
        print(f"Element {element_id} {'selected' if selected else 'deselected'}")
        entry = next(e for e in self.mapping["list"] if e["element_id"] == element_id)
        print(entry)
        for addr in self.dev_addr:
            ch_en = 0
            for e in self.mapping["list"]:
                if e["bfm_id"] == addr and self.element_controls[e["element_id"]]["selected"].get():
                    ch_en |= (1 << e["ch_id"])
            print(ch_en)
            self.dev_hal[addr].set_tr_mask(tx_mask=ch_en, rx_mask=ch_en)
            self.dev_hal[addr].stg2_load()


    def on_program_defaults(self):
        for controls in self.element_controls.values():
            controls["bias"].set(15)
            controls["gain"].set(0)
            controls["phase"].set(4)

        # self.hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF, PA0=85, PA1=85, PA2=85, PA3=85, LNA0=15, LNA1=15, LNA2=15, LNA3=15)
        self.status_var.set("Defaults programmed")

    def on_spinbox_change(self, element_id, field_name, value):
        if "phase" in field_name:
            value = max(4, min(124, value))
        elif "gain" in field_name:
            value = max(0, min(63, value))
        else:
            value = max(0, min(255, value))

        self.element_controls[element_id][field_name].set(value)
        self.status_var.set(f"E{element_id} {field_name} → {value}")

        if(field_name == "bias"):
            addr = self.mapping["list"][element_id]["bfm_id"]
            ch_id = self.mapping["list"][element_id]["ch_id"]
            lna_sel = 1 << ch_id
            self.dev_hal[addr].dac_cfg(pa_sel=0x0, lna_sel=lna_sel, **{f'LNA{ch_id}': value})
            print(f'Updated Device {hex(addr)} Channel {ch_id} Bias to {value}')

    def on_sanity(self):
        self.status_var.set("Sanity check")
        dev_addr = []
        print("Scanning for ORION devices at hex addresses 0x00 to 0x1F...")

        for addr in range(0x00, self.device_count):
            try:
                dev = ORION_8G_12G(self.spi, addr, 0)
                dev.DEVICE_ID.read()
                device_id = dev.DEVICE_ID.device_id
                dev.REVISION.read()
                major = dev.REVISION.major_rev
                minor = dev.REVISION.minor_rev

                if device_id == 0xF2 and major == 1 and minor == 1:
                    print(f"Device found at address 0x{addr:02X}: ID=0x{device_id:02X}, Rev={major}.{minor}")
                    dev_addr.append(addr)
            except Exception:
                pass  # Ignore errors if no device responds

        print("\nSummary:")
        print(f"Total Devices Detected: {len(dev_addr)}")
        print("dev_addr =", [f"0x{addr:02X}" for addr in dev_addr])
        status_var = f"Sanity: {len(dev_addr)} devices found at " + ", ".join([f"0x{addr:02X}" for addr in dev_addr])
        self.status_var.set(status_var)
        print('\n')

    def on_load_plank(self, path=None):
        if(path is None):
            self.cfg_path = filedialog.askopenfilename(filetypes=[("Config files", "*.cfg"), ("All files", "*.*")])
            if not self.cfg_path:
                return
        else:
            self.cfg_path = path
        self.cal_path = self.cfg_path.replace(".cfg", ".cal")

        self.mapping = self.load_element_map(self.cfg_path)
        for entry in self.mapping["list"]:
            print(f"E{entry['element_id']}: BFM={hex(entry['bfm_id'])}, CH={entry['ch_id']}")
            self.dev_addr.append(entry["bfm_id"])
        self.dev_addr = list(dict.fromkeys(self.dev_addr))
        print(self.dev_addr)
        for addr in self.dev_addr:
            dev_csr = ORION_8G_12G(self.spi, addr, 0)
            dev_lut = ORION_8G_12G_lut(self.spi, addr, 0)
            dev_hal = ORION_8G_12G_hal(dev_csr, dev_lut, self.spi, version)
            self.dev_csr.append(dev_csr)
            self.dev_lut.append(dev_lut)
            self.dev_hal.append(dev_hal)
        print(self.dev_hal)
        self.populate_calibration_table()
        self.status_var.set("Plank loaded")

    def on_init_plank(self):
        # Write DACs and reset TR configs via broadcast
        self.hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)

        # Setting data path and tx and rx mask to 0 for safety
        self.hal_bdst.en_data_path(0)
        self.hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)
        self.status_var.set("Plank Initialized")

        # Setup in RX Mode
        self.hal_bdst.init_lut_new(
            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
            r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

        self.hal_bdst.cfg_stg2_load('REG')
        self.hal_bdst.set_tr_mode('EXT_TR')
        self.hal_bdst.set_trx_mode(0)
        self.hal_bdst.init_rx('NOM')
        self.hal_bdst.set_freq('11G')
        self.hal_bdst.enable_rx_correction(1)
        self.hal_bdst.en_data_path(1)

    def on_save_cal(self):
        with open(self.cal_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["element_id", "bfm_id", "ch_id", "bias", "gain", "phase"])

            for entry in self.mapping["list"]:
                eid = entry["element_id"]
                c = self.element_controls[eid]

                writer.writerow([
                    eid,
                    hex(entry["bfm_id"]),
                    entry["ch_id"],
                    c["bias"].get(),
                    c["gain"].get(),
                    c["phase"].get()
                ])

        self.status_var.set("Saved")

    def on_load_cal(self):
        try:
            with open(self.cal_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    eid = int(row["element_id"])
                    c = self.element_controls[eid]

                    c["cal_bias"].set(int(row["bias"]))
                    c["cal_gain"].set(int(row["gain"]))
                    c["cal_phase"].set(int(row["phase"]))

            self.status_var.set("Loaded cal")

        except:
            self.status_var.set("Load failed")

    def on_reset(self):
        self.orion_bdst.SYNC_RST.sync_rst = 1
        self.orion_bdst.SYNC_RST.write()
        self.orion_bdst.SYNC_RST.sync_rst = 0
        self.orion_bdst.SYNC_RST.write()

        self.on_load_plank(self.cfg_path)  # this resets all GUI selections

        self.status_var.set("Plank reset")

if __name__ == "__main__":
    app = App()
    app.mainloop()