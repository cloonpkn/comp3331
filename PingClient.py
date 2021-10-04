import sys
import socket
from datetime import datetime
import time

serverName = sys.argv[1]
serverPort = int(sys.argv[2])

#print ('Host: ', serverName, ' Port: ', serverPort)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(0.6)

rttList = []
sequenceNumber = 3331
while sequenceNumber < 3346:

    #sendTime = datetime.now()
    #time = sendTime.strftime("%d/%m/%Y %H:%M:%S")
    sendTime = time.time()
    messageTime = time.asctime(time.localtime(time.time()))
    

    message = "PING %d "%sequenceNumber + messageTime + "\r\n"

    clientSocket.sendto(message,(serverName, serverPort))

    try:
        returnMessage, serverAddress = clientSocket.recvfrom(2048)
        receiveTime = time.time()
        rtt = (receiveTime - sendTime) * 1000
        rttList.append(rtt)

        #print (returnMessage)
        print ("ping to " + serverName + ", seq = %d , rtt = %dms \r\n"%(sequenceNumber,rtt))
    except socket.timeout:
        print ("ping to " + serverName + ", seq = %d , time out \r\n"%sequenceNumber)

    sequenceNumber = sequenceNumber + 1

clientSocket.close()

print "Max RTT: ", max(rttList), ". Min RTT: ", min(rttList), ". Average RTT: ", sum(rttList)/len(rttList)