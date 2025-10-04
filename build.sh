#!/usr/bin/env bash
# Upgrade pip first
python -m pip install --upgrade pip
# Install gunicorn first
python -m pip install gunicorn
# Then install other requirements
python -m pip install -r requirements.txt
