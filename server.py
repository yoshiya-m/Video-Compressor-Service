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

    # same protocol as client
    def protocol_header(self, json_size, media_type_size, data):
        return json_size.to_bytes(16, "big") + media_type_size.to_bytes(1, "big") + data

    # headerのバイトを数字に変更
    def decode_header(self, header):
        print('header[:16]: {}'.format(int.from_bytes(header[:16], "big")))
        print('header[16:17]: {}'.format(int.from_bytes(header[16:17], "big")))
        print('header[17:64]: {}'.format(int.from_bytes(header[17:64], "big")))
        return int.from_bytes(header[:16], "big"), int.from_bytes(header[16:17], "big"), int.from_bytes(header[17:64], "big")
    

    def protocol_responce(self, state, message):
        return state.to_bytes(2, "big") + len(message.encode('utf-8')).to_bytes(2, "big") + message.encode('utf-8')
    
    # make mp3 file from mp4
    def convert_to_mp3(self, inputfile):
        outputfile = 'output.mp3'
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

        outputfile = 'output.mp4'
        ffmpeg.input(inputfile).output(outputfile, aspect=ratios[option]).run()
        return

    # change resolution
    def change_resolution(self, inputfile, option):
        resolutions = {
            1: '1280x720',
            2: '1920x1080',
            3: '3840x2160'
        }
        outputfile = 'output.mp4'
        ffmpeg.input(inputfile).output(outputfile, s=resolutions[option]).run()
        return
    
    # compress mp4
    def compress(self, inputfile):
        outputfile = 'output.mp4'
        ffmpeg.input(inputfile).output(outputfile, vcodec='libx264', crf=28).run()
        return
    
    # convert mp4 to gif in selected range
    def convert_to_gif(self, input_file, start_time, duration):
        output_gif = 'output.gif'
        ffmpeg.input(input_file, ss=start_time, t=duration).filter('fps', fps=10).output(output_gif).run()
        return
    

    def start(self):
        self.sock.listen(1)

        try:
            print('Starting up on {} port {}'.format(self.server_address, self.server_port))

            # make directory to save file
            path = 'storage'
            if not os.path.exists(path):
                os.makedirs(path)

            connection, client_address = self.sock.accept()
            print('connection accepted')
            filename = 'temp.mp4'

            # headerのデータを受信する
            header = connection.recv(64)
            print('header received')
             # headerからデータを取得

            json_size, media_type_size, pay_load_size = self.decode_header(header)
   

            # bodyのデータを受信する
            body = b''
            data = connection.recv(1400)
            while data:
                body += data
                print('received {} bytes'.format(len(data)))
                data = connection.recv(1400)
            print('finished downloading the file from client')
            
            # bodyからデータを取得
            # json_data_byte + media_type_byte + mp4_data_byte
            media_type_end = json_size + media_type_size
            payload_end = media_type_end + pay_load_size

            json_data_string = body[:json_size].decode('utf-8')
            json_data = json.loads(json_data_string)
            media_type = body[json_size: media_type_end].decode('utf-8')
            payload = body[media_type_end: payload_end]

            # payloadだけファイルに保存する
            # open file to copy data to
            with open(os.path.join(path, filename), "wb+") as f:
                f.write(payload)

            # try this with http status code
            status_message = {
                200: 'ok'
            }

            # return responce. 16 bytes message that includes status code
            state = 200
            message = status_message[state]
            responce = self.protocol_responce(state, message)
    
            # functions = {
            #     1: self.compress,
            #     2: self.change_resolution,
            #     3: self.change_aspect,
            #     4: self.convert_to_mp3,
            #     5: self.convert_to_gif
            # }

            func_index = json_data['func_index']
            target_file = os.path.join(path, filename)
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

        finally:
            print('Closing current connection')
            connection.close()



tcp_server = TCPServer()
tcp_server.start()

        