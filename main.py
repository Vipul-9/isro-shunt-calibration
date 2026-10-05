import json
import time
from hardware.shunt_controller import ShuntController
from hardware.adc_reader import get_voltage
from model.bridge_model import compute_expected_voltage
from model.comparator import compare
from logger.logger import log_result, log_header

PIN_MAP = {"R1": 17, "R2": 18, "R3": 27, "R4": 22, "R5": 23}


def calibrate_one(shunt, Rs, config, controller, gui_callback):
    # Activate the specified shunt via GPIO-controlled relays
    controller.activate(shunt)
    time.sleep(config["settle_delay"])  # allow the bridge to settle

    # Measurement source: ADC or manual GUI input
    if config.get("use_adc", False):
        measured = get_voltage(shunt=shunt, fsr=config.get("adc_fsr", 2.048))
    else:
        measured = gui_callback("ask_voltage", shunt)

    # Expected bridge output from the model
    expected = compute_expected_voltage(config["Vexc"], config["Rg"], Rs)

    # Compare against tolerance
    error, flag = compare(expected, measured, config["tolerance"])

    msg = f"{shunt}: Expected={expected:.6f}, Measured={measured:.6f}, Error={error:.6f} - {flag}"
    gui_callback("log", msg)
    return measured, expected, error, flag


def run_calibration(mode="auto", gui_callback=None):
    with open("config/config.json") as f:
        config = json.load(f)

    controller = ShuntController(PIN_MAP)
    Rs_dict = config["Rs"]
    expected_list, measured_list = [], []

    try:
        log_file = gui_callback("ask_filename")
        if not log_file:
            gui_callback("log", "Calibration cancelled.")
            return
        log_header(log_file)

        if mode == "auto":
            # Sequentially calibrate all shunts
            for shunt, Rs in Rs_dict.items():
                measured, expected, error, flag = calibrate_one(shunt, Rs, config, controller, gui_callback)
                log_result(log_file, [shunt, expected, measured, error, flag])
                expected_list.append(expected)
                measured_list.append(measured)
                gui_callback("update_plot", expected_list, measured_list)
        else:
            # Manual mode: operator picks each shunt
            while True:
                shunt = gui_callback("ask_shunt")
                if shunt not in Rs_dict:
                    gui_callback("log", f"Unknown relay '{shunt}'. Use R1-R5.")
                    if not gui_callback("ask_continue"):
                        break
                    continue
                Rs = Rs_dict[shunt]
                measured, expected, error, flag = calibrate_one(shunt, Rs, config, controller, gui_callback)
                log_result(log_file, [shunt, expected, measured, error, flag])
                expected_list.append(expected)
                measured_list.append(measured)
                gui_callback("update_plot", expected_list, measured_list)
                if not gui_callback("ask_continue"):
                    break

        gui_callback("save_plot", log_file)

    finally:
        controller.cleanup()
        gui_callback("log", "Calibration complete. GPIO cleanup done.")
