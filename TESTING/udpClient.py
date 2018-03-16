import socket

UDP_ADR = "127.0.0.1"
UDP_PORT = 6789

message = "start robot"

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

clientSocket.sendto(message.encode("ascii"), (UDP_ADR, UDP_PORT))
