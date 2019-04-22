#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket,select
import threading
import time, os
from collections import OrderedDict
from global_settings_and_functions import NB_PLAYER, send_to
#import queue
from game_manager import Game_data_manager
from multiprocessing import Queue
class Croupier():
    """docstring for ."""

    def __init__(self, players, server):
        self.players = players
        self.server = server
        self.gdm = Game_data_manager()
        print("initialization complete, croupier rdy")
        for sock, name in self.players.items():
            print("{} IS {}".format(sock.getsockname(),name))
            self.gdm.add_new_player()
            send_to(sock, "MSG Croupier Bienvenue, la table est prête")
        send_to(self.conv_pnumber_to_psock(0), "MSG Croupier En attente de votre signal de lancement")

        self.received_queue =Queue()
        self.current_player_turn = 0
        self.players_statut = [1 for x in range(NB_PLAYER)]
        self.current_entry_fee = 0
        self.start_treating()

    def get_player_name(self, player_number):
        return self.players[self.conv_pnumber_to_psock(player_number)]

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
        self.wait_for_STR_signal()

        while(True):#while self.check_winner():
            self.gdm.deal_cards_to_all()
            self.send_hand_to_all()
            self.brodcast("MSG Croupier Les cartes sont distribuées, merci de miser")

            self.start_bet_phase()
            self.start_game_phase()
            if self.give_earning():
                break

        self.close()

    def wait_for_STR_signal(self):
        while True:
            #if not self.received_queue.empty():print(data)

            data = self.received_queue.get()
            if data == "STR":
                return True
            else:
                send_to(self.conv_pnumber_to_psock(0), "MSG Croupier En attente de votre signal de lancement")

    def start_bet_phase(self):
        self.current_entry_fee = 0
        while not self.gdm.check_bet_phase_done(self.current_entry_fee):
            for player in range(NB_PLAYER):#itere sur toutes les joueurs
                while not self.gdm.check_player_bet_done(player, self.current_entry_fee):#Tant que ce joueur n'a pas fini son mise
                    player_wallet = self.gdm.get_player_wallet(player) #check son portefeuille
                    self.brodcast("MSG Croupier c'est au joueur {} de miser".format(self.get_player_name(player)))
                    self.ask_input_to_player_sock(self.conv_pnumber_to_psock(player), "PUT", player_wallet)
                    player_rep = self.received_queue.get()#recupere sa reponse
                    player_rep = player_rep.split()
                    if player_rep[0] == "PUT":#si le joueur mise
                        try:
                            player_input = int(player_rep[1]) #reconverti sa mise en int
                        except:
                            send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de respecter les format")
                            continue
                        if player_wallet <=  0 or player_input == 0:#s'il n'a pas de jeton
                            self.gdm.set_player_statut(player, 0)# dehors
                            self.brodcast("ANN PUT {} {}".format(self.get_player_name(player), 0))

                        elif player_wallet < player_input:
                            send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Vous n'avez pas assez de jetons")

                        elif player_input < self.current_entry_fee:# s'il mise moins que l'entrée necessaire
                            if player_wallet > player_input:
                                send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Vous devez miser un montant valide")

                            else:
                                self.gdm.set_player_statut(player, 2) #son statut est update en 2 (all in)
                                self.gdm.set_player_chip(player, player_wallet)
                                self.brodcast("ANN PUT {} {}".format(self.get_player_name(player), player_wallet))

                        else:#sinon, il en a assez pour miser
                            self.current_entry_fee = player_input #on update l'entry fee
                            self.gdm.set_player_chip(player, player_input)
                            self.brodcast("ANN PUT {} {}".format(self.get_player_name(player), player_input))


                    elif player_rep[0] == "FLD":#il se couche
                        self.gdm.set_player_statut(player, 0)# dehors
                        self.brodcast("ANN FLD {}".format(self.get_player_name(player)))

                    else:
                        send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de respecter les format")

                self.current_player_turn = (self.current_player_turn +1)% NB_PLAYER

    def start_game_phase(self):
        while not self.gdm.check_loser():
            for player in range(NB_PLAYER):


                if self.gdm.check_loser():
                    break
                if self.gdm.check_empty_hand(player):
                    self.gdm.deal_card_to_player(player)
                    self.gdm.deal_card_to_player(player)
                    self.send_hand_to_player_sock(self.conv_pnumber_to_psock(player))

                if self.gdm.get_player_statut(player):# 1 or 2
                    played_a_card = False
                    while not played_a_card:
                        self.brodcast("MSG Croupier c'est au joueur {} de jouer une carte".format(self.get_player_name(player)))
                        self.ask_input_to_player_sock(self.conv_pnumber_to_psock(player), "PLY", " ")#demande au joueur de jouer une carte
                        player_rep = self.received_queue.get()#recupere sa reponse
                        player_rep = player_rep.split()
                        if player_rep[0] == "PLY":
                            try:
                                player_input = int(player_rep[1]) #reconverti sa mise en int
                            except:
                                send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de respecter les format")
                                continue
                            if self.gdm.remove_card_from_hand(player, player_input):#carte valide et joue
                                self.brodcast("ANN PLY {} {}".format(self.get_player_name(player), player_input))

                                self.brodcast("MSG Croupier la pile vaut maintenant {}".format(self.gdm.get_pile()))
                                played_a_card =True
                            else:
                                send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de joueur une carte valide")
                        else:
                            send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de respecter les format")
                    self.current_player_turn = (self.current_player_turn +1)% NB_PLAYER


    def give_earning(self):
        loser =self.gdm.find_loser()
        for player in range(NB_PLAYER):
            if self.gdm.get_player_statut(player):
                chip_on_table = self.gdm.get_player_chip(player)
                if loser == player:
                    if chip_on_table < self.current_entry_fee:
                        lose = chip_on_table
                    else:
                        lose = self.current_entry_fee

                    self.brodcast("ANN LOS {} {}".format(self.get_player_name(player), lose))
                    self.gdm.modifie_wallet(player, -lose)
                else:
                    if chip_on_table > self.current_entry_fee:
                        win = chip_on_table
                    else:
                        win = self.current_entry_fee

                    self.brodcast("ANN WIN {} {}".format(self.get_player_name(player), win))
                    self.gdm.modifie_wallet(player, win)

        self.gdm.clear_table()
        if self.gdm.check_winner():
            winner = self.gdm.find_winner()
            self.brodcast("ANN VIC {}".format(self.get_player_name(winner)))
            return True
        return False


    def send_hand_to_player_sock(self, player_sock):
        player_hand = self.gdm.get_player_hand(self.conv_psock_to_pnumber(player_sock))
        player_hand = " ".join(map(str, player_hand))
        if player_hand != "":
            send_to(player_sock , "GET "+player_hand)

    def send_hand_to_all(self):
        for player_sock in self.players:
            self.send_hand_to_player_sock(player_sock)

    def ask_input_to_player_sock(self,player_sock, arg1, arg2):
        send_to(player_sock, "REQ {} {}".format(arg1, arg2))

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

    def close(self):
        for sock in self.players:
            send_to(sock, "BYE")
        self.server.close()
        print("Program end engaged")
        os._exit(0)

def main():
    pass
if __name__ == '__main__':
    main()
