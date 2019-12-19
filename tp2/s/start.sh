#!/bin/bash

set -e

./resetConfig.sh

./lossConfig.sh $2

python3 ~/s/main.py $1
