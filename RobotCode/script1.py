
import serial
import time
import threading

def TryParseInt(val):
    try:
        return int(val)
    except ValueError:
        return False



class Controller(object):
    def __init__(self, port):
        self.responseThread = threading.Thread(target=self.GetResponse)
        self.arduino = serial.Serial(port, 9600)
        
        self.userInput = ""
        self.tokens = []
        self.cmds = []
        self.sequence = ""
        self.finished = False
        self.validSequence = False

    def GetResponse(self):
        ardIn = ""
        while(not self.finished):
            if(self.arduino.inWaiting() > 0):
                ardIn = self.arduino.readline().decode("ascii")
                ardIn = ardIn.replace("\r\n", "")
                print("   ^ " + ardIn + " ^")


    def ManualMode(self):
        self.sequence = "6-0"
        time.sleep(.1)
        self.arduino.write(bytes(self.sequence.encode('ascii')))
        time.sleep(1.5)
        while(True):
            time.sleep(.1)
            userInput = input(">")
            time.sleep(.1)
            self.arduino.write(bytes(self.userInput.encode('ascii')))
            if(userInput == "q"):
                userInput = ""
                break


    def SequenceMode(self):
        while(not self.finished):
            self.userInput = input(":")
            if(self.userInput == "manual"):
                self.ManualMode()
            elif(self.userInput == "Q"):
                self.finished = True
                self.responseThread.join()
                break
            else:
                self.GenerateCommandSequence()
                if(self.validSequence):
                    print("sent: " + self.sequence)
                    self.arduino.write(bytes(self.sequence.encode('ascii')))
            self.userInput = ""
            self.sequence = ""
            self.tokens = []
            self.cmds = []
                    


    def GenerateCommandSequence(self):
        userIn = self.userInput.split(',')
        for a in userIn:
            t = a.split(' ')
            for b in t:
                if b is not "":
                    self.tokens.append(b)
        for val in self.tokens:
            x = ""
            if(val == "forward"):
                x = "1-"
            elif(val == "back"):
                x = "2-"
            elif(val == "left"):
                x = "3-90_"
            elif(val == "right"):
                x = "4-90_"
            elif(val == "stop"):
                x = "*"
            elif(TryParseInt(val) != False):
                x = val
            else:
                print("couldn't parse the commands. check your entry.")
                self.validSequence = False
                return
            self.cmds.append(x)
        self.sequence = "".join(self.cmds)
        self.validSequence = True
        return








if (__name__ == "__main__"):
    try:
        c = Controller("/dev/ttyACM0")
    except:
        try:
            c = Controller("/dev/ttyACM1")
        except:
            print("couldnt open arduino port.")

    c.responseThread.start()
    c.SequenceMode()
    c.arduino.close()
    print("finished.")






