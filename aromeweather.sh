#!/bin/bash
. ~/.bashrc
conda activate aromeweather
exec python -u ~/bin/aromeweather.py $@