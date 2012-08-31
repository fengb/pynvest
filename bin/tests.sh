#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR
. __env__.sh


mkdir -p test
export DJANGO_SETTINGS_MODULE=dptest.settings_test
dptest/manage.py flush --noinput --settings=dptest.settings_test
py.test $*
