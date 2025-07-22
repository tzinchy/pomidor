#!/bin/bash
cd /home/dsa-dgi/programs/pomidor/backend/loader
source .venv/bin/activate
python3 app/renovation_etl.py
