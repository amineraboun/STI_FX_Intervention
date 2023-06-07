#!/bin/bash

name="sti"

python -m venv .venv
#source .venv/bin/activate
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install ipykernel
.venv/bin/python -m ipykernel install --user --name=$name
