"""
Simulates an alert flow without waiting for a real alert.
Runs through: early warning -> siren -> cooldown -> idle
"""
import time
import threading
import yaml
from light_controller import LightController

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)
with open("secrets.yaml", encoding="utf-8") as f:
    config.update(yaml.safe_load(f))

# Shorten cooldown for the test
config["light"]["cooldown_seconds"] = 10

light = LightController(config)
flash_interval = config["light"]["flash_interval_seconds"]


def flash(color, stop_event):
    on = True
    while not stop_event.is_set():
        if on:
            light.set_color(*color)
        else:
            light.turn_off()
        on = not on
        stop_event.wait(flash_interval)


stop = threading.Event()
thread = None


def start_flash(color):
    global stop, thread
    stop.set()
    if thread:
        thread.join()
    stop = threading.Event()
    thread = threading.Thread(target=flash, args=(color, stop), daemon=True)
    thread.start()


def stop_flash():
    global thread
    stop.set()
    if thread:
        thread.join()
        thread = None


print("--- Simulating EARLY WARNING (orange, 5s) ---")
start_flash(config["light"]["early_warning_color"])
time.sleep(5)

print("--- Simulating SIREN (red, 5s) ---")
start_flash(config["light"]["siren_color"])
time.sleep(5)

print("--- Simulating COOLDOWN (dim red, 10s) ---")
stop_flash()
light.set_dim_red()
time.sleep(10)

print("--- All clear — light off ---")
light.turn_off()
print("Done.")
