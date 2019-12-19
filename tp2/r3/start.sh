#!/bin/bash

set -e

./resetConfig.sh

./lossConfig.sh $2

python3 ~/r3/main.py
