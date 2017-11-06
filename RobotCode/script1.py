
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

        self.mode = 0 #0 for auto, 1 for manual
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
                ardIn = self.arduino.read().decode("ascii")
                ardIn = ardIn.replace("\r", "")
                ardIn = ardIn.replace("\n", "")
                if(ardIn != ""):
                    print("   ^ " + ardIn + " ^")
                    if(self.mode == 0):
                        print(":", end = "")
                    else:
                        print(">", end = "");


    def ManualMode(self):
        self.mode = 1
        self.sequence = "mm"
        time.sleep(.1)
        self.arduino.write(bytes(self.sequence.encode('ascii')))
        time.sleep(1.5)
        while(True):
            time.sleep(.1)
            self.userInput = input(">")
            time.sleep(.1)
            print(bytes(self.userInput.encode('ascii')))
            self.arduino.write(bytes(self.userInput.encode('ascii')))
            if(self.userInput == "q"):
                self.userInput = ""
                break

    def Run(self):
         while(not self.finished):
            self.userInput = input(":")
            if(self.userInput == "manual"):
                self.ManualMode()
            elif(self.userInput == "Q"):
                self.finished = True
                self.responseThread.join()
                break
            else:
                self.mode = 0
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
        try:
            c = Controller("/dev/ttyACM0")
        except:
            try:
                c = Controller("/dev/ttyACM1")
            except:
                print("couldnt open arduino port.")

        c.responseThread.start()
        c.Run()
        c.arduino.close()
    except:
        print("error.")
    finally:
        print("finished.")






