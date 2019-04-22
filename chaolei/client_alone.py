#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket
from multiprocessing import Queue
import time
import threading
import queue
from global_settings_and_functions import send_to

class Client:
    def __init__(self,hostName,port, GUI_bool):
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
        self.player_name =""
        self.player_hand = []
        self.client_name = None
        self.client_name_accepted = False
        self.GUI_bool= GUI_bool
        self.event_queue = Queue()
        self.start_receiving()
        if not self.GUI_bool:
            self.start_sending()

    def get_event(self):
        data = self.event_queue.get()
        print("")
        return data

    def get_name_statut(self):
        return self.client_name_accepted

    def send_client_name(self, name):
        self.client_name = name
        send_to(self.client, "IAM "+name )

    def get_connect_statut(self):
        return self.connect_statut

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
        send_to(self.client, msg)

    def sending(self):
        while self.allow_sending:
            message = input()
            print(f"sending:{message}")
            if "::STOP" in message:
                print("Signal STOP received, end sending thread")
                self.close()
            else:
                self.send_msg(message)



    def receiving(self):
        while self.allow_receiving:
            try:
                data = self.client.recv(1024)
                if data:
                    data = data.decode().split()
                    if data[0] == "ARV":
                        if data[1] == self.client_name:
                            self.client_name_accepted = True
                            print("Login success")

                    if self.GUI_bool:
                        self.event_queue.put(data)
                    else:
                        self.print_for_user(data)
            except:
                continue

    def print_for_user(self, data):
        if data[0] == "LFT":
            print("Player {} has left".format(data[1]))
        elif data[0] == "WHO":
            print("merci de vous identifier")
        elif data[0] == "MSG":
            print(">>received message from {} : {}".format(data[1], " ".join(data[2:])))

        elif data[0] == "BYE":
            self.close()

        elif data[0] == "ANN":
            if data[1] == "PUT":
                print("Le joueur {} a mise {} ".format(data[2],data[3]))
            if data[1] == "PLY":
                print("Le joueur {} a joué {} ".format(data[2],data[3]))
            if data[1] == "WIN":
                print("Le joueur {} a gagné {} ".format(data[2],data[3]))
            if data[1] == "LOS":
                print("Le joueur {} a perdu {} ".format(data[2],data[3]))
            if data[1] == "VIC":
                print("Le joueur {} remporte la victoire ".format(data[2]))

        elif data[0] == "ARV":
            print(">>New player has joined {}".format(data[1]))
        elif data[0] == "GET":
            print(">>Voici votre main : {}".format(" ".join(data[1:])))
            self.player_hand = map(int, data[1:])
        elif data[0] == "REQ":
            if data[1] == "PUT":
                print("Entrez votre mise, vous disposez de {} jetons".format(data[2]))
            if data[1] == "PLY":
                print("Merci de jouer une carte")

        else:
            print(">>none of switch meet, here is the raw data : "," ".join(data))


    def close(self):
        self.allow_sending = False
        self.allow_receiving = False
        send_to(self.client, "BYE")
        print("Program end engaged")
        os._exit(0)

def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Client("localhost",4567, False)

if __name__ == '__main__':
    main()
