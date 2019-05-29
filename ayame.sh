#!/bin/sh

SCRIPT_DIR=$(cd $(dirname $0); pwd)

python3 $SCRIPT_DIR/ayame/tales.py
python3 $SCRIPT_DIR/ayame/make_csv_scips.py
python3 $SCRIPT_DIR/ayame/proposal.py
