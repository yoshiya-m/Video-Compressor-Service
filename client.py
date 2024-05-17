import socket
import sys

class TCPClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = input('Type in a server address to connect to: ')
        self.server_port = 9001
    
    def start(self):
        print('Connecting to {}'.format(self.server_address, self.server_port))
        try:
            self.sock.connect((self.server_address, self.server_port))
        except socket.error as err:
            print(err)
            sys.exit(1)
        
        filepath = input('Type in a file to upload')
        
