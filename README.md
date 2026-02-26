# OSINT – Minimal X (Twitter) Stream Connector (Python)

A tiny, easy-to-adapt connector that streams X (Twitter) data and writes each event to a **JSONL** log file (one JSON object per line).  
Built to be a minimal starting point you can copy and extend for your own OSINT pipelines.

---

## Quick start

### 1) Install dependencies

This project intentionally keeps dependencies minimal. You only need:

```bash
pip install requests
```

### 2) Add your Bearer Token (required)

Create / edit `config.py` and insert your X API Bearer Token:

```python
X_TOKEN = "YOUR_BEARER_TOKEN_HERE"
```

> Without a valid token, authentication will fail.

### 3) Run the stream

```bash
python3 x-simple-btc-stream.py
```

---

## What it does

- **(Re)sets a stream rule** (tagged as `btc_bitcoin_stream`)
- Opens the **X API v2 filtered stream**
- Logs every incoming event to a timestamped file:
  - `x_stream_YYYYMMDD_HHMMSS.jsonl`
- Prints short status/output to the console while running

JSONL is ideal for later ingestion into databases (Postgres, ClickHouse, SQLite) or data processing tools.

---

## Notes / Troubleshooting

- **API base URL:** the code uses `https://api.x.com/2`. Depending on your account/app configuration, `https://api.twitter.com/2` may also work (see comment in code).
- **Disconnects / rate limits:** the script includes retry/backoff logic. If you see repeated failures, verify:
  - Token is correct
  - Your app has access to the endpoints used
  - Your stream rule is accepted by the API

---

## Repository goal

A **minimal connector** that anyone can copy, run by only adding a token, and then adapt for:

- new rules/keywords
- more fields/expansions
- database ingestion
- additional OSINT sources

---

## License

MIT
