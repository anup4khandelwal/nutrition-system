#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
python3 scripts/pick_today.py
cd whatsapp && COOK_WHATSAPP="$COOK_WHATSAPP" node send.js
