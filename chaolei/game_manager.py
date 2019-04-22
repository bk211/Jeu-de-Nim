#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets
from global_settings_and_functions import HAND_SIZE, WALLET_INIT_AMOUNT, PILE_MAX
class Game_data_manager():
    """docstring for GDM, objet spécifique au Croupier pour gérer les données de jeu"""

    def __init__(self):
        ## deck de jeu
        self.cards_deck= [ x for x in range(4)]*6 + [-1, -1]
        ## pile de carte sur la table
        self.pile_table = 0
        ## liste des mains de joueurs
        self.players_hands = []
        ## liste des portefeuille
        self.players_wallets = []
        ## nombre de joueur
        self.player_count = 0
        ## liste des statut de joueur
        self.players_statut = []
        ## liste des jetons placé sur la table pour chaque joueur
        self.players_chip_on_table =[]
        ## poubelle de carte
        self.cards_bin = []
        ## indique le dernier joueur en action
        self.last_player = 0

    ## verifie si la condition de fin de partie est atteint
    def check_loser(self):
        return self.get_pile() > PILE_MAX

    ## trouve le perdant
    def find_loser(self):
        return self.last_player

    ## verifie si un joueur a effectué la moise
    def check_player_bet_done(self,player_number, entry_fee):
        if entry_fee ==0:
            return False
        if self.players_statut[player_number] == 1 and self.players_chip_on_table[player_number] < entry_fee:
            return False
        return True

    ## véfie si toutes les joueurs ont fini la phase de mise
    def check_bet_phase_done(self, entry_fee):
        return all([self.check_player_bet_done(x,entry_fee) for x in range(self.player_count)])

    ## pose un nombre donné de jeton sur la table
    def set_player_chip(self, player_number, chip):
        self.players_chip_on_table[player_number] = chip

    ## retourne le nombre de jeton posé sur la table par un joueur
    def get_player_chip(self, player_number):
        return self.players_chip_on_table[player_number]


    ## retourne la statut d'un joueur
    def get_player_statut(self, player_number):
        return self.players_statut[player_number]

    ## modifie la statut d'un joueur
    def set_player_statut(self, player_number, statut):
        self.players_statut[player_number] = statut

    ## reset la pile
    def reset_pile(self):
        self.pile_table = 0

    ## ajoute une carte à la pile
    def update_pile(self, card):
        self.pile_table += card

    ## retourne la valeur de la pile
    def get_pile(self):
        return self.pile_table

    ## verifie si une carte est dans le deck
    def check_valid_card_from_deck(self, card):
        return card in self.cards_deck

    ## verifie si une carte est dans la main du joueur
    def check_valid_card_from_hand(self, player_number, card):
        return card in self.players_hands[player_number]

    ## enleve une carte du deck
    def remove_card_from_deck(self, card):
        if self.check_valid_card_from_deck(card):
            self.cards_deck.remove(card)
            return True
        return False

    ## enleve une carte de la main
    def remove_card_from_hand(self, player_number, card):
        if self.check_valid_card_from_hand(player_number, card):
            self.cards_bin.append(card)# poubelle
            self.players_hands[player_number].remove(card)# enleve de la main
            self.update_pile(card) # jete sur la pile
            self.last_player = player_number # fini son tour
            return True
        return False

    ## retourne la main d'un joueur
    def get_player_hand(self, player_number):
        return self.players_hands[player_number]

    ## ajoute un nouveau joueur
    def add_new_player(self):
        self.players_hands.append([])
        self.players_wallets.append(WALLET_INIT_AMOUNT)
        self.player_count +=1
        self.players_statut.append(1)
        self.players_chip_on_table.append(0)

    ## retourne le portefeuille du joueur
    def get_player_wallet(self, player_number):
        return self.players_wallets[player_number]

    ## modifie le portefeuille du joueur
    def modifie_wallet(self, player_number, amount):
        self.players_wallets[player_number] += amount
        if self.players_wallets[player_number] <0:
            self.players_wallets[player_number] = 0

    ## remelange ou reset plutot le deck
    def reshuffle(self):
        self.cards_deck= [ x for x in range(4)]*6 + [-1, -1]

    ## distribue les cartes à toutes les joueurs
    def deal_cards_to_all(self):
        self.reshuffle()
        self.player_hands = [ [] for x in range(self.player_count)]# vide la main
        for player in range(self.player_count):
            if self.players_wallets[player]>0 and self.players_statut[player]: # si un joueur est participant
                for x in range(HAND_SIZE):
                    choice = secrets.choice(self.cards_deck)
                    self.remove_card_from_deck(choice)
                    self.players_hands[player].append(choice)

    ## tire une carte et le donne à un joueur
    def deal_card_to_player(self, player_number):
        choice = secrets.choice(self.cards_deck)
        self.remove_card_from_deck(choice)
        self.players_hands[player_number].append(choice)

    ## vérifie si un joueur a la main vide
    def check_empty_hand(self, player_number):
        return self.players_hands[player_number] == []

    ## nettoie la table pour une nouvelle partie
    def clear_table(self):
        self.reset_pile()
        self.players_hands = [[] for x in range(self.player_count)]# vide la main
        self.players_statut = [ 1 for x in range(self.player_count)]# reset les statuts
        self.players_chip_on_table =[ 0 for x in range(self.player_count)]# reset les jetons sur la table
        self.cards_bin = []# vide la poubelle
        self.last_player = 0

    ## vérifie si on a un gagnant final
    def check_winner(self):
        not_empty_count = 0
        for wallet in self.players_wallets:
            if wallet >0 :
                not_empty_count+=1

        if not_empty_count == 1:
            return True
        return False
    ## trouve le gagant final
    def find_winner(self):
        for player in range(self.player_count):
            if self.players_wallets[player]:
                return player
