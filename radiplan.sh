#!/bin/bash
. ~/.bashrc
conda activate radiplan
exec python -u ~/bin/radiplan.py $@