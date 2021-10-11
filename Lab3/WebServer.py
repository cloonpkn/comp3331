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

    if request[0] == "GET":
        try:
            fileName = request[1]
            requestType = request[1].split(".")
            fileType = requestType[1]

            p = open(fileName[1:])
            messageBody = p.read()
            p.close()

            connectionSocket.send("HTTP/1.1 200 OK\r\n")
            if fileType == "html":
                connectionSocket.send("Content-Type: text/html; charset=utf-8\r\n")
            elif fileType == "png":
                connectionSocket.send("Content-Type: image/png\r\n")
            connectionSocket.send("Connection: close\r\n")
            connectionSocket.send("\r\n")
            connectionSocket.send(messageBody)

        except IOError:
            connectionSocket.send("HTTP/1.1 404 Not Found\r\n")
            connectionSocket.send("Content-Type: text/html; charset=utf-8\r\n")
            connectionSocket.send("Connection: close\r\n")
            connectionSocket.send("\r\n")
            connectionSocket.send("<html><head><title>Error404</title></html><body><h1>Error 404: Not Found</h1></body></html>")

    connectionSocket.close()