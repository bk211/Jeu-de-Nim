MAX_CONNECTION = 10
NB_PLAYER = 2#4
PILE_MAX = 5#9
HAND_SIZE = 4
WALLET_INIT_AMOUNT = 100
import time
def send_to(target_sock, data):
    time.sleep(0.1)
    target_sock.send(data.encode())
