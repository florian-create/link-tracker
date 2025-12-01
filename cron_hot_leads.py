#!/usr/bin/env python3
"""
Cron job to send hot leads (5+ clicks) to Clay every hour
Run this script with: python cron_hot_leads.py

Or set up as a cron job:
0 * * * * cd /path/to/link-tracker && python cron_hot_leads.py
"""

import os
import requests
import sys
from datetime import datetime

# Configuration
API_URL = os.environ.get('API_URL', 'https://link-tracker-r68v.onrender.com')
CLAY_WEBHOOK_URL = os.environ.get('CLAY_WEBHOOK_URL')
MIN_CLICKS = int(os.environ.get('MIN_CLICKS', 5))

def send_hot_leads():
    """Call the hot-leads webhook endpoint"""

    if not CLAY_WEBHOOK_URL:
        print(f"[{datetime.now()}] ERROR: CLAY_WEBHOOK_URL not set in environment")
        sys.exit(1)

    endpoint = f"{API_URL}/api/webhook/hot-leads"

    payload = {
        "clay_webhook_url": CLAY_WEBHOOK_URL,
        "min_clicks": MIN_CLICKS
    }

    try:
        print(f"[{datetime.now()}] Checking for hot leads (min {MIN_CLICKS} clicks)...")

        response = requests.post(endpoint, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print(f"[{datetime.now()}] ✅ SUCCESS: {data.get('message')}")
            print(f"   - Sent: {data.get('sent_count')} leads")
            print(f"   - Total found: {data.get('total_found')} leads")

            if data.get('errors'):
                print(f"   - Errors: {len(data['errors'])}")
                for error in data['errors'][:3]:  # Show first 3 errors
                    print(f"     * {error['email']}: {error['error']}")
        else:
            print(f"[{datetime.now()}] ❌ ERROR: API returned {response.status_code}")
            print(f"   Response: {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"[{datetime.now()}] ❌ EXCEPTION: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    send_hot_leads()
