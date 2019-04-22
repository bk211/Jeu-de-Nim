#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets
from global_settings_and_functions import HAND_SIZE, WALLET_INIT_AMOUNT, PILE_MAX
class Game_data_manager():
    """docstring for ."""

    def __init__(self):
        self.cards_deck= [ x for x in range(4)]*6 + [-1, -1]
        self.pile_table = 0
        self.players_hands = []
        self.players_wallets = []
        self.player_count = 0
        self.players_statut = []
        self.players_chip_on_table =[]
        self.cards_bin = []
        self.last_player = 0

    def check_loser(self):
        return self.get_pile() > PILE_MAX

    def find_loser(self):
        return self.last_player


    def check_player_bet_done(self,player_number, entry_fee):
        if entry_fee ==0:
            return False
        if self.players_statut[player_number] == 1 and self.players_chip_on_table[player_number] < entry_fee:
            return False
        return True


    def check_bet_phase_done(self, entry_fee):
        return all([self.check_player_bet_done(x,entry_fee) for x in range(self.player_count)])

    def set_player_chip(self, player_number, chip):
        self.players_chip_on_table[player_number] = chip

    def get_player_chip(self, player_number):
        return self.players_chip_on_table[player_number]

    def get_player_statut(self, player_number):
        return self.players_statut[player_number]

    def set_player_statut(self, player_number, statut):
        self.players_statut[player_number] = statut

    def reset_pile(self):
        self.pile_table = 0

    def update_pile(self, card):
        self.pile_table += card

    def get_pile(self):
        return self.pile_table

    def check_valid_card_from_deck(self, card):
        return card in self.cards_deck

    def check_valid_card_from_hand(self, player_number, card):
        return card in self.players_hands[player_number]

    def remove_card_from_deck(self, card):
        if self.check_valid_card_from_deck(card):
            self.cards_deck.remove(card)
            return True
        return False

    def remove_card_from_hand(self, player_number, card):
        if self.check_valid_card_from_hand(player_number, card):
            self.cards_bin.append(self.players_hands[player_number].pop(card))
            self.update_pile(card)
            self.last_player = player_number
            return True
        return False

    def get_player_hand(self, player_number):
        return self.players_hands[player_number]

    def add_new_player(self):
        self.players_hands.append([])
        self.players_wallets.append(WALLET_INIT_AMOUNT)
        self.player_count +=1
        self.players_statut.append(1)
        self.players_chip_on_table.append(0)

    def get_player_wallet(self, player_number):
        return self.players_wallets[player_number]

    def modifie_wallet(self, player_number, amount):
        if self.players_wallets[number] >= amount:
            self.players_wallets[number] += amount
            return True
        return False


    def deal_cards_to_all(self):
        for player in range(self.player_count):
            if self.players_wallets[player]>0:
                for x in range(HAND_SIZE):
                    choice = secrets.choice(self.cards_deck)
                    self.remove_card_from_deck(choice)
                    self.players_hands[player].append(choice)

    def deal_card_to_player(self, player_number):
        choice = secrets.choice(self.cards_deck)
        self.remove_card_from_deck(choice)
        self.players_hands[player_number].append(choice)



def main():
    _g = Game_data_manager()
    print(_g.cards_deck)
    _g.add_new_player()
    _g.add_new_player()
    print(_g.players_hands)
    print(_g.cards_deck)
    print(_g.players_hands)
if __name__ == '__main__':
    main()
