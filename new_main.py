import ConfigParser
import sys
import socket
import string
import time
import datetime
import os
import pickle
from collections import defaultdict
sys.path.append("C:\Users\TKW\Desktop\fun.py")
import fun

def main():
	#Load config file
	#Config file should have HOST, PORT, NICK, IDENT, REALNAME and MASTER
	config = ConfigParser.ConfigParser()
	config.read("config.ini")
	config.sections()
	
	#Define the socket
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	#Connect to network config.get('Default', 'IDENT')
	irc.connect((config.get('Default', 'HOST'), int(config.get('Default', 'PORT'))))
	irc.send("USER %s %s bla :%s\r\n" % (config.get('Default', 'IDENT'),
	    config.get('Default', 'HOST'), config.get('Default', 'REALNAME')))
	irc.send("NICK " + config.get('Default', 'NICK') + "\r\n")

	f = fun.functions(irc)
	
	try:
		alert_log = pickle.load(open("alertlog.p", "rb+"))
		print alert_log
	except EOFError:
		alert_log = defaultdict(list)
		pickle.dump(alert_log, open("alertlog.p", "wb"))
		alert_log = pickle.load(open("alertlog.p", "rb"))
		
	with open("to_remind.txt", "a+") as r:
		to_remind_list = r.read().splitlines()
	
	#Loop constantly until prompted otherwise
	#Bot operates by searching for triggers in text
	#For the unfamiliar per RFC 2812 IRC messages MUST be terminates in CR-LF (\r\n) and shall not
	#exceed 512 characters, typically you'd implement a buffer to deal with this, this bot currently
	#has no such buffer designed (though it may in the future), be aware of this while making any changes.
	while(1):
		text = irc.recv(2040) #receive the text
		print text 
		user = text.split('!')[0] #Notes most recent user, while ignoring the host/vhost
		user = user[1:len(user)] #strip the : that will lead the user
		irc.send("NOTICE TKW:I'm connected lol\r\n")
		
		if(text.find(":This nickname is registered and protected.") != -1):
			f.identify(config.get('Default', 'PASSWORD'))
			f.join(config.get('Default', 'CHANNELS'))
			irc.send("PRIVMSG %s :Hello Master\r\n" % config.get('Default', 'MASTER'))
		
		if(text.find('PING') != -1):
			f.pong(text)
		
		if(text.find(':!quit') != -1):
			f.quit()
		
		if(text.find(':!echo') != -1):
			f.echo(text, user, config.get('Default', 'NICK'))
		
		if(user in to_remind_list):
			f.remind(user)
		
		if(text.find(':!alert_me') != -1):
			f.set_alert(text, user, alert_log)
		
		if(text.find(':!remind') != -1):
			f.set_reminder(text, user, to_remind_list)
		
		if(text.find('JOIN') != -1 and text.find(config.get('Default', 'NICK')) != 1):
			for x in alert_log.items():
				if(user in x[0]):
					f.alert(x)
		
		
main()