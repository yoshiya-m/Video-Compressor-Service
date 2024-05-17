import socket
import sys
import os

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

        try:
            # start sending data to server
            with open(filepath, 'rb') as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, 0)

                if filesize > pow(2, 32):
                    raise Exception ('File must be below 4GB')
                
                filename = os.path.basename(f.name)

                data = f.read(1400)
                while data:
                    print('sending')
                    self.sock.send(data)
                    data = f.read(1400)
                

        finally:
            print('Closing socket')
            self.sock.close()






tcp_client = TCPClient()
tcp_client.start()

