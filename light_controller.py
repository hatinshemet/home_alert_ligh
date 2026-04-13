import tinytuya


class LightController:
    def __init__(self, config):
        t = config["tuya"]
        self.device = tinytuya.BulbDevice(
            dev_id=t["device_id"],
            address=t["device_ip"],
            local_key=t["local_key"],
            version=t["version"],
        )
        self.device.set_socketPersistent(True)

    def set_color(self, r, g, b):
        try:
            self.device.set_colour(r, g, b)
        except Exception as e:
            print(f"[light] set_color error: {e}")

    def set_dim_red(self):
        try:
            self.device.set_colour(80, 0, 0)
        except Exception as e:
            print(f"[light] set_dim_red error: {e}")

    def turn_off(self):
        try:
            self.device.turn_off()
        except Exception as e:
            print(f"[light] turn_off error: {e}")
