#!/usr/bin/env bash
# Upgrade pip first
python -m pip install --upgrade pip
# Install requirements with specific pip command
python -m pip install -r requirements.txt
# Verify gunicorn installation
python -m pip install gunicorn