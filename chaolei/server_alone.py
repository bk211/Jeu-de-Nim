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
        try:
            self.server.bind((self.hostName , self.port))
        except:
            print("Unable to bind")
            return
        print(f"bind on {self.hostName} {self.port}")
        self.server.listen(MAX_CONNECTION)
        self.allow_connection = True
        self.allow_recept = True


        self.inputs = [self.server]
        self.outputs = []

        self.to_do_queue = queue.Queue()

    def start_receiving_accept(self):
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
                else:
                    data = s.recv(1024)
                    if data:
                        self.to_do_queue.put(data)

    def sending(self):
        pass
    def send(self):
        
def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Server("localhost",4567)
    _s.start_receiving_accept()

if __name__ == '__main__':
    main()
