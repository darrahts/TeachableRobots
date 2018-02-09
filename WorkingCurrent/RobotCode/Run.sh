#!/bin/bash

#   This script starts the RobotControlModule.py (RCM) script and the Flask Web Server (FWS).


RCM_PATH="$(pwd)/RobotControlModule.py"
FWS_PATH="$(pwd)/FlaskServer/src/server.py"

#echo $RCM_PATH
#echo $FWS_PATH
python3 $RCM_PATH &
sleep 1
python3 $FWS_PATH &
