#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket,select
import threading
import time
#import queue
from multiprocessing import Queue
class Croupier():
    """docstring for ."""

    def __init__(self, players):
        self.players = players
        print("initialization complete, croupier rdy")
        for sock, name in self.players.items():
            print("{} IS {}".format(sock.getsockname(),name))

        self.received_queue =Queue()

    def push_to_rqueue(self, content):
        self.received_queue.put(content)

def main():
    pass
if __name__ == '__main__':
    main()
