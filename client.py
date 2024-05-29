import socket
import sys
import os
import time
import json

class TCPClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = input('Type in a server address to connect to: ')
        self.server_port = 9001
        self.folder_path = 'client'

    # same protocol as client
    def protocol_header(self, json_size, media_type_size, payload_size):
        return json_size.to_bytes(16, "big") + media_type_size.to_bytes(1, "big") + payload_size.to_bytes(47, "big")

    # headerのバイトを数字に変更
    def decode_header(self, header):
        # print('header[:16]: {}'.format(int.from_bytes(header[:16], "big")))
        # print('header[16:17]: {}'.format(int.from_bytes(header[16:17], "big")))
        # print('header[17:64]: {}'.format(int.from_bytes(header[17:64], "big")))
        return int.from_bytes(header[:16], "big"), int.from_bytes(header[16:17], "big"), int.from_bytes(header[17:64], "big")
    
    def make_json_data(self):
        # set parameters
        # choose one option to execute
        # func_index, inputfile_name, 
        data = {}
        print('-------機能一覧-------')
        print('1: 動画を圧縮する')
        print('2: 動画の解像度を変更する')
        print('3: 動画のアスペクト比を変更する')
        print('4: 動画を音声に変更する')
        print('5: 動画からGIFを作成する')
        func_index = int(input('実行したい機能の番号を入力してください: '))
        while func_index not in [1, 2, 3, 4, 5]:
            print('入力が間違っています。')
            func_index = int(input('実行したい機能の番号を入力してください: '))
        data['func_index'] = func_index

        # change resolution
        if data['func_index'] == 2:
            print('-------解像度一覧-------')
            print('1: 1280x720')
            print('2: 1920x1080')
            print('3: 3840x2160')
            option = int(input('希望する解像度の番号を入力してください: '))
            while option not in [1, 2, 3]:
                print('入力が間違っています。')
                option = int(input('希望する解像度の番号を入力してください: '))
            data['option'] = option

        # change aspect
        elif data['func_index'] == 3:
            print('-------アスペクト比一覧-------')
            print('1: 16:9')
            print('2: 4:3')
            print('3: 1:1')
            print('4: 16:10')
            print('5: 5:4')
            option = int(input('希望するアスペクト比の番号を入力してください:'))
            while option not in [1, 2, 3, 4, 5]:
                print('入力が間違っています')
                option = int(input('希望するアスペクト比の番号を入力してください: '))
            data['option'] = option

        # convert into GIF
        elif data['func_index'] == 5:
            start_time = int(input('動画の切り取り始めを秒数で入力してください: '))
            duration = int(input('何秒間切り取りますか？数字を入力してください: '))
            data['start_time'] = start_time
            data['duration'] = duration
        
        
        
        #クライアントはjsonデータを送る
        # サーバーは受け取ったデータを元に処理する
        json_data_str = json.dumps(data)
        byte_data = json_data_str.encode('utf-8')
        # print('byte_data: {}'.format(byte_data))
        return byte_data
    
    def start(self):
        print('Connecting to {}'.format(self.server_address, self.server_port))
        try:
            self.sock.connect((self.server_address, self.server_port))
        except socket.error as err:
            print(err)
            sys.exit(1)
        
        filepath = input('Type in a file to upload: ')
        media_type_byte = os.path.splitext(filepath)[1][1:].encode('utf-8')
        try:
            # start sending data to server
            with open(filepath, 'rb') as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, 0)

                if filesize > pow(2, 32):
                    raise Exception ('File must be below 4GB')
                
                # filename = os.path.basename(f.name)
                json_data_byte = self.make_json_data()

                # headerの作成と送信
                header = self.protocol_header(len(json_data_byte), len(media_type_byte), filesize)
                self.sock.send(header)
                
                mp4_data_byte = f.read()
                # bodyの作成
                body = json_data_byte + media_type_byte + mp4_data_byte
                
                # bodyの送信 json, media_type, mp4 
                chunk_size = 1400
                i = 0
                data = body[i:i + chunk_size]
                print('Sending data to server...')
                while data:
                    #time.sleep(1)
                    
                    self.sock.send(data)
                    i += chunk_size
                    data = body[i:i + chunk_size]
                print('Finished sending')
                
        except Exception as e:
            print('error: ' + str(e))
            print('Closing socket')
            self.sock.close()
            exit()

        # 処理したファイルを受け取る
        try:
            #headerを受信
            header = self.sock.recv(64)
            # decodeする
            json_size, media_type_size, payload_size = self.decode_header(header)
            # print('json_size: {}'.format(json_size))
            # print('media_type_size: {}'.format(media_type_size))
            # print('payload_size: {}'.format(payload_size))

            body = b''
            data = self.sock.recv(1400)
            print('Receiving data from server...')
            while data:
                body += data
                
                data = self.sock.recv(1400)
            print('Finished receiving data from server')
            
            media_type_end = json_size + media_type_size
            payload_end = media_type_end + payload_size

            json_data_string = body[:json_size].decode('utf-8')
            json_data = json.loads(json_data_string)
            
            media_type = body[json_size: media_type_end].decode('utf-8')
            payload = body[media_type_end: payload_end]
            
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            
            file_name = 'output.' + media_type
            
            with open(os.path.join(self.folder_path, file_name), "wb+") as f:
                f.write(payload)

            if json_data['status'] == 'NG':
                print('Error occured')
                print(json_data['error'])
            else:
                print('processing completed')

        except Exception as e:
            print('error: ' + str(e))

        finally:
            print('Closing socket')
            self.sock.close()


tcp_client = TCPClient()
tcp_client.start()

