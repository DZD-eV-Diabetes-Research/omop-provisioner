#!/bin/bash
#Script to generate and oldschool requierments.txt from pyproject.toml

# old non pdm version
#python -m pip install pip-tools -U
#rm requirements.txt
#python -m piptools compile -o requirements.txt pyproject.toml

# New PDM version
rm requirements.txt
pdm export -o requirements.txt --without-hashes