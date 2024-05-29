import socket
import os
import ffmpeg
import json

class TCPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = '0.0.0.0'
        self.server_port = 9001
        self.sock.bind((self.server_address, self.server_port))
        self.folder_path = 'server'
        self.file_name = ''

    # same protocol as client
    def protocol_header(self, json_size, media_type_size, payload_size):
        return json_size.to_bytes(16, "big") + media_type_size.to_bytes(1, "big") + payload_size.to_bytes(47, "big")
    
    # headerのバイトを数字に変更
    def decode_header(self, header):
        return int.from_bytes(header[:16], "big"), int.from_bytes(header[16:17], "big"), int.from_bytes(header[17:64], "big")
    

    def protocol_responce(self, state, message):
        return state.to_bytes(2, "big") + len(message.encode('utf-8')).to_bytes(2, "big") + message.encode('utf-8')
    

    # make mp3 file from mp4
    def convert_to_mp3(self, inputfile):
        self.file_name = 'output.mp3'
        outputfile = os.path.join(self.folder_path, self.file_name) 
        ffmpeg.input(inputfile).output(outputfile, format='mp3').run()
        return

    # change aspect
    def change_aspect(self, inputfile, option):
        ratios = {
            1: '16:9',
            2: '4:3',
            3: '1:1',
            4: '16:10',
            5: '5:4',
        }

        self.file_name = 'output.mp4'
        outputfile = os.path.join(self.folder_path, self.file_name) 
        ffmpeg.input(inputfile).output(outputfile, aspect=ratios[option]).run()
        return

    # change resolution
    def change_resolution(self, inputfile, option):
        resolutions = {
            1: '1280x720',
            2: '1920x1080',
            3: '3840x2160'
        }
        self.file_name = 'output.mp4'
        outputfile = os.path.join(self.folder_path, self.file_name) 
        ffmpeg.input(inputfile).output(outputfile, s=resolutions[option]).run()
        return
    
    # compress mp4
    def compress(self, inputfile):
        self.file_name = 'output.mp4'
        outputfile = os.path.join(self.folder_path, self.file_name) 
        ffmpeg.input(inputfile).output(outputfile, vcodec='libx264', crf=28).run()
        return
    
    # convert mp4 to gif in selected range
    def convert_to_gif(self, input_file, start_time, duration):
        self.file_name = 'output.gif'
        outputfile = os.path.join(self.folder_path, self.file_name) 
        ffmpeg.input(input_file, ss=start_time, t=duration).filter('fps', fps=10).output(outputfile).run()
        return
    

    def start(self):
        self.sock.listen(1)

        try:
            print('Starting up on {} port {}'.format(self.server_address, self.server_port))

            # make directory to save file
            
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)

            connection, client_address = self.sock.accept()
            print('connection accepted')
            input_filename = 'temp.mp4'

            # headerのデータを受信する
            header = connection.recv(64)
            print('header received')
             # headerからデータを取得

            json_size, media_type_size, pay_load_size = self.decode_header(header)
   
            data_size = json_size + media_type_size + pay_load_size
            # bodyのデータを受信する
            body = b''
            while data_size > 0:
                data = connection.recv(data_size if data_size < 1400 else 1400)
                body += data
                data_size -= len(data)
                print('received {} bytes'.format(len(data)))
            print('finished downloading the file from client')
            
            # bodyからデータを取得
            media_type_end = json_size + media_type_size
            payload_end = media_type_end + pay_load_size

            json_data_string = body[:json_size].decode('utf-8')
            json_data = json.loads(json_data_string)
            media_type = body[json_size: media_type_end].decode('utf-8')
            payload = body[media_type_end: payload_end]

            # payloadをファイルに保存する
            with open(os.path.join(self.folder_path, input_filename), "wb+") as f:
                f.write(payload)

            func_index = json_data['func_index']
            target_file = os.path.join(self.folder_path, input_filename)
            # どうやって関数に引数を渡す？　FUNC_INDEXごとに入力変える
            if func_index == 1:
                self.compress(target_file)
            elif func_index == 2:
                option = json_data['option']
                self.change_resolution(target_file, option)
            elif func_index == 3:
                option = json_data['option']
                self.change_aspect(target_file, option)
            elif func_index == 4:
                self.convert_to_mp3(target_file)
            elif func_index == 5:
                start_time = json_data['start_time']
                duration = json_data['duration']
                self.convert_to_gif(target_file, start_time, duration)

            
        except Exception as e:
            print('error: ' + str(e))
            print('Closing current connection')
            connection.close()
            exit()

            
        
        # 送り返す
        try:
            # 処理したファイルをクライアントと同じ方式で返す
            data = {
                'status': 'OK'
            }

            json_data_str = json.dumps(data)
            json_byte_data = json_data_str.encode('utf-8')

            # 処理したファイルのサイズを確認
            with open(os.path.join(self.folder_path, self.file_name), 'rb') as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, 0)
                payload_byte = f.read()
                

            media_type_byte = os.path.splitext(self.file_name)[1][1:].encode('utf-8')
            # HEADER + BODY
            responce_header = self.protocol_header(len(json_byte_data), len(media_type_byte), filesize)
            connection.send(responce_header)

            
            # body
            body = json_byte_data + media_type_byte + payload_byte


            # bodyの送信
            chunk_size = 1400
            i = 0
            data = body[i:i + chunk_size]
            print('Sending data to client...')
            while data:
                connection.send(data)
                i += chunk_size
                data = body[i:i + chunk_size]
            print('Finished sending')

            # 不要なファイルを消去する
            os.remove(os.path.join(self.folder_path, self.file_name))
            os.remove(os.path.join(self.folder_path, input_filename))

        except Exception as e:
            # エラー発生時はJSONファイルを返す
            # jsonデータ
            data = {
                'status': 'NG'
            }
            data['error'] = str(e)
            json_data_str = json.dumps(data)
            json_byte_data = json_data_str.encode('utf-8')
            responce_header = self.protocol_header(len(json_byte_data), 0, 0)
            connection.send(responce_header)
            connection.send(json_byte_data)
        
        finally:
            print('Closing current connection')
            connection.close()




tcp_server = TCPServer()
tcp_server.start()

        