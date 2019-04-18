#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket
from multiprocessing import Queue
import time
import threading
import queue


sharedQueue = Queue()
class Client:
    def __init__(self,clientName,hostName,port):
        self.clientName = clientName
        self.hostName = hostName
        self.ipAddress = socket.gethostbyname(hostName)
        self.port = port
        self.connect_statut = False
        print(f"IP address of the host name {self.hostName} is: {self.ipAddress}")
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        try:
            self.client.connect((self.ipAddress,port))
        except:
            print("Unable to connect")
            return
        print(f"Connection on {self.port}")
        self.connect_statut = True
        self.allow_sending = True
        self.allow_receiving = True

    def close(self):
        self.client.close()

    def start_sending(self):
        if self.connect_statut:
            thread_sending = threading.Thread(target =self.sending)
            thread_sending.start()

    def start_receiving(self):
        if self.connect_statut:
            thread_receiving = threading.Thread(target =self.receiving)
            thread_receiving.start()

    def send_msg(self, msg):
        self.client.send(msg.encode())

    def sending(self):
        while self.allow_sending:
            message = input()
            print(f"sending:{message}")
            if "::STOP" in message:
                print("Signal STOP received, end sending thread")
                self.close()
                break
            self.send_msg(message)



    def receiving(self):
        while self.allow_receiving:
            data = self.client.recv(1024)
            if data:
                data = data.decode().split()
                if data[0] == "LFT":
                    print("Signal LFT received")
                elif data[0] == "MSG":
                    print(">>received message from {} : {}".format(data[1], " ".join(data[2:])))#to do

                elif "cond1" == data[0]:
                    print("cond1 reached")
                    break

                elif "cond2" == data[0]:
                    print("cond2 reached no exit")
                else:
                    print(">>none of swtich meet, here is the raw data :"+" ".join(data))
        print("End receiving thread")

    def close(self):
        self.allow_sending = False
        self.allow_receiving = False
        self.client.close()
        print("Program end engaged, waiting for receiving thread to close")
def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Client("bk","localhost",4567)
    _s.start_sending()
    _s.start_receiving()

if __name__ == '__main__':
    main()
