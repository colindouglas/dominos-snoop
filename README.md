# Domino's Snoop

Did you know that the API for the Domino's pizza tracker is completely open and you
can check on the order status of anyone who's phone number you know?

Oh, you did?

Yeah, me too.

## Setup

Copy the example config and fill in your details:

```toml
[[contacts]]
name = "Alice"
phone = "4165551234"

[[contacts]]
name = "Bob"
phone = "6475554321"

[stores]
"10101" = "Yonge Street"

[pushover]
user_key = "uXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
app_token = "aXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

[poll]
interval_minutes = 2
```

- **contacts**: one entry per phone number to track
- **stores**: optional friendly names for store IDs (falls back to the raw ID if not listed)
- **pushover**: credentials from [pushover.net](https://pushover.net) — omit the section to disable notifications
- **poll.interval_minutes**: how often to check (default: 2)

## Docker

Place `config.toml` in your appdata folder, then mount it at `/data`:

```bash
docker build -t dominos-snoop .
docker run -v /mnt/user/appdata/dominos-snoop:/data dominos-snoop
```

`state.json` will be created automatically in the same folder on first run. The `DATA_DIR` env var controls the data path (default: `/data` in the container, `.` when running locally).
