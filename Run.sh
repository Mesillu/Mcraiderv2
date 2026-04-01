#!/bin/bash

clear
echo "======================="
echo "     McRaider v2"
echo "======================="

sleep 1

pkg update -y
pkg install python git -y

pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "[*] Running..."
python Mcraiderv2.py
