import socket
import os
import time

class TCPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = '0.0.0.0'
        self.server_port = 9001
        self.sock.bind((self.server_address, self.server_port))

    def protocol_responce():
        return 

    def start(self):
        self.sock.listen(1)

        try:
            print('Starting up on {} port {}'.format(self.server_address, self.server_port))

            # make directory to save file
            path = 'storage'
            if not os.path.exists(path):
                os.makedirs(path)

            # receive data

            
            connection, client_address = self.sock.accept()
            # 32 bytes of filelength
            file_size = int.from_bytes(connection.recv(32), "big")
            filename = 'video.mp4'
            # open file to copy data to
            with open(os.path.join(path, filename), "wb+") as f:
             # receive data by 1400 bytes
                while file_size > 0:
                    #time.sleep(1)
                    data = connection.recv(1400)
                    f.write(data)
                    print('received {} bytes'.format(len(data)))
                    file_size -= len(data)
                    print('{} bytes left'.format(file_size))
            print('finished downloading the file from client')

            # try this with http status code
            status_codes = {

            }
            
            # return responce. 16 bytes message that includes status code
            state = 0
            responce = ''
            


        except Exception as e:
            print('error: ' + str(e))

        finally:
            print('Closing current connection')
            connection.close()

tcp_server = TCPServer()
tcp_server.start()

        