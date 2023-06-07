#!/bin/bash

name="sti"

python -m venv .venv

# source .venv/bin/activate

# upgrade pip
.venv/bin/python -m pip install --upgrade pip

# install all requirements
.venv/bin/python -m pip install -r requirements.txt

# install ipykernel (if not already there because of requirements)
.venv/bin/python -m pip install ipykernel

# install a kernel in the standard location for virtual environments
.venv/bin/python -m ipykernel install --prefix .venv --name=$name

#.venv/bin/python -m ipykernel install --user --name=$name

