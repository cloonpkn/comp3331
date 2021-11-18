# COMP3331 Assignment
# Client Program
# Author: Colin Li - z5166028
# Developed on Python 2.7
# runcommand: python client.py server_port

from os import EX_SOFTWARE
from socket import *
from threading import Thread
import sys

serverPort = int(sys.argv[1])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(('localhost',serverPort))

p2pServerSocket = socket(AF_INET, SOCK_STREAM)
p2pServerSocket.bind((clientSocket.getsockname()[0],clientSocket.getsockname()[1]+1))

#print((clientSocket.getsockname()[0],clientSocket.getsockname()[1]+1))

clientAlive = True
p2pQuery = False
p2pQueryUser = " "
p2pClientActive = False
p2pServeActive = False

# Client multithreading built from sample by Wei Song

# Receiving Thread
class inThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        global clientAlive
        global p2pQuery
        global p2pQueryUser
        global p2pClientActive
        global p2pClientSocket
        global username
        try:
            while clientAlive == True:
                serverMessage = clientSocket.recv(1024)
                if serverMessage == "username active":
                    print("This account is already online")
                    clientAlive = False
                    clientSocket.close()
                    print("Press Enter to close")

                elif serverMessage == "username blocked":
                    print("Your account is blocked due to multiple login failures. Please try again later")
                    clientAlive = False
                    clientSocket.close()
                    print("Press Enter to close")

                elif serverMessage == "logged out":
                    print("You have successfully logged out. See you next time!")
                    clientAlive = False
                    clientSocket.close()
                    print("Press Enter to close")

                elif serverMessage == "timed out":
                    print("You have been logged out due to inactivity")
                    clientAlive = False
                    clientSocket.close()
                    print("Press Enter to close")

                elif serverMessage.split(" ")[0] == "startprivate":
                    print(" ".join(serverMessage.split(" ")[2:]))
                    p2pQuery = True
                    username = serverMessage.split(" ")[1]
                    p2pQueryUser = serverMessage.split(" ")[2]
                
                elif serverMessage.split(" ")[0] == "privateconfirm":
                    print("Start private messaging with " + serverMessage.split(" ")[1])
                    p2pQueryUser = serverMessage.split(" ")[1]
                    peerIP = serverMessage.split(" ")[2]
                    peerPort = int(serverMessage.split(" ")[3]) + 1
                    username = serverMessage.split(" ")[4]
                    p2pClientSocket = socket(AF_INET, SOCK_STREAM)
                    p2pClientSocket.connect((peerIP, peerPort))
                    p2pClientThread = p2pInThread(p2pClientSocket)
                    p2pClientThread.start()
                    p2pClientActive = True

                else:
                    print(serverMessage)
        except error:
            pass


# Sending Thread
class outThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global p2pQuery
        global p2pServeActive
        global p2pServeSocket
        try:
            while clientAlive == True:
                clientMessage = raw_input()
                if p2pQuery == True:
                    clientSocket.send("privateresponse " + clientMessage + " " + p2pQueryUser)
                    p2pQuery = False
                    if clientMessage == "y":
                        p2pServerSocket.listen(1)
                        p2pServeSocket, p2pClientAddr = p2pServerSocket.accept()
                        p2pServeThread = p2pInThread(p2pServeSocket)
                        p2pServeThread.start()
                        p2pServeActive = True
                elif p2pClientActive == True:
                    p2pClientSocket.send(clientMessage)
                    clientSocket.send(clientMessage)
                elif p2pServeActive == True:
                    p2pServeSocket.send(clientMessage)
                    clientSocket.send(clientMessage)
                else:
                    clientSocket.send(clientMessage)
        except error:
            pass

# p2p thread
class p2pInThread(Thread):
    def __init__(self, clientSocket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        #print("p2p thread started")
        self.p2pAlive = True

    def run(self):
        global p2pServeActive
        global p2pClientActive
        try:
            while self.p2pAlive == True:
                message = self.clientSocket.recv(1024)
                # handle private message requests
                command = message.split(" ")
                if command[0] == "private":
                    if command[1] == username:
                        print(p2pQueryUser + "(private): " + " ".join(command[2:]))
                if command[0] == "stopprivate":
                    if command[1] == username:
                        if p2pClientActive == True:
                            p2pClientSocket.send("stopprivate " + p2pQueryUser)
                            p2pClientActive = False
                            p2pClientSocket.close()
                            print("Private chat concluding")
                        if p2pServeActive == True:
                            p2pServeSocket.send("stopprivate " + p2pQueryUser)
                            p2pServeActive = False
                            p2pServeSocket.close()
                            print("Private chat concluding")
        except:
            pass
                




recThread = inThread()
recThread.start()
senThread = outThread()
senThread.start()

#while clientAlive == True:
#    p2pServerSocket.listen(1)
#    p2pClientSockt, p2pClientAddr = p2pServerSocket.accept()
#    p2pClientThread = p2pThread(p2pClientSockt)
#    p2pClientThread.start()