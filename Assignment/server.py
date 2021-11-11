# COMP3331 Assignment
# Server Program
# Author: Colin Li - z5166028
# Developed on Python 3.7.10
# runcommand: python server.py server_port block_duration timeout

from socket import *
import sys

serverPort = int(sys.argv[1])

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost',serverPort))

serverSocket.listen(1)

while 1:
    connectionSocket, addr = serverSocket.accept()

    message = connectionSocket.recv(1024)

    request = message.split(" ")

    

    connectionSocket.close()