#!/usr/bin/python

import smbus
import math 
import web

urls = ( '/', 'index' )

# power registers for the mpu6050
pm1 = 0x6b
pm2 = 0x6c

bus = smbus.SMBus(1)
gyroAddress = 0x68


def readByte(address):
    return bus.read_byte_data(gyroAddress, address)

def readWord(address):
    high = bus.read_byte_data(gyroAddress, address)
    low = bus.read_byte_data(gyroAddress, address+1)
    val = ( high << 8) + low
    return val

def readWord_2c(address):
    val = readWord(address)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def distance(a,b):
    return math.sqrt((a*a)+(b*b))

def getYrotation(x,y,z):
    radians = math.atan2(x, distance(y,z))
    return -math.degrees(radians)

def getXrotation(x,y,z):
    radians = math.atan2(y, distance(x,z))
    return -math.degrees(radians)


class index:
    def GET(self):
        gX = readWord_2c(0x43) / 131
        gY = readWord_2c(0x45) / 131
        gZ = readWord_2c(0x47) / 131

        aX = readWord_2c(0x3b) / 16384.0
        aY = readWord_2c(0x3d) / 16384.0
        aZ = readWord_2c(0x3f) / 16384.0

        return str(getXrotation(aX, aY, aZ))+" "+str(getYrotation(aX, aY, aZ))

if __name__ == "__main__":
    bus.write_byte_data(gyroAddress, pm1, 0)
    app = web.application(urls, globals())
    app.run()   
        







