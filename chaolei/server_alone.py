#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket,select
import threading
import time
import queue

MAX_CONNECTION = 10

class Server:
    def __init__(self,hostName,port):
        self.hostName = hostName
        #self.ipAddress = socket.gethostbyname(hostName)
        self.port = port
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.bind_statut = False
        try:
            self.server.bind((self.hostName , self.port))
        except:
            print("Unable to bind")
            return
        print(f"bind on {self.hostName} {self.port}")
        self.bind_statut = True
        self.server.listen(MAX_CONNECTION)
        self.allow_connection = True
        self.allow_recept = True
        self.allow_treat =True


        self.inputs = [self.server]
        self.outputs = []

        self.to_do_queue = queue.Queue()

    def start_receiving_accept(self):
        if self.bind_statut:
            print("start receving and accept thread")
            self.thread_receiving_accept = threading.Thread(target = self.receiving_accept)
            self.thread_receiving_accept.start()
        #self.thread_receiving_accept.join()
    def receiving_accept(self):
        while self.allow_connection or self.allow_recept:
            #print("bk1")
            rlist, wlist, elist = select.select(self.inputs,self.outputs,[])

            #print("bk2")
            for s in rlist:
                if s is self.server and self.allow_connection:
                    conn, cliaddr = s.accept()
                    print(f"connection from {cliaddr}")
                    self.inputs.append(conn)
                    self.brodcast(f"new connection from {cliaddr}")
                else:
                    data = s.recv(1024)
                    if data:
                        self.to_do_queue.put(data)
                        print(">>data received")

    def send_to(self, target_sock, data):
        target_sock.send(data.encode())

    def brodcast(self, data):
        for s in self.inputs:
            if not s is self.server:
                self.send_to(s, data)

    def start_sending_all(self):
        if self.bind_statut:
            print("start sending thread")
            self.thread_sending = threading.Thread(target = self.sending)
            self.thread_sending.start()

    def sending(self):
        sending_lock = True
        while sending_lock:
            usr_input = input()
            if "::STOP" in usr_input:
                print("Signal STOP received, end sending thread")
                break
            self.brodcast(usr_input)

    def start_treating(self):
        if self.bind_statut:
            print("start sending thread")
            self.thread_treating = threading.Thread(target = self.treating)
            self.thread_treating.start()

    def treating(self):
        while self.allow_treat:
            while(not self.to_do_queue.empty()):
                decoded_data = self.to_do_queue.get().decode().split()
                print(">>received :"+" ".join(decoded_data))
                self.to_do_queue.task_done()

class Game_ruler():
    """docstring for ."""

    def __init__(self, arg):
        self.arg = arg



def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Server("localhost",4567)
    _s.start_receiving_accept()
    _s.start_sending_all()
    _s.start_treating()
if __name__ == '__main__':
    main()
