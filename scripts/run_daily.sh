#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a

# Generate today's payload
python3 scripts/pick_today.py

# Build wa.me link & auto-open (99% automated - one tap to send)
python3 scripts/send_via_walink.py
