import socket

class TCPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = '0.0.0.0'
        self.server_port = 9001
        self.sock.bind((self.server_address, self.server_port))

    def start(self):
        self.sock.listen(1)


