#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket,select
import threading
import time
from collections import OrderedDict
#import queue
from multiprocessing import Queue
from croupier import Croupier
from global_settings_and_functions import send_to ,MAX_CONNECTION, NB_PLAYER

class Server:
    """ objet serveur qui va host le jeu"""
    def __init__(self,hostName,port):
        ##variables transparent
        self.hostName = hostName
        self.ipAddress = socket.gethostbyname(hostName)
        ##variables transparent
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
        ## connection maximal
        self.server.listen(MAX_CONNECTION)
        ## sockets connectées actuel
        self.current_nb_connected = 0
        ## nombre de joueurs connectés
        self.current_nb_players = 0
        self.allow_connection = True
        self.allow_recept = True
        self.allow_treat =True
        self.allow_sending = True
        self.croupier = None
        ## statut du jeu
        self.game_statut = False

        self.inputs = [self.server]
        ## queue d'evenement
        self.to_do_queue = Queue()
        ## dictionnaire ordonné qui stock les sockets joueur en keys ainsi que leurs pseudo en valeur
        self.players_dict = OrderedDict()
        ## obsolète
        self.spectators_dict = OrderedDict()

    ## lance le thread qui accept les connection et la reception de données
    def start_receiving_accept(self):
        if self.bind_statut:
            print("start receving and accept thread")
            self.thread_receiving_accept = threading.Thread(target = self.receiving_accept)
            self.thread_receiving_accept.start()

    ## fonction de reception et de acceptation des connections
    def receiving_accept(self):
        while self.allow_connection or self.allow_recept:
            try:
                rlist, wlist, elist = select.select(self.inputs,[],[])
            except:
                continue
            for s in rlist:
                if s is self.server and self.allow_connection:
                    # si nouvelle connection socket
                    conn, cliaddr = s.accept()
                    print("connection from {}".format(cliaddr))
                    self.inputs.append(conn)
                    #demande au socket de s'identifier
                    if self.current_nb_connected < MAX_CONNECTION:
                        self.players_dict[conn] = "VISITOR"
                        send_to(conn,"WHO")
                    else:
                        self.spectators_dict[conn] = "VISITOR"
                        send_to(conn,"WHO")

                    self.current_nb_connected +=1

                else:
                    # sinon, il s'agit d'une reception de donnée
                    try:
                        data = s.recv(1024)
                    except:
                        continue
                    data = data.decode()
                    if data:
                        # si autentification
                        if data[:3] == "IAM" :
                            if self.add_to_lists(s, data):
                                print("add new player {}".format(data[4:]))
                                self.current_nb_players +=1
                                self.brodcast("ARV {}".format(data[4:]))
                                ## si le nombre de joueur necessaire pour le jeu est atteint, le croupier est appelé et le jeu se lance
                                if self.current_nb_players == NB_PLAYER and self.game_statut is False :
                                    self.croupier = Croupier(self.players_dict, self.server)
                                    self.game_statut = True

                        # si message, on retransmet le message au joueurs
                        elif data[:3] == "MSG" or data[:3]=="ANN":
                            print("arg = MSG or ANN, brodcasting to everyone")
                            self.brodcast(data)

                        elif data[:3] in ["STR", "PUT", "PLY"]:#mecanisme de controle qui assure que c'est le bon socket qui envoie une reponse
                            if s is self.croupier.get_current_player_sock():
                                self.croupier.push_to_rqueue(data)
                            else:
                                send_to(s,"MSG Croupier Merci de respecter l'ordre de jeu")

                        elif "BYE" == data:#close signal
                            print("received BYE signal")
                            self.inputs.remove(s)
                            print("removed socket :{}".format(s))
                            if s in self.players_dict:
                                self.brodcast("LFT {}".format(self.players_dict[s]))
                                self.players_dict.pop(s)
                            send_to(s, "BYE")
                            s.close()

                        else:
                            print(">>data received :")
                            print(data)
                    else:#socket closing
                        print("handle closed")
                        self.inputs.remove(s)
                        print("removed socket :{}".format(s))
                        if s in self.players_dict:
                            self.players_dict.pop(s)
                        send_to(s, "BYE")
                        s.close()
        print("End receiving_accept thread")
    ## fonction d'autentification pour une socket retourne True si il est ressit sinon False
    def add_to_lists(self, player_sock, raw_data):
        data = raw_data.split()
        if len(data) != 2:# erreur format:IAM PSEUDO
            send_to(player_sock, "ERR ARGV MISMATCH")
            return False
        if data[0] == "IAM":#bonne entete
            if player_sock in self.players_dict:
                if data[1] not in self.players_dict.values():#si le pseudo n'est pas pris
                    if self.players_dict[player_sock] == "VISITOR": #si le pseudo n'est pas set(evite les changement de pseudo)
                        self.players_dict[player_sock] = data[1]
                        send_to(player_sock, "MSG SYS Welcome")
                        return True
                    send_to(player_sock, "ERR PSEUDO ALEADY SET")
                    return False
                send_to(player_sock, "ERR PSEUDO USED")
                return False
            else:
                if data[1] not in self.spectators_dict.values():
                    self.spectators_dict[player_sock] = data[1]
                    send_to(player_sock, "WELCOME!! ")
                    return True
                send_to(player_sock, "ERR PSEUDO USED")
                return False
        send_to(player_sock, "ERR ENTETE")
        return False#erreur entete


    ## fonction de brodcast
    def brodcast(self, data):
        for s in self.inputs[1:]:
        #    if s is not self.server :
            send_to(s, data)

    ## fonction pour activer la saisit terminal du serveur
    def start_sending_all(self):
        if self.bind_statut:
            print("start sending thread")
            self.thread_sending = threading.Thread(target = self.sending)
            self.thread_sending.start()

    ## si la saisit mannuel est activé, tous ce qui est en entrée sera envoyé en brodcast
    def sending(self):
        while self.allow_sending:

            usr_input = input()
            if "::STOP" in usr_input:
                print("Signal STOP received, end sending thread")
                self.close()
                break
            else:
                self.brodcast(usr_input)

    ## fonction de fermeture du serveur 
    def close(self):
        self.allow_receiving = False
        self.allow_connection = False
        self.allow_sending = False
        for sock in self.inputs[1:]:
            send_to(sock, "BYE")
        self.server.close()
        print("Program end engaged")
        os._exit(0)





def main():
    #s = Client("pablo.rauzy.name",4567)
    _s = Server("localhost",4567)
    _s.start_receiving_accept()
    _s.start_sending_all()

if __name__ == '__main__':
    main()
