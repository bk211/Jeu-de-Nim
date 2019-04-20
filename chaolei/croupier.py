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
            self.gdm.add_new_player(name)
            send_to(sock, "MSG Croupier Bienvenue, la table est prête")
        send_to(self.select_player(0), "MSG Croupier En attente de votre signal de lancement")

        self.received_queue =Queue()
        self.current_game_phase = 0
        self.current_player_turn = 0
        self.start_treating()

    def get_current_player_sock(self):#retourne la socket du joueur qui a la main
        return self.select_player(self.current_player_turn)

    def brodcast(self, data):
        for player_sock in self.players:
            send_to(self.players, data)

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
                send_to(self.select_player(0), "MSG Croupier En attente de votre signal de lancement")


        print("Start phase")
        self.gdm.deal_cards_to_all()
        self.send_hand_to_all()
        #while self.current_game_phase == 1:
        #    pass

    def send_hand_to_player_sock(self, player_sock):
        player_hand = self.gdm.get_player_hand(self.players[player_sock])
        player_hand = " ".join(map(str, player_hand))
        if player_hand != "":
            send_to(player_sock , "GET "+player_hand)

    def send_hand_to_all(self):
        for player_sock in self.players:
            self.send_hand_to_player_sock(player_sock)

    def ask_input_to_player_sock(self,player_sock):
        current_wallet = self.gdm.get_player_wallet(self.players[player_sock])
        send_to(player_sock, "REQ PUT {}".format(current_wallet))

    def select_player(self, number):
        x = 0
        for player_sock in self.players:
            if x == number:
                return player_sock
            x += 1

    def push_to_rqueue(self, content):
        self.received_queue.put(content)

def main():
    pass
if __name__ == '__main__':
    main()
