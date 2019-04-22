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
    """Croupier, objet clé du serveur qui permet la gestion du déroulement du jeu"""

    ## Le constructeur
    # @param dictionnaire de socket/pseudo ainsi que le serveur
    def __init__(self, players, server):
        self.players = players
        self.server = server
        ## lance le gdm qui gère localement les donées de jeu
        self.gdm = Game_data_manager()
        print("initialization complete, croupier rdy")
        for sock, name in self.players.items():
            print("{} IS {}".format(sock.getsockname(),name))
            self.gdm.add_new_player()
            send_to(sock, "MSG Croupier Bienvenue, la table est prête")
        # demande le lancement du jeu
        send_to(self.conv_pnumber_to_psock(0), "MSG Croupier En attente de votre signal de lancement")

        self.received_queue =Queue()
        self.current_player_turn = 0
        # 0 non participant à la partie, 1 participant, 2 participant all in
        self.players_statut = [1 for x in range(NB_PLAYER)]
        # entrée à payer pour rester dans le jeu
        self.current_entry_fee = 0
        self.start_treating()

    ## convertie le numéro de joueur en socket corespondante
    def get_player_name(self, player_number):
        return self.players[self.conv_pnumber_to_psock(player_number)]

    ## retourne la socket du joueur qui a la main
    def get_current_player_sock(self):
        return self.conv_pnumber_to_psock(self.current_player_turn)

    ## fonction de brodcast
    def brodcast(self, data):
        for player_sock in self.players:
            send_to(player_sock, data)
    ## lance le thread de traitement
    def start_treating(self):
        print("Croupier has started his treating thread")
        self.thread_treating = threading.Thread(target = self.treating)
        self.thread_treating.start()

    ## fonction principar qui gère la boucle de jeu
    def treating(self):
        # attend le signal de jeu
        self.wait_for_STR_signal()

        while(True):
            self.gdm.deal_cards_to_all()# distribue  les cartes
            self.send_hand_to_all() # envoie les cartes au joueurs
            self.brodcast("MSG Croupier Les cartes sont distribuées, merci de miser")

            self.start_bet_phase()# lance la phase de mise
            self.start_game_phase()#lance la phase de mise
            if self.give_earning():# tant qu'il n'y a pas de gagnant la boucle continue
                break

        self.close()

    ## fonction d'attente du lancement du jeu, il est bloqué tant que STR n'est pas envoyé par le bon joueur
    def wait_for_STR_signal(self):
        while True:
            #if not self.received_queue.empty():print(data)

            data = self.received_queue.get()
            if data == "STR":
                return True
            else:
                send_to(self.conv_pnumber_to_psock(0), "MSG Croupier En attente de votre signal de lancement")

    ## fonction qui gere la phase de mise
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
    ## fonction qui gère la phase de jeu
    def start_game_phase(self):
        while not self.gdm.check_loser():# tant qu'il n'y a pas de pertant
            for player in range(NB_PLAYER):
                if self.gdm.check_loser():
                    break
                if self.gdm.check_empty_hand(player): # si un joueur n'a plus de carte il en reprends 2
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
                            if self.gdm.remove_card_from_hand(player, player_input):#carte valide et joué
                                self.brodcast("ANN PLY {} {}".format(self.get_player_name(player), player_input))

                                self.brodcast("MSG Croupier la pile vaut maintenant {}".format(self.gdm.get_pile()))
                                played_a_card =True
                            else:
                                send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de joueur une carte valide")
                        else:
                            send_to(self.conv_pnumber_to_psock(player), "MSG Croupier Merci de respecter les format")
                    self.current_player_turn = (self.current_player_turn +1)% NB_PLAYER

    ## phase de calcul de gain
    def give_earning(self):
        ## numéro du perdant
        loser =self.gdm.find_loser()
        for player in range(NB_PLAYER):
            if self.gdm.get_player_statut(player):# si le joueur a participé à la partie
                chip_on_table = self.gdm.get_player_chip(player)
                if loser == player:
                    if chip_on_table < self.current_entry_fee:
                        lose = chip_on_table
                    else:
                        lose = self.current_entry_fee
                    # anonce
                    self.brodcast("ANN LOS {} {}".format(self.get_player_name(player), lose))
                    self.gdm.modifie_wallet(player, -lose)
                else:
                    if chip_on_table > self.current_entry_fee:
                        win = chip_on_table
                    else:
                        win = self.current_entry_fee
                    #anonce
                    self.brodcast("ANN WIN {} {}".format(self.get_player_name(player), win))
                    self.gdm.modifie_wallet(player, win)

        self.gdm.clear_table()
        if self.gdm.check_winner():# s'il y a un gagnant final
            winner = self.gdm.find_winner()
            self.brodcast("ANN VIC {}".format(self.get_player_name(winner)))
            return True
        return False

    ## envoie la main qu'un joueur possède à la bonne socket
    def send_hand_to_player_sock(self, player_sock):
        player_hand = self.gdm.get_player_hand(self.conv_psock_to_pnumber(player_sock))
        player_hand = " ".join(map(str, player_hand))
        if player_hand != "":
            send_to(player_sock , "GET "+player_hand)

    ## distribue les cartes à tous le monde
    def send_hand_to_all(self):
        for player_sock in self.players:
            self.send_hand_to_player_sock(player_sock)

    ## fonction qui permet de lancer une requete
    def ask_input_to_player_sock(self,player_sock, arg1, arg2):
        send_to(player_sock, "REQ {} {}".format(arg1, arg2))

    ## fonction de conversion de numéro de joueur à socket_joueur
    def conv_pnumber_to_psock(self, pnumber):
        x = 0
        for player_sock in self.players:
            if x == pnumber:
                return player_sock
            x += 1

    ## fonction de conversion socket_joueur à numéro de joueur
    def conv_psock_to_pnumber(self, psock):
        player_number =0
        for player_sock in self.players:
            if player_sock == psock:
                return player_number
            player_number +=1

    ## push un contenue à la queue , pour usage externe
    def push_to_rqueue(self, content):
        self.received_queue.put(content)

    ## fonction de fermeture
    def close(self):
        for sock in self.players:
            send_to(sock, "BYE")
        self.server.close()
        print("Program end engaged")
        os._exit(0)
