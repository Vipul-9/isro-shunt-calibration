import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from main import run_calibration, PIN_MAP
from hardware.shunt_controller import ShuntController


class LinearityPlot(tk.Canvas):
    """Canvas plot of measured vs expected bridge voltage."""

    def __init__(self, master, width=600, height=400, **kwargs):
        super().__init__(master, width=width, height=height, bg="white", **kwargs)
        self.width, self.height = width, height
        self.expected, self.measured = [], []
        self.margin = 50
        self.create_text(self.width / 2, 20, text="Linearity Plot", font=("Arial", 14, "bold"))
        self.create_line(self.margin, self.height - 40, self.width - 20, self.height - 40)  # X-axis
        self.create_line(self.margin, 40, self.margin, self.height - 40)                    # Y-axis

    def update_plot(self, expected, measured):
        self.expected, self.measured = expected, measured
        self.delete("points")
        if not expected:
            return
        max_x, max_y = max(expected), max(measured)
        scale_x = (self.width - 2 * self.margin) / max_x if max_x != 0 else 1
        scale_y = (self.height - 80) / max_y if max_y != 0 else 1
        prev_x, prev_y = None, None
        for ex, me in zip(expected, measured):
            x = int(self.margin + ex * scale_x)
            y = int(self.height - 40 - me * scale_y)
            self.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue", tags="points")
            if prev_x is not None:
                self.create_line(prev_x, prev_y, x, y, fill="red", tags="points")
            prev_x, prev_y = x, y

    def save_plot(self, filename="plot.ps"):
        self.postscript(file=filename)


class CalibrationGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shunt Calibration")
        self.geometry("800x600")
        self.mode = tk.StringVar(value="manual")
        self.output = tk.Text(self, height=15)
        self.output.pack()
        tk.Radiobutton(self, text="Manual", variable=self.mode, value="manual").pack()
        tk.Radiobutton(self, text="Automatic", variable=self.mode, value="auto").pack()
        tk.Button(self, text="Start Calibration", command=self.start_calibration).pack()
        tk.Button(self, text="Test Relays", command=self.test_relays).pack()
        self.plot_widget = LinearityPlot(self)
        self.plot_widget.pack()

    # Called by the calibration engine; keeps main.py independent of tkinter
    def gui_callback(self, action, *args):
        if action == "log":
            self.log(args[0])
        elif action == "ask_filename":
            filename = simpledialog.askstring("Save As", "Enter CSV filename:")
            if filename and not filename.endswith(".csv"):
                filename += ".csv"
            return filename
        elif action == "ask_shunt":
            return simpledialog.askstring("Shunt Selection", "Enter relay (R1-R5):")
        elif action == "ask_voltage":
            return float(simpledialog.askstring("Voltage Input", f"Enter measured voltage for {args[0]}:"))
        elif action == "ask_continue":
            return messagebox.askyesno("Continue?", "Calibrate another shunt?")
        elif action == "update_plot":
            self.plot_widget.update_plot(args[0], args[1])
            self.update_idletasks()
        elif action == "save_plot":
            self.plot_widget.save_plot(args[0].replace(".csv", ".ps"))

    def log(self, msg):
        self.output.insert(tk.END, f"{msg}\n")
        self.output.see(tk.END)
        self.update_idletasks()

    def start_calibration(self):
        self.log("Starting calibration...")
        run_calibration(mode=self.mode.get(), gui_callback=self.gui_callback)

    def test_relays(self):
        controller = ShuntController(PIN_MAP)
        for shunt in PIN_MAP:
            self.log(f"Activating {shunt}...")
            controller.activate(shunt)
            time.sleep(0.5)
            controller.deactivate_all()
        controller.cleanup()
        self.log("Relay test complete.")


if __name__ == "__main__":
    app = CalibrationGUI()
    app.mainloop()
