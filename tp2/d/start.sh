#!/bin/bash

set -e

./resetConfig.sh

./lossConfig.sh $2

python3 ~/d/main.py $1
