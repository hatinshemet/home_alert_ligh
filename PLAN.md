# Home Alert Light System — Project Plan

## Overview

A Python service that polls the Israeli Home Front Command (Pikud HaOref) alert API and controls a Tuya RGB smart bulb to visually indicate alert status in your area.

| Alert Type | Light Behavior |
|---|---|
| Early warning (missile launch detected) | Pulsing **yellow/orange** |
| Immediate siren (Tzeva Adom) | Flashing **red** |
| All-clear / no alert | Light off (or dim white) |

---

## Architecture

```
[Oref0 Alert API] → [Python poller] → [tinytuya] → [Tuya RGB Bulb]
                         ↑
                   (config.yaml)
                  (area filter, device creds)
```

---

## Components

### Hardware
- Raspberry Pi 4 B (final deployment target)
- Tuya RGB+CCT smart bulb (already on Tuya app)

### Software
- **Python 3.10+**
- **tinytuya** — local LAN control of Tuya devices (no cloud round-trip)
- **requests** — polling the alert API
- **PyYAML** — configuration
- **systemd** — auto-start service on the Pi (deployment step)

---

## Alert API

The Home Front Command exposes a public polling endpoint:

```
GET https://www.oref.org.il/WarningMessages/alert/alerts.json
Headers:
  Referer: https://www.oref.org.il/
  X-Requested-With: XMLHttpRequest
```

- Returns an empty body (or `{}`) when there are no active alerts.
- Returns a JSON object with `data` (array of city names) and `cat` (category) when active.

### Alert Categories (`cat` field)
| `cat` | Meaning |
|---|---|
| `1` | Tzeva Adom — immediate rocket/missile (SIREN) |
| `2` | Hostile aircraft intrusion |
| `3` | Earthquake |
| `4` | Hazmat |
| `5` | Tsunami |
| `6` | Unconventional missile (early warning) |
| `13` | General early warning |

For this project: **cat 1 = red flash**, **all others = yellow/amber pulse**.

---

## Project Structure

```
home_alert_light/
├── config.yaml          # device credentials + area filter
├── main.py              # entry point / poll loop
├── alert_client.py      # Oref0 API polling logic
├── light_controller.py  # tinytuya bulb control
├── requirements.txt
└── deploy/
    └── home-alert.service  # systemd unit for the Pi
```

---

## Implementation Steps

### Phase 1 — Local development on Mac

1. **Init project** in this directory.
2. **Install dependencies** in a virtualenv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install tinytuya requests pyyaml
   ```
3. **Extract Tuya device credentials** (Device ID, IP, Local Key):
   - Use `python -m tinytuya wizard` — guides you through Tuya IoT Platform to get the local key.
   - Requires a free Tuya IoT Platform account linked to your SmartLife/Tuya app.
4. **Build `alert_client.py`** — polls the API every 2–3 seconds, filters by your city/area.
5. **Build `light_controller.py`** — maps alert state to bulb color/flash pattern using tinytuya.
6. **Build `main.py`** — poll loop + state machine (idle -> early warning -> siren -> cooldown).
7. **Test on Mac** (mock the API response or use a city with a live alert from the history endpoint).

### Phase 2 — Deploy to Raspberry Pi

1. **Transfer files** via rsync:
   ```bash
   rsync -avz home_alert_light/ pi@<PI_IP>:~/home_alert_light/
   ```
2. **On the Pi**, set up the virtualenv and install dependencies (same as Phase 1, Step 2).
3. **Ensure the Pi and bulb are on the same LAN** (required for tinytuya local control).
4. **Install the systemd service** so it runs on boot:
   ```bash
   sudo cp deploy/home-alert.service /etc/systemd/system/
   sudo systemctl enable home-alert
   sudo systemctl start home-alert
   ```
5. **Verify** with `journalctl -u home-alert -f`.

---

## Configuration (`config.yaml`)

```yaml
area:
  cities:
    - "תל אביב - מרכז"    # your city in Hebrew, as it appears in the API
    - "רמת גן"

poll_interval_seconds: 2

tuya:
  device_id: "your_device_id"
  device_ip: "192.168.x.x"      # bulb's LAN IP (set static DHCP lease)
  local_key: "your_local_key"
  version: 3.3                   # usually 3.3 or 3.4

light:
  siren_color:         [255, 0, 0]     # red
  early_warning_color: [255, 140, 0]   # orange/amber
  flash_interval_seconds: 0.5
  cooldown_seconds: 120                # keep light on N seconds after alert clears
```

---

## State Machine

```
IDLE
  |  alert detected (filtered by city)
  v
EARLY_WARNING  (cat != 1)  --> amber pulse
  |  cat becomes 1 OR new siren alert
  v
SIREN          (cat == 1)  --> red flash
  |  alert clears (empty response)
  v
COOLDOWN       --> slow dim red for cooldown_seconds
  |  timer expires
  v
IDLE           --> light off
```

---

## Key Decisions & Trade-offs

| Decision | Rationale |
|---|---|
| **tinytuya local LAN** vs Tuya cloud API | Local is faster (~ms vs ~1-2s) and works without internet |
| **Polling** vs WebSocket | Oref0 has no public WebSocket; polling at 2-3s matches the app behavior |
| **Python** | Best library support (tinytuya), runs well on Pi, easy to iterate on Mac |
| **systemd** | Standard, reliable auto-start on Pi with crash recovery |

---

## Prerequisites Before Coding

- [ ] Create a free Tuya IoT Platform account (iot.tuya.com)
- [ ] Link your SmartLife app to the platform (Cloud -> Development -> Link App Account)
- [ ] Run `python -m tinytuya wizard` to discover device ID, IP, and local key
- [ ] Confirm your city name in Hebrew via the Oref0 history API:
      `https://www.oref.org.il/WarningMessages/History/AlertsHistory.json`
- [ ] Set a static DHCP lease for the bulb's IP on your router (recommended)

---

## Next Steps

Start with **Phase 1, Step 3** (Tuya credentials) — it's the longest external dependency.
Once you have the device credentials, the rest of the code can be built and tested quickly on your Mac.
