MAX_CONNECTION = 4
NB_PLAYER = 1#4
def send_to(target_sock, data):
    target_sock.send(data.encode())
