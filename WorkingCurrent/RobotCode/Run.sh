#!/bin/bash

#   This script starts the RobotControlModule.py (RCM) script and the Flask Web Server (FWS).


RCM_PATH=$(pwd)/RobotCjontrolModule.py
FWS_PATH=$(pwd)/FlaskServer/src/server.py

./RCM_PATH &
sleep 1
./FWS_PATH &
