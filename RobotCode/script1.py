
import serial
import time
import threading
import sys
import select

arduino = serial.Serial("/dev/ttyACM0", 9600)
arduino.flush()
arduino.flush()
#arduino.write(bytes("1-1_*".encode('ascii')))

userInput = ""
tokens = []
cmds = []

while(True):
    arduino.flushInput()
    arduino.flushOutput()
    userInput = input(":")
    if(userInput != ""):
        if userInput == "manual":
            sequence = "6-0"
            arduino.flushInput()
            arduino.flushOutput()
            time.sleep(.1)
            arduino.write(bytes(sequence.encode('ascii')))
            time.sleep(1.5)
            while(True):
                time.sleep(.1)
                if(arduino.inWaiting() > 0):
                    print(arduino.readline())
                    arduino.flushInput()
                    arduino.flushOutput()
                userInput = input(">")
                arduino.flushInput()
                time.sleep(.1)
                arduino.write(bytes(userInput.encode('ascii')))
                if(userInput == "q"):
                    userInput = ""
                    break
                userInput = ""
                arduino.flushOutput()
        elif userInput == "Q":
            break
        else:
            userIn = userInput.split(',')
            for a in userIn:
                t = a.split(' ')
                for b in t:
                    if b is not "":
                        tokens.append(b)
            for val in tokens:
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
                else:
                    x = str(val + "_")
                cmds.append(x)

            for val in cmds:
                print(val)
            sequence = "".join(cmds)
            #print("sending: " + sequence)
        arduino.flush()
        arduino.write(bytes(sequence.encode('ascii')))
        time.sleep(1)
        userInput == ""
        cmds.clear()
        sequence = ""
        for val in cmds:
            print(val)
        print(sequence)
        print(userInput)
    #if(arduino.inWaiting() > 0):
    #    print("something to read.")
    #    print(arduino.readline())


arduino.close()
