#!/bin/bash

set -e

./resetConfig.sh

./lossConfig.sh $2

python3 ~/r2/main.py
