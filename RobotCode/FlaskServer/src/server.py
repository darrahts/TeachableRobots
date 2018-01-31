#!/usr/bin/python3

import os
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from teachablerobots.src.Communicate import SocketComm
import logging

app = Flask(__name__)
#log = logging.getLogger("werkzeug")
#log.setLevel(logging.ERROR)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')
socketio = SocketIO(app)

tcpClient = SocketComm()
    

def ParseCmdString(cmdList):
    cmdString = ""
    for val in cmdList:
        #   check if its an int (i.e. forward or backward amount)
        if(type(val) == type(2)):
            if(val > 0):
                cmdString += "1-{}_".format(val)
            elif(val < 0):
                cmdString += "2-{}_".format(val)
            else:
                return "0"
            
        #   check if its a string (i.e. turn left or right)
        elif (type(val) == type("s")):
            if(val == "left"):
                cmdString += "3-90_"
            elif(val == "right"):
                cmdString += "4-90_"
            elif(val == "stop"):
                cmdString += "*"
                break
    cmdString += "*"
    print(cmdString)
        
    return cmdString
    

def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):
    try:
        src = os.path.join(root_dir(), filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)


@app.route('/')
def index():
    return Response(get_file('../public/index.html'), mimetype="text/html")
    return render_template('index.html')


@app.route('/main.js')
def mainjs():
    return Response(get_file('../public/main.js'), mimetype="text/html")
    return render_template('index.html')


@socketio.on('submission')
def test_message(message):
    print('got', message)
    
    #emit('my response', {'data': 'got it!'})
    
    tcpClient.sendMessage(ParseCmdString(message))


if __name__ == '__main__':
    try:
        print("setting up connection...")
        while(True):
            if(tcpClient.setupLine("127.0.0.1")):
                break
            else:
                ans = input("robot not online. try again (y/n)?")
                if(ans == "n"):
                    break
        if(tcpClient.connected):
            socketio.run(app, host="0.0.0.0")
    except Exception as e:
        print(str(e))














