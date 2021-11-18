# COMP3331 Assignment
# Server Program
# Author: Colin Li - z5166028
# Developed on Python 2.7
# runcommand: python server.py server_port block_duration

from socket import *
from threading import Thread
from time import *
import sys

if len(sys.argv) != 4:
    print("ERROR: use command follows - python server.py SERVER_PORT BLOCK_DURATION TIMEOUT\n")
    exit(0)

serverPort = int(sys.argv[1])
block_duration = int(sys.argv[2])
timeout_limit = int(sys.argv[3])

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost',serverPort))

# multithreading code built from sample written by Wei Song
class clientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.privateQuery = False
        
        #print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        self.loggedIn = False
    
    def run(self):
        try:
            message = ''

            if self.loggedIn == False:
                self.login()

            self.clientSocket.settimeout(timeout_limit)
        
            sleep(0.01)

            self.offlineMessages()
        
            while self.clientAlive:
                # use recv() to receive message from the client
                message = self.clientSocket.recv(1024)
                #print(message)

                command = message.split(" ")

                # handle commands from the client
                # message command
                if command[0] == "message":
                    self.message(command[1],command[2:])

                # broadcast command
                elif command[0] == "broadcast":
                    self.broadcast(command[1:])
                    
                # whoelse command
                elif command[0] == "whoelse":
                    self.whoelse()

                # whoelsesince command
                elif command[0] == "whoelsesince":
                    self.whoelsesince(command[1])

                # block command
                elif command[0] == "block":
                    self.block(command[1])

                # unblock command
                elif command[0] == "unblock":
                    self.unblock(command[1])

                # logout command
                elif command[0] == "logout":
                    self.logout()

                # startprivate command
                elif command[0] == "startprivate":
                    self.startprivate(command[1])

                # private command
                elif command[0] == "private":
                    if command[1] in status.validUsers:
                        # check if targetuser is valid
                        if command[1] == self.alias:
                            # send a message to themselves
                            self.clientSocket.send("Error: Cannot private message self")
                        else:
                            if [command[1], self.alias] in status.p2pPartners or [self.alias, command[1]] in status.p2pPartners:
                                # valid
                                pass
                            else:
                                self.clientSocket.send("Error: Private messaging to " + command[1] + " not enabled")
                    else:
                        # target user is invalid
                        self.clientSocket.send("Error: Invalid user")

                # stopprivate command
                elif command[0] == "stopprivate":
                    if command[1] in status.validUsers:
                        # check if targetuser is valid
                        if command[1] == self.alias:
                            # send a message to themselves
                            self.clientSocket.send("Error: Cannot private message self")
                        else:
                            if [command[1], self.alias] in status.p2pPartners or [self.alias, command[1]] in status.p2pPartners:
                                # valid
                                pass
                            else:
                                self.clientSocket.send("Error: Private messaging to " + command[1] + " not enabled")
                    else:
                        # target user is invalid
                        self.clientSocket.send("Error: Invalid user")
                
                elif command[0] == "privateresponse" and command[2] in status.usersQueryingP2P:
                    x = status.activeUsers.index(command[2])
                    targetSocket = status.activeSocket[x]
                    if command[1] == "y":
                        status.p2pPartners.append([command[2], self.alias])
                        targetSocket.send("privateconfirm " + self.alias + " " + str(self.clientAddress[0]) + " " + str(self.clientAddress[1]) + " " + command[2])
                    else:
                        targetSocket.send(self.alias + " has declined private messaging")
                    x = status.usersQueryingP2P.index(command[2])
                    status.usersQueryingP2P.pop(x)

                else:
                    self.clientSocket.send("ERROR: Invalid command")

        except timeout:
            self.timedout()


    def login(self):
        self.clientSocket.send('--- Please Enter Your Username ---')
        clientMessage = self.clientSocket.recv(1024)

        credFile = open("credentials.txt",'a+')
        creds = credFile.readlines()

        newUser = True
        
        # check if entered username is listed in credentials file
        for x in range(len(creds)):
            if status.isActive(clientMessage) == True:
                # username is currently active
                newUser = False
                self.clientSocket.send('username active')
                # terminate client
                self.clientAlive = False
                break

            userpass = creds[x].split(" ")
            username = userpass[0]
            if clientMessage == username:
                # username is listed in credentials.txt
                newUser = False

                # check if user is currently blocked
                if status.isBlocked(clientMessage) == True:
                    self.clientSocket.send('username blocked')
                    # terminate client
                    self.clientAlive = False
                    break

                password = userpass[1]
                self.clientSocket.send('--- Username is Valid ---')
                # validate password
                attempts = 0
                while attempts <= 3:
                    if attempts == 3:
                        # username is blocked for block_duration
                        self.clientSocket.send('username blocked')
                        status.addBlock(username)
                        # terminate client
                        self.clientAlive = False
                        break
                        
                    sleep(0.01)
                    self.clientSocket.send('--- Please Enter Your Password ---')
                    clientMessage = self.clientSocket.recv(1024)

                    if clientMessage == password.rstrip():
                        # valid password
                        self.clientSocket.send('--- Welcome to this messaging application! Have fun! ---')
                        # thread is now logged in
                        self.loggedIn = True
                        self.alias = username
                        status.addActiveUser(username, self.clientSocket)
                        status.removeOfflineUser(username)
                        self.presenseUpdate("in", False)
                        break
                    else:
                        # invalid password
                        self.clientSocket.send('*** Incorrect Password. Try Again ***')
                        sleep(0.01)
                        attempts += 1

        # create new credential
        if newUser == True:
            # write new username password line to credential.txt
            self.clientSocket.send('--- Welcome New User ---')
            sleep(0.01)
            username = clientMessage
            self.clientSocket.send('--- Please Enter a Password ---')
            clientMessage = self.clientSocket.recv(1024)
            password = clientMessage
            # append new username and password to credentials.txt
            credFile.write("\n" + username + " " + password)
            self.clientSocket.send('--- Welcome to this messaging application! Have fun! ---')
            # thread is now logged in
            self.loggedIn = True
            self.alias = username
            status.addValidUser(username)
            status.addActiveUser(username, self.clientSocket)
            self.presenseUpdate("in", False)

        credFile.close()

    def presenseUpdate(self, inOrOut, timeoutFlag):
        blockEvent = False
        for x in status.activeSocket:
            if x == self.clientSocket:
                pass
            # check if self is blocked by other user
            elif [status.activeUsers[status.activeSocket.index(x)],self.alias] in status.blacklists:
                blockEvent = True
            elif timeoutFlag == True:
                x.send(self.alias + " has timed out")
            else:
                x.send(self.alias + " has logged " + inOrOut)
        if blockEvent == True:
            pass

    def message(self, targetUser, message):
        if targetUser in status.validUsers:
            # check if targetuser is valid
            if targetUser == self.alias:
                # send a message to themselves
                self.clientSocket.send("Error: Cannot message self")
            else:
                # check if sender is blocked by targetUser
                if [self.alias, targetUser] in status.blacklists:
                    self.clientSocket.send("Your message could not be delivered as the recipient has blocked you")
                else:
                    # Online messaging
                    if status.isActive(targetUser) == True:
                        x = status.activeUsers.index(targetUser)
                        targetSocket = status.activeSocket[x]
                        targetSocket.send(self.alias + ": " + " ".join(message))
                    # Offline messaging
                    else:
                        status.storeMessage(self.alias, targetUser, message)
        else:
            # target user is invalid
            self.clientSocket.send("Error: Invalid user")

    def offlineMessages(self):
        for x in status.storedMessages:
            if x[0] == self.alias:
                self.clientSocket.send(x[1] + ": " + " ".join(x[2]))

    def broadcast(self, message):
        blockEvent = False
        for x in status.activeSocket:
            if x == self.clientSocket:
                pass
            elif [self.alias, status.activeUsers[status.activeSocket.index(x)]] in status.blacklists:
                blockEvent = True
            else:
                x.send(self.alias + ": " + " ".join(message))
        if blockEvent == True:
            self.clientSocket.send("Your message could not be delivered to some recipients")

    def whoelse(self):
        blockEvent = False
        for x in status.activeUsers:
            if x == self.alias:
                pass
            # check if query user is blocked by an active user
            elif [self.alias, x] in status.blacklists:
                blockEvent = True
            else:
                self.clientSocket.send(x)
            sleep(0.01)

        if blockEvent == True:
            pass

    def whoelsesince(self, queryTime):
        blockEvent = False
        for x in status.activeUsers:
            if x == self.alias:
                pass
            elif [self.alias, x] in status.blacklists:
                blockEvent = True
            else:
                self.clientSocket.send(x)
            sleep(0.01)
        for y in range(len(status.offlineUsers)):
            if [self.alias, status.offlineUsers[y]] in status.blacklists:
                blockEvent = True
            elif time() < status.offlineUsersTime[y] + int(queryTime):
                self.clientSocket.send(status.offlineUsers[y])

    def block(self, target):
        if target in status.validUsers:
            # check if target is valid
            if target == self.alias:
                # blacklisting themselves
                self.clientSocket.send("Error: Cannot block self")
            else:
                if [target, self.alias] in status.blacklists:
                    self.clientSocket.send("Error: " + target + " is already blocked")
                else:
                    # blacklists = [blocked, blocker]
                    status.blacklists.append([target, self.alias])
                    self.clientSocket.send(target + " is blocked")
        else:
            # target user is invalid
            self.clientSocket.send("Error: Invalid user")

    def unblock(self, target):
        if target in status.validUsers:
            # check if target is valid
            if target == self.alias:
                # unblacklisting themselves
                self.clientSocket.send("Error: Cannot unblock self")
            else:
                if [target, self.alias] in status.blacklists:
                    # blacklists = [blocked, blocker]
                    status.blacklists.remove([target, self.alias])
                    self.clientSocket.send(target + " is unblocked")
                else:
                    self.clientSocket.send("Error: " + target + " is not blocked")
        else:
            # target user is invalid
            self.clientSocket.send("Error: Invalid user")

    def startprivate(self, target):
        if target in status.validUsers:
            # check if target is valid
            if target == self.alias:
                # start private with themselves
                self.clientSocket.send("Error: Cannot private message self")
            else:
                # check if sender is blocked by target
                if [self.alias, target] in status.blacklists:
                    self.clientSocket.send("Your request could not be delivered as the recipient has blocked you")
                else:
                    # Online
                    if status.isActive(target) == True:
                        x = status.activeUsers.index(target)
                        targetSocket = status.activeSocket[x]
                        targetSocket.send("startprivate " + target + " " + self.alias + " would like to private message, enter y or n:")
                        status.usersQueryingP2P.append(self.alias)
                    # Offline
                    else:
                        self.clientSocket.send("User is offline")
        else:
            # target user is invalid
            self.clientSocket.send("Error: Invalid user")

    def logout(self):
        self.presenseUpdate("out", False)
        status.removeActiveUser(self.alias, self.clientSocket)
        status.addOfflineUser(self.alias)
        self.loggedIn = False
        self.clientAlive = False
        self.clientSocket.send("logged out")

    def timedout(self):
        self.presenseUpdate("out", True)
        status.removeActiveUser(self.alias, self.clientSocket)
        status.addOfflineUser(self.alias)
        self.loggedIn = False
        self.clientAlive = False
        self.clientSocket.send("timed out")
     

class serverStatus():
    def __init__(self):
        self.blockedUsers = []
        self.blockedUsersTime = []
        self.offlineUsers = []
        self.offlineUsersTime = []
        self.activeUsers = []
        self.activeSocket = []
        self.validUsers = []
        self.storedMessages = []
        self.blacklists = []
        self.usersQueryingP2P = []
        self.p2pPartners = []

    def addBlock(self, username):
        blockTime = time()
        self.blockedUsers.append(username)
        self.blockedUsersTime.append(blockTime)
        print(username + " blocked at" + str(blockTime))

    def isBlocked(self, username):
        blocked = False
        for x in range(len(self.blockedUsers)):
            if self.blockedUsers[x] == username:
                currTime = time()
                blockTimeOut = self.blockedUsersTime[x] + block_duration
                if currTime < blockTimeOut:
                    blocked = True
                    break
                else:
                    blocked = False
                    # block no longer active, remove from list
                    self.blockedUsers.pop(x)
                    self.blockedUsersTime.pop(x)
                    break
        return blocked

    def addActiveUser(self, username, clientSocket):
        self.activeUsers.append(username)
        self.activeSocket.append(clientSocket)

    def isActive(self, username):
        active = False
        for x in self.activeUsers:
            if x == username:
                active = True
        return active

    def removeActiveUser(self, username, clientSocket):
        self.activeUsers.remove(username)
        self.activeSocket.remove(clientSocket)

    def addOfflineUser(self, username):
        self.offlineUsers.append(username)
        self.offlineUsersTime.append(time())

    def removeOfflineUser(self, username):
        # check if previously went offline
        if username in self.offlineUsers:
            x = self.offlineUsers.index(username)
            self.offlineUsers.remove(username)
            self.offlineUsersTime.pop(x)
    
    def initialiseValidUsers(self):
        credFile = open("credentials.txt",'r')
        creds = credFile.readlines()
        credFile.close()
        for x in creds:
            userpass = x.split(" ")
            username = userpass[0]
            self.validUsers.append(username)

    def addValidUser(self, username):
        self.validUsers.append(username)

    def storeMessage(self, sender, target, message):
        self.storedMessages.append([target,sender,message])



status = serverStatus()

status.initialiseValidUsers()

while 1:
    serverSocket.listen(1)

    cSocket, addr = serverSocket.accept()

    cThread = clientThread(addr, cSocket)

    cThread.start()

            
cSocket.close()
serverSocket.close()