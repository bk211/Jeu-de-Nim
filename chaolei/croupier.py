#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket,select
import threading
import time
from collections import OrderedDict
from global_settings_and_functions import NB_PLAYER, send_to
#import queue
from game_manager import Game_data_manager
from multiprocessing import Queue
class Croupier():
    """docstring for ."""

    def __init__(self, players):
        self.players = players
        self.gdm = Game_data_manager()
        print("initialization complete, croupier rdy")
        for sock, name in self.players.items():
            print("{} IS {}".format(sock.getsockname(),name))
            self.gdm.add_new_player()
            send_to(sock, "MSG Croupier Bienvenue, la table est prête")
        send_to(self.conv_pnumber_to_psock(0), "MSG Croupier En attente de votre signal de lancement")

        self.received_queue =Queue()
        self.current_game_phase = 0
        self.current_player_turn = 0
        self.players_statut = [1 for x in range(NB_PLAYER)]
        self.start_treating()

    def get_current_player_sock(self):#retourne la socket du joueur qui a la main
        return self.conv_pnumber_to_psock(self.current_player_turn)

    def brodcast(self, data):
        for player_sock in self.players:
            send_to(player_sock, data)

    def start_treating(self):
        print("Croupier has started his treating thread")
        self.thread_treating = threading.Thread(target = self.treating)
        self.thread_treating.start()

    def treating(self):
        while self.current_game_phase == 0:
            #if not self.received_queue.empty():
            data = self.received_queue.get()
            print(data)
            if data == "STR":
                self.current_game_phase = 1
                print("value changed")
            else:
                send_to(self.conv_pnumber_to_psock(0), "MSG Croupier En attente de votre signal de lancement")


        self.gdm.deal_cards_to_all()
        self.send_hand_to_all()
        self.brodcast("MSG Croupier Les cartes sont distribuées, merci de miser")

        while self.current_game_phase == 1:
            self.start_bet_phase()
            break

        print("reached the end")

    def start_bet_phase(self):
        current_player_number = 0
        requiered_entry_fee =0
        print("reached")
        while not self.gdm.check_bet_phase_done(requiered_entry_fee):

            current_player_number = current_player_number % NB_PLAYER
            current_statut = self.gdm.get_player_statut(current_player_number)
            print("bk1")
            if not self.gdm.check_player_bet_done(current_player_number, requiered_entry_fee):
            #si le joueur est engagé dans la partie, s'il n'est pas en all in, si ce qu'il a misé est inférieur à entrée necessaire
                print("bk2")
                self.ask_input_to_player_sock(self.conv_pnumber_to_psock(current_player_number))#demande de miser
                print("bk3")

                player_rep = self.received_queue.get()#recupere sa reponse
                player_rep = player_rep.split()
                print(">>debug_line: ",player_rep)
                if player_rep[0] == "PUT":#si le joueur mise
                    player_input = int(player_rep[1]) #reconverti sa mise en int
                    player_wallet = self.gdm.get_player_wallet(current_player_number) #check son portefeuille

                    if player_wallet <=  0 :#s'il n'a pas de jeton
                        self.gdm.set_player_statut(current_player_number, 0)# dehors

                    elif player_input >= requiered_entry_fee:# s'il mise plus ou égal que l'entrée necessaire
                        if player_wallet <= requiered_entry_fee:#s'il n'a pas assez, il s'agit d'un all in
                            self.gdm.set_player_statut(current_player_number, 2) #son statut est update en 2 (all in)
                        else:#sinon, il en a assez pour miser
                            requiered_entry_fee = player_input #on update l'entry fee
                        self.gdm.set_player_chip(current_player_number, player_wallet)# dans les 2 cas, on pose les jetons sur la table

                    else:#il n'a pas assez, il s'agit d'un all in
                        self.gdm.set_player_statut(current_player_number, 2)
                        self.gdm.set_player_chip(current_player_number, player_wallet)

                    current_player_number +=1 #on passe au joueur suivant

                elif player_rep[0] == "FLD":#il se couche
                    self.gdm.set_player_statut(current_player_number, 0)# dehors
                    current_player_number +=1 #on passe au joueur suivant
                else:
                    send_to(self.conv_pnumber_to_psock(current_player_number), "MSG Croupier Merci de respecter les format")

    def send_hand_to_player_sock(self, player_sock):
        player_hand = self.gdm.get_player_hand(self.conv_psock_to_pnumber(player_sock))
        player_hand = " ".join(map(str, player_hand))
        if player_hand != "":
            send_to(player_sock , "GET "+player_hand)

    def send_hand_to_all(self):
        for player_sock in self.players:
            self.send_hand_to_player_sock(player_sock)

    def ask_input_to_player_sock(self,player_sock):
        print("bk2.2")
        current_wallet = self.gdm.get_player_wallet(self.conv_psock_to_pnumber(player_sock))
        print("bk4")
        send_to(player_sock, "REQ PUT {}".format(current_wallet))

    def conv_pnumber_to_psock(self, pnumber):
        x = 0
        for player_sock in self.players:
            if x == pnumber:
                return player_sock
            x += 1

    def conv_psock_to_pnumber(self, psock):
        player_number =0
        for player_sock in self.players:
            if player_sock == psock:
                return player_number
            player_number +=1


    def push_to_rqueue(self, content):
        self.received_queue.put(content)

def main():
    pass
if __name__ == '__main__':
    main()
