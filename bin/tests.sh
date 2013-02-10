#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$SCRIPT_DIR/..
export PROJECT_DIR=$PYTHONPATH/pynvest
cd $PYTHONPATH


rm -rf test
mkdir -p test
export DJANGO_SETTINGS_MODULE=pynvest.settings_test
pynvest/manage.py syncdb --noinput --settings=pynvest.settings_test
py.test $*
