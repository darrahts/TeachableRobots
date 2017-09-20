#!/usr/bin/python
from Hardware import *
import math

# power registers for the mpu6050
pm1 = 0x6b
pm2 = 0x6c

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

bus.write_byte_data(gyroAddress, pm1, 0)

print("Gyro Data")

gX = readWord_2c(0x43) / 131
gY = readWord_2c(0x45) / 131
gZ = readWord_2c(0x47) / 131

print "x: ", gX
print "y: ", gY
print "z: ", gZ

aX = readWord_2c(0x3b) / 16384.0
aY = readWord_2c(0x3d) / 16384.0
aZ = readWord_2c(0x3f) / 16384.0

print "aX: ", aX
print "aY: ", aY
print "aZ: ", aZ

print "x rotation: ", getXrotation(aX, aY, aZ)
print "y rotation: ", getYrotation(aX, aY, aZ)





