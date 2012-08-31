#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR/.."

cd $PROJECT_DIR
mkdir -p $PROJECT_DIR/test
export DJANGO_SETTINGS_MODULE=dptest.settings_test
$PROJECT_DIR/dptest/manage.py flush --noinput --settings=dptest.settings_test
py.test $*
