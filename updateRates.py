#!/usr/bin/env python3
#
# import_and_set_rates.py
#
# Fetches EUR→all exchange rates and writes:
#   • /exchangeRates/latest
#   • /exchangeRates/{YYYY-MM-DD}
#
# Usage:
#   python import_and_set_rates.py /path/to/sa.json

import sys
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

def fetch_latest_rates(base: str = 'EUR') -> dict[str, float]:
    """Fetch latest rates from Frankfurter and inject base=1.0."""
    url = f'https://api.frankfurter.dev/v1/latest?base={base}'
    resp = requests.get(url)
    resp.raise_for_status()
    rates = resp.json().get('rates', {})
    rates[base] = 1.0
    return rates

def main(sa_key_path: str):
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(sa_key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    base = 'EUR'
    today = datetime.now(timezone.utc).date().isoformat()  # "YYYY-MM-DD"
    rates = fetch_latest_rates(base)

    payload = {
        'baseCurrency': base,
        'date':         today,
        'rates':        rates
    }

    # 1) Update "latest"
    db.collection('exchangeRates').document('latest').set(payload)
    print(f"[✓] /exchangeRates/latest updated for {today}")

    # 2) Append to history
    db.collection('exchangeRates').document(today).set(payload)
    print(f"[✓] /exchangeRates/{today} written")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python import_and_set_rates.py /path/to/serviceAccountKey.json")
        sys.exit(1)
    main(sys.argv[1])
