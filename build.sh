#!/usr/bin/env bash
# Upgrade pip first
python -m pip install --upgrade pip
<<<<<<< HEAD
# Install gunicorn first
python -m pip install gunicorn
# Then install other requirements
python -m pip install -r requirements.txt
=======
# Install requirements with specific pip command
python -m pip install -r requirements.txt
# Verify gunicorn installation
python -m pip install gunicorn
>>>>>>> eca20facb17c1301a63150b875588ef29bd045e9
