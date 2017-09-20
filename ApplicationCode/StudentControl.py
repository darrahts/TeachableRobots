import socket
from collections import deque
from threading import Thread
from time import sleep
import os
import sys
import termios
import tty

def getKey():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    k = None
    try:
        k = os.read(fd, 3)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    key = str(k)
    key = key.replace("b", "")
    key = key.replace("'", "")
    return key


class Communicate(object):
    def __init__(self):
        self.address = ""
        self.port = 5580
        self.finished = False
        self.inbox = deque()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.getMessagesThread = Thread(target=self.getMessages)
        print(self.address)
        return
    
    def setupLine(self, addr):
        self.address = addr
        if self.address is "":
            try:
                self.connection.bind((self.address, self.port))
                self.connection.listen(1)
                self.connection, otherAddress = self.connection.accept()
                print("connected to: " + otherAddress[0])
            except socket.error as msg:
                print(msg)
        else:
            self.connection.connect((self.address, self.port))
        self.getMessagesThread.start()
        return

    def sendMessage(self, msg):
        self.connection.send(str.encode(msg))
        return

    def getMessages(self):
        while not self.finished:
            received = self.connection.recv(1024)
            decoded = received.decode('utf-8')
            if len(decoded) > 0:
                if decoded == "connection closed.":
                    print("connection closed.")
                else:
                    print("\n" + decoded) 
        return

    def closeConnection(self):
        self.finished = True
        self.getMessagesThread.join()
        self.connection.close()
        print("connection closed.")
        return

comm = Communicate()
try:
    addr = input("enter the address to connect to: ")
    if(addr == "robot1"):
        addr = "192.168.1.40"
        print(addr)
    comm.setupLine(addr)
    while(comm.finished == False):
        msg = getKey()
        comm.sendMessage(msg)
        if(msg == "q"):
            break

except KeyboardInterrupt:
    pass

finally:
    print("goodbye")
    comm.closeConnection()






















