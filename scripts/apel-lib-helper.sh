#!/bin/bash

if python --version 2>&1 | grep -qE 'Python 3\.(6|7|8|9|[1-9][0-9])'; then
    if command -v pip &>/dev/null; then
        sudo pip install mysqlclient
    elif command -v pip3 &>/dev/null; then
        sudo pip3 install mysqlclient
    else
        echo "pip command NOT found."
    fi
elif python3 --version 2>&1 | grep -qE 'Python 3\.(6|7|8|9|[1-9][0-9])'; then
    if command -v pip3 &>/dev/null; then
        sudo pip3 install mysqlclient
    else
        echo "pip3 command NOT found."
    fi
else
    echo "Skipping mysqlclient installtion process"
fi
