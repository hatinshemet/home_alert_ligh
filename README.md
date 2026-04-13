# Home Alert Light

A Python service that listens to Israeli Home Front Command (Pikud HaOref) alerts and controls a Tuya RGB smart bulb to give a visual indication when there is an alert in your area.

| Alert Type | Light |
|---|---|
| Immediate siren (Tzeva Adom) | Flashing red |
| Early warning (all other categories) | Flashing orange |
| Cooldown (alert just cleared) | Dim red for 2 minutes |
| No alert | Off |

## Hardware Requirements

- A Tuya-compatible RGB smart bulb connected to your local WiFi via the SmartLife or Tuya Smart app
- Any computer on the same local network (developed for Raspberry Pi 4 B)

## Prerequisites

- Python 3.10+
- A free [Tuya IoT Platform](https://platform.tuya.com) account linked to your SmartLife app
- Your bulb's **Device ID**, **local IP address**, and **local key** (see Setup below)

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd home_alert_ligh
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Get your Tuya device credentials

Run the tinytuya wizard — it will scan your local network and fetch the local key from the Tuya platform:

```bash
python -m tinytuya wizard
```

You will need:
- **API Key / Access ID** — from your Tuya IoT Platform project Overview page
- **API Secret** — from the same page
- **Region** — `eu` for Central Europe, `eu-w` for Western Europe, `us` for Americas

The wizard will output your device's ID, IP address, and local key.

### 4. Create your secrets file

```bash
cp secrets.yaml.example secrets.yaml
```

Edit `secrets.yaml` and fill in your device credentials:

```yaml
tuya:
  device_id: "your_device_id"
  device_ip: "192.168.x.x"
  local_key: "your_local_key"
  version: 3.5
```

> `secrets.yaml` is gitignored and will never be committed.

### 5. Set your city

Open `config.yaml` and set your city name in Hebrew, exactly as it appears in the Oref system. You can find the correct spelling by checking:

```
https://www.oref.org.il/WarningMessages/History/AlertsHistory.json
```

```yaml
area:
  cities:
    - "תל אביב - מרכז"   # replace with your city
```

### 6. Run

```bash
python main.py
```

The service will poll for alerts every 2 seconds and control the light automatically.

## Deploying to Raspberry Pi

Transfer the files (excluding `venv/` and `secrets.yaml`):

```bash
rsync -avz --exclude venv --exclude secrets.yaml . pi@<PI_IP>:~/home_alert_ligh/
```

Then on the Pi, copy your secrets file manually:

```bash
scp secrets.yaml pi@<PI_IP>:~/home_alert_ligh/secrets.yaml
```

Set up the virtualenv on the Pi:

```bash
cd ~/home_alert_ligh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run as a background service (auto-start on boot)

Create `/etc/systemd/system/home-alert.service`:

```ini
[Unit]
Description=Home Alert Light
After=network.target

[Service]
WorkingDirectory=/home/pi/home_alert_ligh
ExecStart=/home/pi/home_alert_ligh/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```bash
sudo systemctl enable home-alert
sudo systemctl start home-alert
sudo journalctl -u home-alert -f   # view logs
```

## Configuration

All non-sensitive settings are in `config.yaml`:

| Key | Description | Default |
|---|---|---|
| `area.cities` | List of Hebrew city names to monitor | — |
| `poll_interval_seconds` | How often to check for alerts | `2` |
| `light.siren_color` | RGB color for immediate siren | `[255, 0, 0]` (red) |
| `light.early_warning_color` | RGB color for early warnings | `[255, 140, 0]` (orange) |
| `light.flash_interval_seconds` | Flash on/off speed | `0.5` |
| `light.cooldown_seconds` | How long to show dim red after alert clears | `120` |

## Alert Categories

The service uses the public Oref0 API (`www.oref.org.il`). Alert category `1` (Tzeva Adom) triggers the red siren mode. All other categories trigger the orange early warning mode.

## License

MIT
