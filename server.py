import socket
import os
import ffmpeg

class TCPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = '0.0.0.0'
        self.server_port = 9001
        self.sock.bind((self.server_address, self.server_port))

    def protocol_responce(self, state, message):
        return state.to_bytes(2, "big") + len(message.encode('utf-8')).to_bytes(2, "big") + message.encode('utf-8')
    
    # make mp3 file from mp4
    def convert_into_mp3(self, inputfile):
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
            status_message = {
                200: 'ok'
            }

            # return responce. 16 bytes message that includes status code
            state = 200
            message = status_message[state]
            responce = self.protocol_responce(state, message)
            #self.sock.send(responce)
            
            
            # for i in range(1, 6):
            #     self.change_aspect('sample.mp4', i)
            #self.convert_into_mp3('sample.mp4')
            # aspect_ratio = 
            #self.change_aspect('sample.mp4', aspect_ration)
            
            # self.change_resolution('sample.mp4', 3)
            # self.compress('sample.mp4')
            self.convert_to_gif('sample.mp4', 12, 5)


        except Exception as e:
            print('error: ' + str(e))

        finally:
            print('Closing current connection')
            connection.close()



tcp_server = TCPServer()
tcp_server.start()

        