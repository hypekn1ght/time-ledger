#!/bin/bash
# Time Ledger - Backend Startup Script
# Run this to start the API server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"
echo "Starting Time Ledger API..."
echo "Local:    http://localhost:8000"
echo "Public:   https://openclaw.tailcd9b6e.ts.net"
echo ""
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
