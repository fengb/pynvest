SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SRC_DIR=$SCRIPT_DIR/..
export PROJECT_DIR=$SRC_DIR/dptest

cd $SRC_DIR
export PYTHONPATH=$SRC_DIR
