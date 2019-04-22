MAX_CONNECTION = 10
NB_PLAYER = 1#4
PILE_MAX = 5#9
HAND_SIZE = 4
WALLET_INIT_AMOUNT = 100
import time
def send_to(target_sock, data):
    time.sleep(0.1)
    try:
        target_sock.send(data.encode())
    except:
        print("send_to failed")
