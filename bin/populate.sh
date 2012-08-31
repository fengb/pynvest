#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR
. __env__.sh


cd $PROJECT_DIR
export PYTHONPATH=$SRC_DIR
export DJANGO_SETTINGS_MODULE=dptest.settings
python -c '
import sys
import pynvest_investment.batches

pynvest_investment.batches.populate(output=sys.stdout)
'
