import requests


class AlertClient:
    API_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
    HEADERS = {
        "Referer": "https://www.oref.org.il/",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
    }

    def __init__(self, config):
        self.cities = set(config["area"]["cities"])

    def get_active_alert(self):
        """Returns the alert dict if there is an active alert in our cities, else None."""
        try:
            resp = requests.get(self.API_URL, headers=self.HEADERS, timeout=5)
            text = resp.text.strip()
            if not text or text == "{}":
                return None
            data = resp.json()
            if not data or "data" not in data:
                return None
            alert_cities = set(data.get("data", []))
            if self.cities & alert_cities:
                return data
            return None
        except Exception:
            return None
