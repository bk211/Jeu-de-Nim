#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket
import threading
import time

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
        while True:
            message = input()
            print(f"sending:{message}")
            if "::STOP" in message:
                print("Signal STOP received, end sending thread")
                break
            self.send_msg(message)

    def receiving(self):
        while True:
            data = self.client.recv(1024).decode()
            if f"LFT {self.clientName}" in data:
                print("Signal LFT received")
                break

            decoded_data = data.split()
            print("received decoded_data >>:", decoded_data)

            if decoded_data[0] == "MSG":
                print(f">>received:{decoded_data[0:]}")#to do

            if "cond1" in data:
                print("cond1 reached")
                break

            if "cond2" in data:
                print("cond2 reached no exit")
        print("end receiving thread")



def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Client("bk","localhost",4567)
    _s.start_sending()
    _s.start_receiving()

if __name__ == '__main__':
    main()
