import socket
import sys
import uuid
import time
import numpy as np



def GetTime(t):
    h1 = b"\xff"
    h2 = b"\xfe"
    l1 = b"\xfd"
    l2 = b"\xfc"
    return bytearray(h1 + h2 + l1 + l2)



val = np.uint32(123344)
print(val)
print(sys.getsizeof(val()))





timeNow = lambda: int(round(time.time() * 1000))
start = timeNow()

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server = ("52.73.65.98", 1973)

#server = ("localhost", 12345)

#mac = bytes((hex(uuid.getnode()))[2:], "ascii")
mac = hex(uuid.getnode())[2:]

##for i in range(0, 300):
##    t = GetTime(i)
##    msg = bytearray.fromhex(mac)
##    msg += t
##    msg += b"\x49"
##    print(msg)
##    sent = socket.sendto(msg, server)
##    time.sleep(1)
##    



