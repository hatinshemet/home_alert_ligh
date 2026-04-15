"""
Quick test to verify tinytuya can control the bulb.
Cycles through: red flash -> orange -> dim red -> off
"""
import time
import yaml
from light_controller import LightController

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)
with open("secrets.yaml", encoding="utf-8") as f:
    config.update(yaml.safe_load(f))

light = LightController(config)

print("Testing SIREN color (red)...")
for _ in range(4):
    light.set_color(255, 0, 0)
    time.sleep(0.5)
    light.turn_off()
    time.sleep(0.5)

print("Testing EARLY WARNING color (orange)...")
for _ in range(4):
    light.set_color(255, 140, 0)
    time.sleep(0.5)
    light.turn_off()
    time.sleep(0.5)

print("Testing COOLDOWN (dim red)...")
light.set_dim_red()
time.sleep(3)

print("Turning off...")
light.turn_off()
print("Done.")
