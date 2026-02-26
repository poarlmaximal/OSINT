#!/usr/bin/env python3
# Live X (Twitter) v2 Filtered Stream -> JSONL logfile (for later DB/OSINT analysis)
# config.py must define: BEARER_TOKEN = "xxxxx"

import json, time, requests
from datetime import datetime
from pathlib import Path
from config import X_TOKEN

BASE = "https://api.x.com/2"  # for some accounts it may be api.twitter.com
RULES = f"{BASE}/tweets/search/stream/rules"
STREAM = f"{BASE}/tweets/search/stream"

# X search is case-insensitive, so BTC/btc/Bitcoin/bitcoin is covered by these terms.
QUERY = '(BTC OR Bitcoin OR "₿") -is:retweet -is:reply'  # drop replies/RTs to reduce noise/cost
TAG = "btc_bitcoin_stream"

# Request rich metadata in ONE stream call (cost-sparing vs many lookups later).
PARAMS = {
    "tweet.fields": "id,text,created_at,lang,author_id,conversation_id,public_metrics,geo,entities,context_annotations,source",
    "expansions": "author_id,geo.place_id,referenced_tweets.id,referenced_tweets.id.author_id",
    "user.fields": "id,name,username,created_at,description,location,verified,public_metrics,entities,url",
    "place.fields": "full_name,id,country,country_code,geo,name,place_type",
}

H = {"Authorization": f"Bearer {X_TOKEN}", "Content-Type": "application/json"}

def upsert_rule():
    """Delete existing rule with same TAG, then add ours (keeps your account rules tidy)."""
    r = requests.get(RULES, headers=H, timeout=20); r.raise_for_status()
    existing = [x["id"] for x in r.json().get("data", []) if x.get("tag") == TAG]
    if existing:
        d = requests.post(RULES, headers=H, json={"delete": {"ids": existing}}, timeout=20); d.raise_for_status()
    a = requests.post(RULES, headers=H, json={"add": [{"value": QUERY, "tag": TAG}]} , timeout=20); a.raise_for_status()

def stream_to_log():
    """Connect once; write every payload as one JSON line (JSONL) for later parsing/import."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = Path(f"x_stream_{ts}.jsonl").resolve()
    print(f"Logging to: {log}")

    backoff = 1
    while True:
        try:
            with requests.get(STREAM, headers=H, params=PARAMS, stream=True, timeout=(10, 90)) as r:
                r.raise_for_status(); backoff = 1
                with log.open("a", encoding="utf-8") as f:
                    for line in r.iter_lines():
                        if not line:  # keep-alives
                            continue
                        obj = json.loads(line.decode("utf-8"))
                        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        data = obj.get("data", {})
                        print(f'{data.get("created_at","")} @{data.get("author_id","")}: {data.get("text","")[:120]}')
        except KeyboardInterrupt:
            print("\nStopped."); return
        except Exception as e:
            print(f"Stream error: {e} (retry in {backoff}s)")
            time.sleep(backoff); backoff = min(backoff * 2, 60)

if __name__ == "__main__":
    upsert_rule()
    stream_to_log()
