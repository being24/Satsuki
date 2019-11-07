#!/bin/sh

SCRIPT_DIR=$(cd $(dirname $0); pwd)

python3 $SCRIPT_DIR/ayame/scips.py
python3 $SCRIPT_DIR/ayame/tales.py
python3 $SCRIPT_DIR/ayame/proposal.py
python3 $SCRIPT_DIR/ayame/auther.py
python3 $SCRIPT_DIR/ayame/ex.py
python3 $SCRIPT_DIR/ayame/joke.py
python3 $SCRIPT_DIR/ayame/guidehub.py
