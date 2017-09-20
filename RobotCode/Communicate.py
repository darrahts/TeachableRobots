import socket
from collections import deque
from threading import Thread

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
                    self.inbox.appendleft(decoded)
        return

    def closeConnection(self):
        self.finished = True
        self.getMessagesThread.join()
        self.connection.close()
        return
