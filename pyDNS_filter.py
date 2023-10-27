# coding: utf-8
import socket, sys
from threading import Thread

show_debug = True
def debug(inputTxt):
	if show_debug: print(inputTxt)

class Server():
	running = True
	rewriteDict = {}
	
	def __init__(self):
		print("Server starting!")
		try:
			hostsFile = open("hosts")
			for line in hostsFile.readlines():
				if not line:
					break
				if not ":" in line:
					break
				domain, ip_value = line.split(':', 1)
				self.rewriteDict[domain.lower().strip()] = ip_value.strip()
			print(" -*- hostsFile has been loaded -*- \n")
			for item in self.rewriteDict.keys():
				print(item + " " + self.rewriteDict[item]); print("-"*30) # Want to see the rewrites when loaded
		except Exception as e:
			print("\n - hostsFile syntax is '<domain>:<ip>' example 'facebokk.com:127.0.0.1' - Go fix your hosts file!)") #print('Error on line {}: "{}"'.format(sys.exc_info()[-1].tb_lineno, e))
		
	def run(self):
		udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udps.bind(('', 53))
		while self.running:
			try:
				packet, ip = udps.recvfrom(1024) # Receive a UDP packet, parse the packet, get what domain it is requesting
				print("-Received a packet from " + ip[0])
				parsed_domain = self.parse_packet(packet)
				if not parsed_domain:
					print("Error parsing packet! Ignoring..")
				else:
					print("-IP " + ip[0] + "	REQUEST: "  + parsed_domain ) # Now, check if this domain is in the naughty-list or not	
					if parsed_domain in self.rewriteDict: # If in list, we build a custom reply packet and send as reply
						print(" * * * CUSTOM REWRITE * * *")
						udps.sendto( self.build_packet(self.rewriteDict[parsed_domain].split("."), packet), ip)
					else: # if not, we forward the packet to google DNS services and forward the reply
						udps.sendto(self.forwarded_to_GoogleDNS(packet), ip)
			except Exception as e:
				pass # Shit happens.. Keep on reading new incoming even though
	
	def forwarded_to_GoogleDNS(self, data):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
			s.sendto(data, ('8.8.8.8', 53)) # we send the request data to google's DNS server
			d = s.recvfrom(1024) # receive data from google's DNS server (data, addr)
			s.close()
			return d[0]
		except (socket.error, Exception) as e:
			print('Error on line {}: "{}"'.format(sys.exc_info()[-1].tb_lineno, e))

	def build_packet(self, ipArr, original_packet):
		try:
			ipBytes = bytearray("aaaa","utf-8") # Create 4 bytes array that can be modified. One char is one byte, then take each 
			for i in range(4): # number part of the IP (separated by ".") and turn the number to int value and set it as the byte value.
				ipBytes[i] = int(ipArr[i]) # only 0-3, i.e. 4 bytes
			debug(ipBytes)
			custom_packet = b"" + original_packet[:2] + b"\x81\x80" + original_packet[4:6] + original_packet[4:6] + b"\x00\x00\x00\x00"
			custom_packet += original_packet[12:]  # Copying the Domain Name Question from original request
			custom_packet += b"\xc0\x0c"  # Pointer to domain name
			custom_packet += b"\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04"  # Response type, ttl and resource data length
			custom_packet += ipBytes
			debug(custom_packet)
			return custom_packet
		except Exception as e:
			print('Error on line {}: "{}"'.format(sys.exc_info()[-1].tb_lineno, e))

	def parse_packet(self, packet):
		debug(packet)
		data = packet
		if not data.startswith(b"\x00") and not data.endswith(b"\x00\x01"):
			print("Uxpected formatting, this was probably not a valid DNS request packet, rejecting!")
			return False
		try:
			qtype = ( data[2]  >> 3) & 15   # Opcode bits
			if qtype != 0:                  # Standard query
				print("Type is "+str(qtype)+" and not 0") # Let's go ahead and see if we can pull a domain out of it anyway?			
			# The domain name in the request would be split up in parts with ascii chars, each with a header byte that tells the length, fist headerbyte
			readLen = data[12] #  we really need is at [12] It tells how many chars to read. New header byte + payload again, and again until "\x00" 
			data = data[13:][:-4] # Remove the leading header bs bytes and the first length indicator, also the trailing 4 bytes after request domain
			debug(data)
			dataArr = [char for char in data] # Put all remaining chars in an array, easy to pop(0)
			domain = ""
			while readLen > 0:
				for x in range(readLen):
					domain += chr(dataArr.pop(0))
				domain += "."
				readLen = dataArr.pop(0)
			return domain[:-1] # Remove the trailing "."
		except Exception as e:
			print('Error on line {}: "{}"'.format(sys.exc_info()[-1].tb_lineno, e)); return False