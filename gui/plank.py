import tkinter as tk
from tkinter import ttk
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
        ttk.Button(self.calib_sidebar, text="Program Defaults", command=self.on_program_defaults).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Save Cal", command=self.on_save_cal).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Load Cal", command=self.on_load_cal).pack(fill="x", pady=5)

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
    def on_program_defaults(self):
        for controls in self.element_controls.values():
            controls["bias"].set(127)
            controls["gain"].set(0)
            controls["phase"].set(4)
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

    def on_sanity(self):
        self.status_var.set("Sanity check")

    def on_load_plank(self):
        self.mapping = self.load_element_map("plank1.cfg")
        self.populate_calibration_table()
        self.status_var.set("Plank loaded")

    def on_save_cal(self):
        with open("plank1.cal", "w", newline="") as f:
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
            with open("plank1.cal") as f:
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


if __name__ == "__main__":
    app = App()
    app.mainloop()