import tkinter as tk
from tkinter import ttk
import csv

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Tabbed GUI App")
        self.geometry("1000x650")

        # --- Theme ---
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # --- Layout ---
        self._create_layout()

        # --- Tabs ---
        self._create_tabs()

        # --- Status Bar ---
        self._create_status_bar()

    # =========================
    # Main Layout
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

        # Build calibration layout
        self._build_calibration_tab()

    # =========================
    # Calibration Tab Layout
    # =========================
    def _build_calibration_tab(self):
        # Make tab expandable
        self.tab_calibration.grid_rowconfigure(0, weight=1)
        self.tab_calibration.grid_columnconfigure(0, weight=1)

        # --- Paned Window ---
        self.paned = ttk.PanedWindow(self.tab_calibration, orient="horizontal")
        self.paned.grid(row=0, column=0, sticky="nsew")

        # --- Sidebar ---
        self.calib_sidebar = ttk.Frame(
            self.paned,
            padding=10,
            relief="solid",
            borderwidth=1
        )

        # --- Main Area ---
        self.calib_main = ttk.Frame(
            self.paned,
            padding=10,
            relief="solid",
            borderwidth=1
        )

        # Add panes
        self.paned.add(self.calib_sidebar, weight=1)
        self.paned.add(self.calib_main, weight=4)

        # =========================
        # Sidebar Content (Buttons)
        # =========================
        ttk.Button(self.calib_sidebar, text="Sanity", command=self.on_sanity).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Load Plank Cfg", command=self.on_load_plank).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Program Defaults", command=self.on_program_defaults).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Save Cal", command=self.on_save_cal).pack(fill="x", pady=5)
        ttk.Button(self.calib_sidebar, text="Load Cal", command=self.on_load_cal).pack(fill="x", pady=5)

        # Placeholder main area
        ttk.Label(self.calib_main, text="Main Area").pack()

    def populate_calibration_table(self):
        # Clear previous content
        for widget in self.calib_main.winfo_children():
            widget.destroy()

        self.element_controls = {}

        # ---- Header Row ----
        headers = [
            "Element", "BFM", "CH",
            "Cal PA", "Cal LNA", "Cal Gain", "Cal Phase",
            "PA", "LNA", "Gain", "Phase"
        ]

        for col, text in enumerate(headers):
            ttk.Label(self.calib_main, text=text, font=("Arial", 10, "bold")) \
                .grid(row=0, column=col, padx=4, pady=5)

        # ---- Data Rows ----
        for row_idx, entry in enumerate(self.mapping["list"], start=1):
            element_id = entry["element_id"]
            bfm_id = entry["bfm_id"]
            ch_id = entry["ch_id"]

            # Labels
            ttk.Label(self.calib_main, text=str(element_id)).grid(row=row_idx, column=0, padx=4)
            ttk.Label(self.calib_main, text=hex(bfm_id)).grid(row=row_idx, column=1, padx=4)
            ttk.Label(self.calib_main, text=str(ch_id)).grid(row=row_idx, column=2, padx=4)

            # ---- Variables ----
            vars_dict = {
                "cal_pa_bias": tk.IntVar(value=0),
                "cal_lna_bias": tk.IntVar(value=0),
                "cal_gain": tk.IntVar(value=0),
                "cal_phase": tk.IntVar(value=0),
                "pa_bias": tk.IntVar(value=0),
                "lna_bias": tk.IntVar(value=0),
                "gain": tk.IntVar(value=0),
                "phase": tk.IntVar(value=0),
            }

            for name, var in vars_dict.items():
                self.attach_callback(var, element_id, name)

            # ---- Calibrated Set ----
            # ---- Calibrated Set (LABELS now) ----
            ttk.Label(self.calib_main, textvariable=vars_dict["cal_pa_bias"]) \
                .grid(row=row_idx, column=3, padx=4)

            ttk.Label(self.calib_main, textvariable=vars_dict["cal_lna_bias"]) \
                .grid(row=row_idx, column=4, padx=4)

            ttk.Label(self.calib_main, textvariable=vars_dict["cal_gain"]) \
                .grid(row=row_idx, column=5, padx=4)

            ttk.Label(self.calib_main, textvariable=vars_dict["cal_phase"]) \
                .grid(row=row_idx, column=6, padx=4)

            # ---- Normal Set ----
            ttk.Spinbox(self.calib_main, from_=0, to=255, textvariable=vars_dict["pa_bias"], width=5) \
                .grid(row=row_idx, column=7, padx=4)

            ttk.Spinbox(self.calib_main, from_=0, to=255, textvariable=vars_dict["lna_bias"], width=5) \
                .grid(row=row_idx, column=8, padx=4)

            ttk.Spinbox(self.calib_main, from_=0, to=63, textvariable=vars_dict["gain"], width=5) \
                .grid(row=row_idx, column=9, padx=4)

            ttk.Spinbox(self.calib_main, from_=4, to=124, textvariable=vars_dict["phase"], width=5) \
                .grid(row=row_idx, column=10, padx=4)

            # Store everything
            self.element_controls[element_id] = vars_dict

    # =========================
    # Global Status Bar
    # =========================
    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")

        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.grid(row=1, column=0, sticky="ew")

    # Helper Functions
    def attach_callback(self, var, element_id, field_name):
        def callback(*args):
            try:
                value = var.get()
            except Exception:
                return  # ignore invalid/empty intermediate state

            self.on_spinbox_change(element_id, field_name, value)

        var.trace_add("write", callback)

    def load_element_map(self, csv_path):
        data = []
        by_element = {}
        by_bfm = {}

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                entry = {
                    "element_id": int(row["element_id"]),
                    "bfm_id": int(row["bfm_id"], 16),  # hex → int
                    "ch_id": int(row["ch_id"])
                }

                data.append(entry)

                # Index by element
                by_element[entry["element_id"]] = entry

                # Group by BFM
                bfm = entry["bfm_id"]
                if bfm not in by_bfm:
                    by_bfm[bfm] = []
                by_bfm[bfm].append(entry)

        return {
            "list": data,
            "by_element": by_element,
            "by_bfm": by_bfm
        }

    # Handlers
    def on_program_defaults(self):
        self.status_var.set("Programming default values...")

        for element_id, controls in self.element_controls.items():
            controls["pa_bias"].set(127)
            controls["lna_bias"].set(127)
            controls["gain"].set(0)
            controls["phase"].set(4)

        self.status_var.set("Defaults programmed")

    def on_spinbox_change(self, element_id, field_name, value):
        # Clamp values
        if "phase" in field_name:
            value = max(4, min(124, value))
        elif "gain" in field_name:
            value = max(0, min(63, value))
        else:  # bias
            value = max(0, min(255, value))

        # Write back corrected value
        self.element_controls[element_id][field_name].set(value)

        self.status_var.set(f"E{element_id} {field_name} → {value}")

    def on_sanity(self):
        self.status_var.set("Running sanity check...")

    def on_load_plank(self):
        try:
            self.status_var.set("Loading plank configuration...")
            self.mapping = self.load_element_map('plank1.cfg')
            self.populate_calibration_table()
            self.status_var.set("Plank configuration loaded successfully")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

    def on_save_cal(self):
        if not hasattr(self, "mapping") or not hasattr(self, "element_controls"):
            self.status_var.set("No calibration data to save")
            return

        file_path = "plank1.cal"

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    "element_id", "bfm_id", "ch_id",
                    "pa_bias", "lna_bias", "gain", "phase"
                ])

                # Data rows
                for entry in self.mapping["list"]:
                    element_id = entry["element_id"]
                    bfm_id = entry["bfm_id"]
                    ch_id = entry["ch_id"]

                    controls = self.element_controls[element_id]

                    writer.writerow([
                        element_id,
                        hex(bfm_id),
                        ch_id,
                        controls["pa_bias"].get(),
                        controls["lna_bias"].get(),
                        controls["gain"].get(),
                        controls["phase"].get()
                    ])

            self.status_var.set(f"Calibration saved to {file_path}")

        except Exception as e:
            self.status_var.set(f"Error saving file: {str(e)}")

    def on_load_cal(self):
        file_path = "plank1.cal"

        if not hasattr(self, "element_controls"):
            self.status_var.set("UI not initialized")
            return

        try:
            with open(file_path, "r") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    element_id = int(row["element_id"])

                    if element_id not in self.element_controls:
                        continue

                    controls = self.element_controls[element_id]

                    # Update CAL (label-backed variables)
                    controls["cal_pa_bias"].set(int(row["pa_bias"]))
                    controls["cal_lna_bias"].set(int(row["lna_bias"]))
                    controls["cal_gain"].set(int(row["gain"]))
                    controls["cal_phase"].set(int(row["phase"]))

            self.status_var.set("Calibration loaded successfully")

        except FileNotFoundError:
            self.status_var.set(f"{file_path} not found")

        except Exception as e:
            self.status_var.set(f"Error loading file: {str(e)}")


# =========================
# Run
# =========================
if __name__ == "__main__":
    app = App()
    app.mainloop()