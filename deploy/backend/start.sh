#!/bin/bash
cd /www/wwwroot/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
