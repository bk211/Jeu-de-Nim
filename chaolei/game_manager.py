#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets

HAND_SIZE = 4
WALLET_INIT_AMOUNT = 100
class Game_data_manager():
    """docstring for ."""

    def __init__(self):
        self.cards_deck= [ x for x in range(4)]*8 + [-1, -1]
        self.pile_table = 0
        self.players_hands = dict()
        self.players_wallets = dict()
        self.cards_bin = []

    def reset_pile(self):
        self.pile_table = 0

    def update_pile(self, card):
        self.pile_table += card

    def check_valid_card_from_deck(self, card):
        return card in self.cards_deck

    def check_valid_card_from_hand(self, player_name, card):
        return card in self.players_hands[player_name]

    def remove_card_from_deck(self, card):
        if self.check_valid_card_from_deck(card):
            self.cards_deck.remove(card)
            return True
        return False

    def remove_card_from_hand(self, player_name, card):
        if self.check_valid_card_from_hand(player_name, card):
            self.cards_bin.append(self.players_hands[player_name].pop(card))
            return True
        return False

    def play_hand(self, player_name, card):
        if self.remove_card_from_hand(player_name, card):
            self.update_pile(card)
            return True
        return False

    def add_new_player(self, player_name):
        self.players_hands[player_name] = []
        self.players_wallets[player_name] = WALLET_INIT_AMOUNT

    def modifie_wallets(self, player_name, amount):
        self.players_wallets[player_name] += amount

    def give_cards_to_all(self):
        for player,hand in self.players_hands.items():
            for x in range(HAND_SIZE):
                choice = secrets.choice(self.cards_deck)
                self.remove_card_from_deck(choice)
                hand.append(choice)






def main():
    _g = Game_data_manager()
    print(_g.cards_deck)
    _g.add_new_player("player1")
    _g.add_new_player("player2")
    print(_g.players_hands)
    _g.give_cards_to_all()
    print(_g.cards_deck)
    print(_g.players_hands)
if __name__ == '__main__':
    main()
