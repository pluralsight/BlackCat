#!/usr/bin/env bash
flake8
cd blackcat/
python3 -m pytest .