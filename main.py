import time
import threading
import yaml
from alert_client import AlertClient
from light_controller import LightController


IDLE = "idle"
EARLY_WARNING = "early_warning"
SIREN = "siren"
COOLDOWN = "cooldown"


def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open("secrets.yaml", encoding="utf-8") as f:
        config.update(yaml.safe_load(f))

    client = AlertClient(config)
    light = LightController(config)

    state = IDLE
    cooldown_until = 0
    flash_thread = None
    stop_flash = threading.Event()

    def start_flash(color, interval):
        nonlocal flash_thread, stop_flash
        stop_flash.set()
        if flash_thread:
            flash_thread.join()
        stop_flash = threading.Event()

        def _flash(stop):
            on = True
            while not stop.is_set():
                if on:
                    light.set_color(*color)
                else:
                    light.turn_off()
                on = not on
                stop.wait(interval)

        flash_thread = threading.Thread(target=_flash, args=(stop_flash,), daemon=True)
        flash_thread.start()

    def stop_flashing():
        nonlocal flash_thread
        stop_flash.set()
        if flash_thread:
            flash_thread.join()
            flash_thread = None

    siren_color = config["light"]["siren_color"]
    warning_color = config["light"]["early_warning_color"]
    flash_interval = config["light"]["flash_interval_seconds"]
    cooldown_secs = config["light"]["cooldown_seconds"]
    poll_interval = config["poll_interval_seconds"]

    print("Home alert light running. Press Ctrl+C to stop.")

    while True:
        alert = client.get_active_alert()

        if alert:
            cat = str(alert.get("cat", ""))
            is_siren = cat == "1"
            cities = alert.get("data", [])
            print(f"[alert] cat={cat} cities={cities}")

            if is_siren:
                if state != SIREN:
                    print("[state] -> SIREN (red flash)")
                    state = SIREN
                    start_flash(siren_color, flash_interval)
            else:
                if state not in (SIREN, EARLY_WARNING):
                    print("[state] -> EARLY_WARNING (orange pulse)")
                    state = EARLY_WARNING
                    start_flash(warning_color, flash_interval)
        else:
            if state in (SIREN, EARLY_WARNING):
                print(f"[state] -> COOLDOWN ({cooldown_secs}s)")
                state = COOLDOWN
                cooldown_until = time.time() + cooldown_secs
                stop_flashing()
                light.set_dim_red()
            elif state == COOLDOWN:
                if time.time() >= cooldown_until:
                    print("[state] -> IDLE (light off)")
                    state = IDLE
                    light.turn_off()

        time.sleep(poll_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
