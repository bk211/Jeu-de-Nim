MAX_CONNECTION = 10
NB_PLAYER = 1#4

HAND_SIZE = 4
WALLET_INIT_AMOUNT = 100

def send_to(target_sock, data):
    target_sock.send(data.encode())
