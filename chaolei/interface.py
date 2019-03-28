#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket
import threading
import time

class Client:
    def __init__(self,hostName,port):
        self.hostName = hostName
        self.ipAddress = socket.gethostbyname(hostName)
        self.port = port
        print(f"IP address of the host name {self.hostName} is: {self.ipAddress}")
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
        
        try:    
            self.client.connect((self.ipAddress,port))
        except:
            print("Unable to connect")
            return
        print(f"Connection on {self.port}")

        self.clientName = " "
        self.thread_receiving = threading.Thread(target =self.receiving)
        self.thread_sending = threading.Thread(target =self.sending)
        self.thread_receiving.start()
        self.thread_sending.start()

        self.thread_sending.join()
        self.thread_receiving.join()


    def sending(self):
        while True:
            message = input()
            print(f"sending:{message}")
            if "::STOP" in message:
                print("Signal STOP received, end sending thread")
                break
            message = message
            self.client.send(message.encode())

    def receiving(self):
        while True:
            data = self.client.recv(1024).decode('utf-8')
            #if f"LFT {self.clientName}" in data:
            if f"LFT {self.clientName}" in data:
                break
            

            print(f">>received:{data}")



            
def main():
    #s = Client("pablo.rauzy.name",4567)
    s = Client("localhost",4567)



if __name__ == '__main__':
    main()
