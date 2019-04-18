#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket,select
import threading
import time
#import queue
from multiprocessing import Queue
from game_manager import Game_data_manager
from croupier import Croupier
MAX_CONNECTION = 4
NB_PLAYER = 1#4


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
        self.current_nb_connected = 0
        self.current_nb_players = 0
        self.allow_connection = True
        self.allow_recept = True
        self.allow_treat =True
        self.allow_sending = True
        self.croupier = None

        self.inputs = [self.server]

        self.to_do_queue = Queue()
        self.gdm = Game_data_manager()
        self.players_list = dict()
        self.spectators_list = dict()

    def start_receiving_accept(self):
        if self.bind_statut:
            print("start receving and accept thread")
            self.thread_receiving_accept = threading.Thread(target = self.receiving_accept)
            self.thread_receiving_accept.start()
        #self.thread_receiving_accept.join()
    def receiving_accept(self):
        while self.allow_connection or self.allow_recept:
            #print("bk1")
            rlist, wlist, elist = select.select(self.inputs,[],[])

            #print("bk2")
            for s in rlist:
                if s is self.server and self.allow_connection:
                    conn, cliaddr = s.accept()
                    print("connection from {}".format(cliaddr))
                    self.inputs.append(conn)

                    if self.current_nb_connected < MAX_CONNECTION:
                        self.players_list[conn] = "VISITOR"
                        self.send_to(conn,"WHO")
                    else:
                        self.spectators_list[conn] = "VISITOR"
                        self.send_to(conn,"WHO")

                    self.brodcast("new connection from {}".format(cliaddr))
                    self.current_nb_connected +=1

                else:
                    data = s.recv(1024)
                    if data:
                        if "IAM" in data.decode():
                            if self.add_to_lists(s, data):
                                print("add new player {}".format(data[4:].decode()))
                                self.current_nb_players +=1
                                self.croupier = Croupier()
                        else:
                            self.to_do_queue.put(data.decode())
                            print(">>data received")
                    else:#socket closing
                        s.close()
                        print("removed socket :{}".format(s))
                        self.inputs.remove(s)
        print("End receiving_accept thread")

    def add_to_lists(self, player_sock, raw_data):
        data = raw_data.decode().split()
        if len(data) != 2:# erreur format:IAM PSEUDO
            self.send_to(player_sock, "ERR ARGV MISMATCH")
            return False
        if data[0] == "IAM":#bonne entete
            if player_sock in self.players_list:
                if data[1] not in self.players_list.values():#si le pseudo n'est pas pris
                    if self.players_list[player_sock] == "VISITOR": #si le pseudo n'est pas set(evite les changement de pseudo)
                        self.players_list[player_sock] = data[1]
                        return True
                    self.send_to(player_sock, "ERR PSEUDO ALEADY SET")
                    return False
                self.send_to(player_sock, "ERR PSEUDO USED")
                return False
            else:
                if data[1] not in self.spectators_list.values():
                    self.spectators_list[player_sock] = data[1]
                    self.send_to(player_sock, "WELCOME!! ")
                    return True
                self.send_to(player_sock, "ERR PSEUDO USED")
                return False
        self.send_to(player_sock, "ERR ENTETE")
        return False#erreur entete


    def send_to(self, target_sock, data):
        target_sock.send(data.encode())

    def brodcast(self, data):
        for s in self.inputs[1:]:
        #    if s is not self.server :
            self.send_to(s, data)

    def start_sending_all(self):
        if self.bind_statut:
            print("start sending thread")
            self.thread_sending = threading.Thread(target = self.sending)
            self.thread_sending.start()


    def sending(self):
        while self.allow_sending:

            usr_input = input()
            if "::STOP" in usr_input:
                print("Signal STOP received, end sending thread")

            elif"::RAGNAROK" in usr_input:
                print("endjdioawjdiwo")
            self.brodcast(usr_input)

    def start_treating(self):
        if self.bind_statut:
            print("start treating thread")
            self.thread_treating = threading.Thread(target = self.treating)
            self.thread_treating.start()

    def treating(self):
        while self.allow_treat:
            while(not self.to_do_queue.empty()):#obsolete, cat Queue.get() est bloquant par defaut, a changer
                data = self.to_do_queue.get().split()
                if data[0] == "MSG":
                    print("arg = MSG, brodcasting to everyone")
                    self.brodcast(" ".join(data))
                else:
                    print(">>received :"+" ".join(data))#to do, pushe to the croupier

    def close(self):
        self.allow_receiving = False
        self.allow_connection = False
        self.allow_sending = False
        self.allow_treat = False
        self.server.close()
        print("Program end engaged, waiting for running threads to close")





def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Server("localhost",4567)
    _s.start_receiving_accept()
    _s.start_sending_all()
    _s.start_treating()
if __name__ == '__main__':
    main()
