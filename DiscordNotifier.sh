#! /usr/bin/bash

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" || exit 1
source venv/bin/activate
python3 main.py
