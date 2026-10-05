version = 'v2'

# The table shows (and the table edits, Program Defaults and Load Cal write) only the active LNA / PA bias DACs
# (DAC_CTRL_LNAx / DAC_CTRL_PAx), not the _PDN ones.
# Init Plank is unchanged: it calls dac_cfg with its defaults (LNA 127, PA 0 for v2 / 127 for v1; the _PDN DACs too).
# These two constants are those defaults, only used to show the values in the table after Init Plank.
INIT_LNA_BIAS = 127
INIT_PA_BIAS = 0 if version == 'v2' else 127

# Bias DAC codes of the two fixed bias voltages
LNA_BIAS_M2P5 = 40                             # LNA bias of -2.5 V
PA_BIAS_M3P3 = 60 if version == 'v1' else 20   # PA bias of -3.3 V
import sys
sys.path.append('../include')

from SPI import *
from ORION_8G_12G import *
from ORION_8G_12G_lut import *
from ORION_8G_12G_hal import *

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import csv
import os
import queue
import re
import threading
import serial.tools.list_ports

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

        self.spi = None  # opened by Connect, closed by Disconnect
        self.orion_bdst = None
        self.orion_lut_bdst = None
        self.hal_bdst = None
        self.device_count = 0x20  # Scans from 0x00 to 0x1F (32 addresses)
        self.dev_addr = []
        self.dev_csr = []
        self.dev_lut = []
        self.dev_hal = []

        self.cfg_path = ''

        self._connect_queue = queue.Queue()
        self._bulk_select = False  # True while Select All / Deselect All changes many elements (masks are applied once at the end)
        self._syncing = False  # True while the GUI values are set from the hardware state (no writes back to the chip)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.on_scan_ports()

    # =========================
    # Layout
    # =========================
    def _create_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ttk.Frame(self, padding=5)
        self.container.grid(row=0, column=0, sticky="nsew")

        self._create_connection_bar()

    # =========================
    # Connection (SPI port)
    # =========================
    def _create_connection_bar(self):
        bar = ttk.Frame(self.container)
        bar.pack(side="top", fill="x", pady=(0, 5))

        ttk.Label(bar, text="PORT").pack(side="left", padx=(0, 5))
        self.port_combo = ttk.Combobox(bar, state="readonly", width=40)
        self.port_combo.pack(side="left", padx=5)
        self.btn_connect = ttk.Button(bar, text="Connect", command=self.on_connect)
        self.btn_connect.pack(side="left", padx=5)
        self.btn_disconnect = ttk.Button(bar, text="Disconnect", command=self.on_disconnect, state="disabled")
        self.btn_disconnect.pack(side="left", padx=5)
        self.btn_scan = ttk.Button(bar, text="Scan COM Ports", command=self.on_scan_ports)
        self.btn_scan.pack(side="left", padx=5)

        self.conn_var = tk.StringVar(value="Disconnected")
        ttk.Label(bar, textvariable=self.conn_var, font=("Arial", 10, "bold")).pack(side="left", padx=15)

    def on_scan_ports(self):
        ports = [p for p in serial.tools.list_ports.comports() if "USB" in p.hwid]
        for p in ports:
            print(f"[{p.device}] {p.description} [{p.hwid}]")
        if not ports:
            print("No USB COM ports available.")

        values = [str(p) for p in ports]
        current = self.port_combo.get()
        self.port_combo["values"] = values
        if current in values:
            self.port_combo.set(current)  # keep the selection if the port is still there
        elif values:
            self.port_combo.current(0)
        else:
            self.port_combo.set("")
        if hasattr(self, "status_var"):
            self.status_var.set(f"{len(values)} USB port(s) found")

    def _set_conn_buttons(self, connected=False, connecting=False):
        self.btn_connect.config(state="disabled" if connected or connecting else "normal")
        self.btn_disconnect.config(state="normal" if connected else "disabled")
        self.btn_scan.config(state="disabled" if connecting else "normal")

    def on_connect(self):
        match = re.search(r'\b(COM\d+)\b', self.port_combo.get())
        if not match:
            self.status_var.set("No port selected: press Scan COM Ports and pick a port")
            return
        port = match.group(1)

        if self.spi is not None:
            self.on_disconnect()  # release the port of the previous connection first

        self._set_conn_buttons(connecting=True)
        self.conn_var.set(f"Connecting @ {port}...")
        self.status_var.set(f"Connecting @ {port}...")

        def work():  # SPI() waits 1 s, so it runs in a thread to keep the window responsive
            try:
                self._connect_queue.put(("ok", port, SPI(port)))
            except Exception as e:
                self._connect_queue.put(("error", port, e))

        threading.Thread(target=work, daemon=True).start()
        self.after(100, self._poll_connect)

    def _poll_connect(self):
        try:
            kind, port, result = self._connect_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_connect)
            return

        if kind == "error":
            self.conn_var.set("Disconnected")
            self.status_var.set(f"Connect failed @ {port}: {result}")
            self._set_conn_buttons(connected=False)
            messagebox.showerror("Connect failed", f"Could not open {port}:\n{result}")
            return

        self.spi = result
        self.orion_bdst = ORION_8G_12G(self.spi, 0, 1)
        self.orion_lut_bdst = ORION_8G_12G_lut(self.spi)
        self.hal_bdst = ORION_8G_12G_hal(self.orion_bdst, self.orion_lut_bdst, self.spi, version)
        self._create_devices()  # a plank loaded before connecting
        self.conn_var.set(f"Connected @ {port}")
        self.status_var.set(f"Connected @ {port}")
        self._set_conn_buttons(connected=True)

    def on_disconnect(self):
        if self.spi is None:
            self.status_var.set("Not connected")
            return
        try:
            self.spi.close()
        except Exception as e:
            print(f"Error while closing SPI: {e}")
        self.spi = None
        self.orion_bdst = None
        self.orion_lut_bdst = None
        self.hal_bdst = None
        self.dev_csr, self.dev_lut, self.dev_hal = [], [], []  # these held the closed port
        self.conn_var.set("Disconnected")
        self.status_var.set("Disconnected")
        self._set_conn_buttons(connected=False)

    def _connected(self):
        if self.spi is None:
            self.status_var.set("Not connected: connect to a port first")
            return False
        return True

    def _create_devices(self):
        """(Re)create the objects of the loaded plank's devices on the current SPI connection."""
        self.dev_csr, self.dev_lut, self.dev_hal = [], [], []
        if self.spi is None:
            return
        for addr in self.dev_addr:
            dev_csr = ORION_8G_12G(self.spi, addr, 0)
            dev_lut = ORION_8G_12G_lut(self.spi, addr, 0)
            dev_hal = ORION_8G_12G_hal(dev_csr, dev_lut, self.spi, version)
            self.dev_csr.append(dev_csr)
            self.dev_lut.append(dev_lut)
            self.dev_hal.append(dev_hal)

    def _on_close(self):
        self.on_disconnect()  # releases the COM port
        self.destroy()

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
        ttk.Label(self.calib_sidebar, text="Cal file:").pack(anchor="w", pady=(10, 0))
        self.cal_path_var = tk.StringVar()
        ttk.Entry(self.calib_sidebar, textvariable=self.cal_path_var).pack(fill="x", pady=(0, 2))
        ttk.Button(self.calib_sidebar, text="Browse Cal File", command=self.on_browse_cal).pack(fill="x", pady=(0, 5))
        ttk.Button(self.calib_sidebar, text="Save Cal", command=self.on_save_cal).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Load Cal", command=self.on_load_cal).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Reset Plank", command=self.on_reset).pack(fill="x", pady=5)

        # ---- TR Mode ----
        ttk.Label(self.calib_sidebar, text="TR Mode:").pack(anchor="w", pady=(0, 5))

        self.tr_mode = tk.StringVar(value="RX")  # default
        # the Bias / Gain / Phase columns of the table follow the TR mode (RX or TX values) and the devices are set to it
        self.tr_mode.trace_add("write", lambda *args: self._on_tr_mode_change())

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
        self.mode_widgets = {}  # element id -> {field: widget}: they show the RX or the TX value, see _refresh_mode_view

        toolbar = ttk.Frame(self.calib_main)
        toolbar.grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 5))
        ttk.Button(toolbar, text="Select All", command=lambda: self.select_all_elements(True)).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Deselect All", command=lambda: self.select_all_elements(False)).pack(side="left")

        headers = [
            "Sel", "Element", "BFM", "CH",
            "Cal Bias", "Cal Gain", "Cal Phase",
            "Bias", "Gain", "Phase"
        ]

        for col, text in enumerate(headers):
            ttk.Label(self.calib_main, text=text, font=("Arial", 10, "bold")) \
                .grid(row=1, column=col, padx=4, pady=5)

        for row_idx, entry in enumerate(self.mapping["list"], start=2):
            element_id = entry["element_id"]

            vars_dict = {
                "selected": tk.BooleanVar(value=False),

                "cal_bias": tk.IntVar(value=0),  # cal LNA bias
                "cal_pa_bias": tk.IntVar(value=0),
                "cal_rx_gain": tk.IntVar(value=0),
                "cal_tx_gain": tk.IntVar(value=0),
                "cal_rx_phase": tk.IntVar(value=0),
                "cal_tx_phase": tk.IntVar(value=0),

                "bias": tk.IntVar(value=0),  # LNA bias
                "pa_bias": tk.IntVar(value=0),
                "rx_gain": tk.IntVar(value=0),
                "tx_gain": tk.IntVar(value=0),
                "rx_phase": tk.IntVar(value=0),
                "tx_phase": tk.IntVar(value=0),
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

            widgets = {}
            for col, field in enumerate(("bias", "gain", "phase"), start=4):
                widgets["cal_" + field] = ttk.Label(self.calib_main, textvariable=vars_dict[self._view_key(field, cal=True)])
                widgets["cal_" + field].grid(row=row_idx, column=col)
            for col, (field, lo, hi) in enumerate((("bias", 0, 255), ("gain", 0, 63), ("phase", 4, 124)), start=7):
                widgets[field] = ttk.Spinbox(self.calib_main, from_=lo, to=hi, textvariable=vars_dict[self._view_key(field)], width=5)
                widgets[field].grid(row=row_idx, column=col)

            self.mode_widgets[element_id] = widgets
            self.element_controls[element_id] = vars_dict

    # what the Bias / Gain / Phase columns show in RX mode and in TX mode (the .cal file keeps all of them)
    MODE_FIELDS = {"bias": ("bias", "pa_bias"), "gain": ("rx_gain", "tx_gain"), "phase": ("rx_phase", "tx_phase")}

    def _view_key(self, field, cal=False):
        """Variable behind a column of the table in the current TR mode (cal=True: the cal value)."""
        rx_key, tx_key = self.MODE_FIELDS[field]
        key = rx_key if self.tr_mode.get() == "RX" else tx_key
        return ("cal_" + key) if cal else key

    def _on_tr_mode_change(self):
        """TX / RX radio button: show the values of that mode and program the devices with set_trx_mode (RX = 0, TX = 1)."""
        self._refresh_mode_view()
        trx = 1 if self.tr_mode.get() == "TX" else 0
        if self.spi is None:
            self.status_var.set(f"TR mode {self.tr_mode.get()} selected (not connected: devices not programmed)")
            return
        try:
            self.hal_bdst.set_trx_mode(trx)
        except Exception as e:
            self.status_var.set(f"Setting the TRX mode failed: {e}")
            messagebox.showerror("TR mode", f"Could not set the TRX mode of the devices:\n{e}")
            return
        self.status_var.set(f"TR mode {self.tr_mode.get()}: devices programmed with set_trx_mode({trx}). "
                            f"Bias is the {'PA' if trx else 'LNA'} bias, Gain and Phase are the {self.tr_mode.get()} values")

    def _refresh_mode_view(self):
        """Point the Bias / Gain / Phase columns of every element at the RX values (RX mode) or the TX values (TX mode)."""
        if not getattr(self, "mode_widgets", None):
            return
        for element_id, widgets in self.mode_widgets.items():
            vars_dict = self.element_controls[element_id]
            for field in self.MODE_FIELDS:
                widgets["cal_" + field].config(textvariable=vars_dict[self._view_key(field, cal=True)])
                widgets[field].config(textvariable=vars_dict[self._view_key(field)])
        rx = self.tr_mode.get() == "RX"
        self.status_var.set(f"TR mode {self.tr_mode.get()}: Bias is the {'LNA' if rx else 'PA'} bias, Gain and Phase are the {self.tr_mode.get()} values")

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
        if self._bulk_select:
            return
        selected = self.element_controls[element_id]["selected"].get()
        print(f"Element {element_id} {'selected' if selected else 'deselected'}")
        entry = next(e for e in self.mapping["list"] if e["element_id"] == element_id)
        print(entry)
        self._apply_tr_masks()

    def _apply_tr_masks(self):
        """Enable the TX / RX channels of the selected elements on every device."""
        if not self._connected():
            return
        for addr in self.dev_addr:
            ch_en = 0
            for e in self.mapping["list"]:
                if e["bfm_id"] == addr and self.element_controls[e["element_id"]]["selected"].get():
                    ch_en |= (1 << e["ch_id"])
            print(ch_en)
            self._hal_for(addr).set_tr_mask(tx_mask=ch_en, rx_mask=ch_en)
            self._hal_for(addr).stg2_load()


    def select_all_elements(self, value=True):
        if not hasattr(self, "element_controls"):
            self.status_var.set("Load a plank cfg first")
            return
        self._bulk_select = True
        try:
            for controls in self.element_controls.values():
                controls["selected"].set(value)
        finally:
            self._bulk_select = False
        self._apply_tr_masks()  # one update for all elements
        n = len(self.element_controls)
        self.status_var.set(f"{n if value else 0} of {n} elements selected"
                            + ("" if self.spi is not None else " (not connected: masks not applied)"))

    def on_program_defaults(self):
        # LNA bias -2.5 V and PA bias -3.3 V on all channels: programmed into the bias DACs (broadcast) and shown in the table
        # (only the LNA / PA DACs shown in the table, the _PDN DACs are not touched)
        if self.spi is not None:
            self._write_bias(self.hal_bdst, lna=LNA_BIAS_M2P5, pa=PA_BIAS_M3P3)
        self._show_bias(LNA_BIAS_M2P5, PA_BIAS_M3P3)

        for controls in self.element_controls.values():
            controls["rx_gain"].set(0)
            controls["tx_gain"].set(0)
            controls["rx_phase"].set(4)
            controls["tx_phase"].set(4)

        self.status_var.set(f"Defaults programmed: LNA bias -2.5 V (code {LNA_BIAS_M2P5}), PA bias -3.3 V (code {PA_BIAS_M3P3})"
                            + ("" if self.spi is not None else " (not connected: bias DACs not programmed)"))

    def on_spinbox_change(self, element_id, field_name, value):
        if "phase" in field_name:
            value = max(4, min(124, value))
        elif "gain" in field_name:
            value = max(0, min(63, value))
        else:
            value = max(0, min(255, value))

        self.element_controls[element_id][field_name].set(value)
        self.status_var.set(f"E{element_id} {field_name} → {value}")

        if field_name in ("bias", "pa_bias") and self.spi is not None and not self._syncing:
            addr = self.mapping["list"][element_id]["bfm_id"]
            ch_id = self.mapping["list"][element_id]["ch_id"]
            if field_name == "bias":
                self._write_bias(self._hal_for(addr), lna=value, ch_mask=1 << ch_id)
            else:
                self._write_bias(self._hal_for(addr), pa=value, ch_mask=1 << ch_id)
            print(f'Updated Device {hex(addr)} Channel {ch_id} {"LNA" if field_name == "bias" else "PA"} Bias to {value}')

    def _scan_devices(self):
        """Addresses (0x00 to 0x1F) of the ORION devices that answer with the expected device ID (0xF2) and revision (1.1)."""
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
        print('\n')
        return dev_addr

    def on_sanity(self):
        if not self._connected():
            return
        self.status_var.set("Sanity check")
        dev_addr = self._scan_devices()
        status_var = f"Sanity: {len(dev_addr)} devices found at " + ", ".join([f"0x{addr:02X}" for addr in dev_addr])
        self.status_var.set(status_var)

    def on_load_plank(self, path=None, keep_cal_path=False):
        if(path is None):
            cfg_path = filedialog.askopenfilename(filetypes=[("Config files", "*.cfg"), ("All files", "*.*")])
            if not cfg_path:
                return
        else:
            cfg_path = path

        # the cfg is only used if the connected devices (sanity scan) match it: number of beamformers and chip ids (bfm_id)
        if not self._connected():
            messagebox.showerror("Load Plank Cfg", "Not connected.\n\nConnect to a port first: the cfg is checked against the devices "
                                 "on the plank (sanity) before it is loaded.")
            return
        mapping = self.load_element_map(cfg_path)
        expected = sorted({entry["bfm_id"] for entry in mapping["list"]})
        self.status_var.set("Checking the cfg against the devices (sanity)...")
        self.update_idletasks()
        found = sorted(self._scan_devices())
        if found != expected:
            fmt = lambda addrs: ", ".join(f"0x{a:02X}" for a in addrs) or "none"
            lines = [f"The plank cfg does not match the devices on the plank. Nothing was loaded.\n",
                     f"cfg:    {len(expected)} beamformer(s): {fmt(expected)}",
                     f"found:  {len(found)} beamformer(s): {fmt(found)}"]
            if set(expected) - set(found):
                lines.append(f"in the cfg but not found: {fmt(sorted(set(expected) - set(found)))}")
            if set(found) - set(expected):
                lines.append(f"found but not in the cfg: {fmt(sorted(set(found) - set(expected)))}")
            self.status_var.set("Plank cfg mismatch: nothing loaded")
            messagebox.showerror("Plank cfg mismatch", "\n".join(lines))
            return

        # default cal file: same folder and name as the cfg, shown in the Cal file box (it can be changed there).
        # Loading a cfg always replaces what is in the box; only Reset Plank (keep_cal_path) keeps the path that is there.
        default_cal = os.path.splitext(cfg_path)[0] + ".cal"
        if not keep_cal_path or not self.cal_path_var.get().strip():
            self.cal_path_var.set(default_cal)
        self.cfg_path = cfg_path

        self.mapping = mapping
        self.dev_addr = []
        for entry in self.mapping["list"]:
            print(f"E{entry['element_id']}: BFM={hex(entry['bfm_id'])}, CH={entry['ch_id']}")
            self.dev_addr.append(entry["bfm_id"])
        self.dev_addr = list(dict.fromkeys(self.dev_addr))
        print(self.dev_addr)
        self._create_devices()
        print(self.dev_hal)
        self.populate_calibration_table()
        cal_path = self.cal_path_var.get().strip()
        self.status_var.set(f"Plank cfg loaded successfully: {len(expected)} beamformer(s) match {os.path.basename(self.cfg_path)}. "
                            f"Cal file: {os.path.basename(cal_path)} ({'found' if os.path.isfile(cal_path) else 'does not exist yet'})")

    def on_init_plank(self):
        if not self._connected():
            return
        # Write DACs and reset TR configs via broadcast
        self.hal_bdst.dac_cfg(pa_sel=0xF, lna_sel=0xF)
        self._show_bias(INIT_LNA_BIAS, INIT_PA_BIAS)  # show the defaults that dac_cfg just programmed

        # Setting data path and tx and rx mask to 0 for safety
        self.hal_bdst.en_data_path(0)
        self.hal_bdst.set_tr_mask(tx_mask=0, rx_mask=0)
        self.status_var.set("Plank Initialized")

        # Setup in RX Mode
        gain_lut = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_gain_lut__freq_9p5__algo_joint_max__iq_[264,464]__bias_nom__vdd_3p3__temp_25C__wo_phase_corr.xlsx'  # RX gain LUT (phase correction codes = 0)

        ph_lut = '0dB'  # '0dB', '5dB', or 'switch' (switch LUTs at lut_switch gain code)
        ph_lut_0dB = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_phase_lut__freq_9p5__gm_1__backoff_0__algo_joint_max__av_2047__bias_nom__vdd_3p3__temp_25C__iq_step_is_1.xlsx'
        ph_lut_5db = r'C:\Users\silic\Github\orion_sdk\scripts\logs\v2__rx_phase_lut__freq_9p5__gm_1__backoff_5__algo_joint_max__av_2047__bias_nom__vdd_3p3__temp_25C.xlsx'

        lut1, lut2 = {'0dB': (ph_lut_0dB, ph_lut_0dB),
                      '5dB': (ph_lut_5db, ph_lut_5db),
                      'switch': (ph_lut_0dB, ph_lut_5db)}[ph_lut]  # phase LUTs for the 1st (9G) and 2nd (11G) RX LUT

        self.hal_bdst.init_lut_new(r'C:/Users/silic/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
                               r'C:/Users/silic/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
                               gain_lut,
                               lut1,
                               gain_lut,
                               lut2)


        # self.hal_bdst.init_lut_new(
        #     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/final_lut/TX_Gain_LUT_10p5GHz.xlsx',
        #     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/tx_phase_lut_9p5_pm_0p5_gm_0p4.xlsx',
        #     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
        #     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx',
        #     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/RX0_Gain_LUT_9p5GHz_LowBias_I_460_Q_8.xlsx',
        #     r'C:/Users/silic/OneDrive/Documents/GitHub/orion/results/LUT/phase_lut_freq_9p5_gm_0p5_pm_1p5_optimal.xlsx')

        self.hal_bdst.cfg_stg2_load('REG')
        self.hal_bdst.set_tr_mode('INT_TR')
        self.hal_bdst.set_trx_mode(0)
        self.hal_bdst.init_rx('NOM')
        self.hal_bdst.init_tx('MAX')
        self.hal_bdst.set_freq('9G')
        self.hal_bdst.enable_rx_correction(1)
        self.hal_bdst.en_data_path(1)

    def _write_bias(self, hal, lna=None, pa=None, ch_mask=0xF):
        """Write the LNA / PA bias DACs shown in the table for the channels in ch_mask. The _PDN DACs are not written
        (hal.dac_cfg always writes both, so the DAC registers are written directly)."""
        csr = hal.orion_csr
        for i in range(4):
            if not ch_mask & (1 << i):
                continue
            for name, value in ((f'DAC_CTRL_LNA{i}', lna), (f'DAC_CTRL_PA{i}', pa)):
                if value is not None:
                    setattr(getattr(csr, name), name, value)
                    getattr(csr, name).write()

    def _show_bias(self, lna_bias=None, pa_bias=None):
        """Show the LNA / PA bias codes now set in the hardware in every element of the table (nothing is written to the chip).
        A bias that is None is left as it is."""
        if not hasattr(self, "element_controls"):
            return  # no plank loaded yet
        self._syncing = True
        try:
            for controls in self.element_controls.values():
                if lna_bias is not None:
                    controls["bias"].set(lna_bias)
                if pa_bias is not None:
                    controls["pa_bias"].set(pa_bias)
        finally:
            self._syncing = False

    def on_browse_cal(self):
        # a save dialog without the overwrite question: it can pick an existing cal file or name a new one
        path = filedialog.asksaveasfilename(title="Cal file", defaultextension=".cal", confirmoverwrite=False,
                                            filetypes=[("Cal files", "*.cal"), ("All files", "*.*")])
        if path:
            self.cal_path_var.set(path)

    def on_save_cal(self):
        cal_path = self.cal_path_var.get().strip()
        if not cal_path:
            messagebox.showerror("Save Cal", "No cal file selected.\n\nEnter a path or use Browse Cal File.")
            return
        if getattr(self, "mapping", None) is None:
            self.status_var.set("Load a plank cfg first")
            return
        existed = os.path.exists(cal_path)
        try:
            with open(cal_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["element_id", "bfm_id", "ch_id", "lna_bias", "pa_bias", "rx_gain", "tx_gain", "rx_phase", "tx_phase"])

                for entry in self.mapping["list"]:
                    eid = entry["element_id"]
                    c = self.element_controls[eid]

                    writer.writerow([
                        eid,
                        hex(entry["bfm_id"]),
                        entry["ch_id"],
                        c["bias"].get(),
                        c["pa_bias"].get(),
                        c["rx_gain"].get(),
                        c["tx_gain"].get(),
                        c["rx_phase"].get(),
                        c["tx_phase"].get()
                    ])
        except OSError as e:
            self.status_var.set(f"Save failed: {e}")
            messagebox.showerror("Save Cal", f"Could not write the cal file:\n{cal_path}\n\n{e}")
            return

        if existed:
            self.status_var.set("Saved")
        else:
            self.status_var.set(f"Saved (new cal file created: {os.path.basename(cal_path)})")
            messagebox.showwarning("Cal file created", f"The cal file did not exist, so it was created:\n{cal_path}")

    def _hal_for(self, addr):
        return self.dev_hal[self.dev_addr.index(addr)]

    def _read_cal(self, cal_path):
        """Rows of a .cal file: element id and the bias / gain / phase values (None for a value the file does not have)."""
        rows = []
        with open(cal_path) as f:
            for row in csv.DictReader(f):
                # older cal files call the LNA bias "bias", have one gain / phase for RX and TX, and may not have pa_bias
                get = lambda name, old=None: row.get(name) or (row.get(old) if old else None)
                rows.append({
                    "element_id": int(row["element_id"]),
                    "bias": int(get("lna_bias", "bias")),
                    "pa_bias": int(row["pa_bias"]) if row.get("pa_bias") else None,
                    "rx_gain": int(get("rx_gain", "gain")), "tx_gain": int(get("tx_gain", "gain")),
                    "rx_phase": int(get("rx_phase", "phase")), "tx_phase": int(get("tx_phase", "phase")),
                })
        return rows

    def _program_all(self):
        """Write the bias DACs and the RX / TX gain and phase codes of every element of the table into the devices."""
        for entry in self.mapping["list"]:
            c = self.element_controls[entry["element_id"]]
            hal = self._hal_for(entry["bfm_id"])
            ch = 1 << entry["ch_id"]
            self._write_bias(hal, lna=c["bias"].get(), pa=c["pa_bias"].get(), ch_mask=ch)
            hal.set_lut_idx(c["rx_phase"].get(), c["rx_gain"].get(), ch, mode="RX")
            hal.set_lut_idx(c["tx_phase"].get(), c["tx_gain"].get(), ch, mode="TX")
        for addr in self.dev_addr:
            self._hal_for(addr).stg2_load()

    def on_load_cal(self):
        cal_path = self.cal_path_var.get().strip()
        if not cal_path or not os.path.isfile(cal_path):
            self.status_var.set("Load failed: cal file not found")
            messagebox.showerror("Load Cal", f"Cal file not found:\n{cal_path or '(no file selected)'}\n\nNothing was loaded.")
            return
        try:
            rows = self._read_cal(cal_path)
            unknown = [r["element_id"] for r in rows if r["element_id"] not in self.element_controls]
            if unknown:
                raise ValueError(f"elements {unknown} are not in the loaded plank cfg")
        except Exception as e:
            print(f"Load cal failed: {e}")
            self.status_var.set(f"Load failed: {e}")
            return

        # fill the cal columns and the table (the DACs and codes are written below, not field by field)
        self._syncing = True
        try:
            for r in rows:
                c = self.element_controls[r["element_id"]]
                c["cal_bias"].set(r["bias"]); c["bias"].set(r["bias"])
                if r["pa_bias"] is not None:
                    c["cal_pa_bias"].set(r["pa_bias"]); c["pa_bias"].set(r["pa_bias"])
                for name in ("rx_gain", "tx_gain", "rx_phase", "tx_phase"):
                    c[f"cal_{name}"].set(r[name]); c[name].set(r[name])
        finally:
            self._syncing = False

        if self.spi is None:
            self.status_var.set("Loaded cal into the table (not connected: devices not programmed)")
            return
        try:
            self._program_all()
        except Exception as e:
            print(f"Programming failed: {e}")
            self.status_var.set(f"Loaded cal, but programming the devices failed: {e}")
            return
        self.status_var.set(f"Loaded cal and programmed {len(rows)} element(s)")

    def on_reset(self):
        if not self._connected():
            return
        self.orion_bdst.SYNC_RST.sync_rst = 1
        self.orion_bdst.SYNC_RST.write()
        self.orion_bdst.SYNC_RST.sync_rst = 0
        self.orion_bdst.SYNC_RST.write()

        self.on_load_plank(self.cfg_path, keep_cal_path=True)  # this resets all GUI selections

        self.status_var.set("Plank reset")

if __name__ == "__main__":
    app = App()
    app.mainloop()