"""
Query the Dominos Canada order tracker by phone number.

Reads contacts from config.toml and store names from stores.toml.
Steps:
1. Load config and persisted order state (order ID -> last known status)
2. Poll each contact's orders
3. For each new order or status change, send a Pushover notification
4. Persist updated state
"""

import json
import time
import tomllib
import uuid
from pathlib import Path

import requests

BASE_URL = "https://api.dominos.ca/tracker-presentation-service"
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
STATE_FILE = Path("state.json")

_DPZ_D = str(uuid.uuid4())

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
    "Accept": "application/json",
    "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
    "Market": "CANADA",
    "DPZ-Language": "en",
    "DPZ-Market": "CANADA",
    "X-DPZ-D": _DPZ_D,
    "Cookie": f"X-DPZ-D={_DPZ_D}; AKA_A2=A",
}


def list_orders(phone: str) -> list[dict]:
    """Return all recent orders for a phone number."""
    params = {
        "phonenumber": phone,
        "_": int(time.time() * 1000),
    }
    response = requests.get(f"{BASE_URL}/v2/orders", params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_order_detail(track_path: str) -> dict:
    """Fetch granular status for one order using the Actions.Track path."""
    response = requests.get(f"{BASE_URL}{track_path}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def send_notification(user_key: str, app_token: str, title: str, message: str) -> None:
    response = requests.post(
        PUSHOVER_URL,
        data={
            "token": app_token,
            "user": user_key,
            "title": title,
            "message": message,
        },
    )
    response.raise_for_status()


def load_state() -> dict[str, str]:
    """Return a mapping of order ID to last known status."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict[str, str]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def poll(config: dict) -> None:
    stores: dict[str, str] = config.get("stores", {})
    pushover = config.get("pushover")
    state = load_state()

    for contact in config["contacts"]:
        orders = list_orders(contact["phone"])
        if not orders:
            continue
        print(f"=== {contact['name']} ===")
        for order in orders:
            order_id = order["OrderID"]
            store_name = stores.get(order.get("StoreID", ""), order.get("StoreID", ""))
            print(f"Store: {store_name}  |  {order['OrderDescription']}")

            if track_path := order.get("Actions", {}).get("Track"):
                detail = get_order_detail(track_path)
                status = detail.get("OrderStatus", "Unknown")
                print(f"Status: {status}")

                last_status = state.get(order_id)
                if status != last_status:
                    if pushover:
                        title = (
                            f"New Dominos order for {contact['name']}"
                            if last_status is None
                            else f"Order update for {contact['name']}"
                        )
                        send_notification(
                            pushover["user_key"],
                            pushover["app_token"],
                            title=title,
                            message=f"{store_name}: {order['OrderDescription']}\nStatus: {status}",
                        )
                        print(f"Notification sent: {last_status!r} -> {status!r}")
                    state[order_id] = status

    save_state(state)


def main() -> None:
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    interval = config.get("poll", {}).get("interval_minutes", 2) * 60

    pushover = config.get("pushover")
    backoff = 0
    MAX_BACKOFF = 30 * 60

    while True:
        print(f"--- Polling at {time.strftime('%H:%M:%S')} ---")
        try:
            poll(config)
            backoff = 0
            sleep_secs = interval
        except Exception as e:
            print(f"Error: {e}")
            if pushover:
                send_notification(
                    pushover["user_key"],
                    pushover["app_token"],
                    title="Dominos tracker error",
                    message=str(e),
                )
            backoff = min(MAX_BACKOFF, backoff * 2 if backoff else 30)
            sleep_secs = backoff
            print(f"Backing off for {sleep_secs}s...")

        print(f"Sleeping {sleep_secs}s...")
        time.sleep(sleep_secs)


if __name__ == "__main__":
    main()
