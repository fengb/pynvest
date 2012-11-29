#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$SCRIPT_DIR/..
export PROJECT_DIR=$PYTHONPATH/dptest
cd $PYTHONPATH


mkdir -p test
export DJANGO_SETTINGS_MODULE=dptest.settings_test
dptest/manage.py flush --noinput --settings=dptest.settings_test
py.test $*
