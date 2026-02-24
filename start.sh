#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Start bot with gunicorn (production server)
gunicorn bot:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
