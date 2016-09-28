import datetime
import pickle
class functions():
	def __init__(self, irc):
		self.irc = irc

	def pong(self, text):
		"""
		Sends PONG to the server when prompted.
		Text provided to allow generic usage across multiple networks.
		"""
		print "Received: " + text
		self.irc.send('PONG ' + text.split() [1] + '\r\n')
		print 'SENDING: PONG ' + text.split() [1] + '\r\n'

	def identify(self, password):
		""""
		Logins bot into its registered nick using PASSWORD in config.ini.
		"""
		self.irc.send("PRIVMSG NickServ :IDENTIFY %s\r\n" % password)

	def join(self, channels):
		"""
		Prompts bot to join channels provided in config.ini.
		"""
		self.irc.send("JOIN %s\r\n" % channels)

	def quit(self):
		"""
		Has bot quit server with quit message.
		Most servers won't use your disconnect message unless you've 
		been connected for over 5 minutes.
		
		Raises:
			SystemExit: Shutdown the bot.
		"""
		print "Trying to quit\n"
		self.irc.send('QUIT :ded\r\n') 
		raise SystemExit(0)

	def echo(self, text, user, nick):
		"""
		Prompts bot to echo the text proceeding :!echo
		"""
		print "Trying to echo\n"
		lines = text.split()
		send_to = ""
		
		if nick in lines:
			send_to = user #If sent as a direct message, echo in kind
		else:
			send_to = lines[2] #If posted in a channel, echo in channel
		
		message = ' '.join(str(x) for x in lines[4:len(lines)]) + "\r\n"
		print (("PRIVMSG %s :" % send_to) + message)		
		self.irc.send(("PRIVMSG %s :" % send_to) + message)	

	def set_reminder(self, text, user, to_remind_list): #automatically convert me to user, add timed responses rather tha just next message, if user not on wait until they are
		"""
		Write a reminder for a certain user (nick based) to a text file.
		Write who the the reminder is for to a seperate file.
		
		Raises:
			IndexError: if reminder is not properly formatted
		"""
		with open('to_remind.txt', "a+") as to_remind:
			to_remind.write(user + "\n") #writes a list of users to remind 
			to_remind_list.append(user)
		
		try:
			print "Logging reminder, please wait warmly\n"
			with open('remind_log.txt', 'a+') as remind_log:
				lines = text.split()
				now = datetime.datetime.now()
				
				if (lines[5] != "that" or lines[6] == None):
					raise IndexError
				
				#Writes a time stamp for the reminder
				remind_log.write('[' + str(now).split('.')[0] + ']  ') 
				#Writers sender and receiver of reminder
				remind_log.write("From: " + user + " For: " + str(lines[4]) + " Channel: " + lines[02] + "  ") 
				#Prints reminder to sender
				self.irc.send(("PRIVMSG %s :" % lines[02]) + ("I will remind %s that " % str(lines[4])) + ' '.join(str(x) for x in lines[6:len(lines)]) + "\r\n") 
				#Writes reminder to log
				remind_log.write("message: " + ' '.join(str(x) for x in lines[6:len(lines)])) 
				remind_log.write('\n')
		except IndexError:
			print "ERROR! Improperly formatted reminder\n"
			self.irc.send(("PRIVMSG %s :" % lines[02]) + "Error! Improperly formatted reminder. (Format: !remind [user] that [message])\r\n")
			
	def remind(self, user):
		""" 
		Loop through the remind log, checking if reminder is for user,
		if so print it out in the channel it was set then delete the 
		reminder from the log.
		"""		
		lines = open('remind_log.txt').readlines()
		for i, line in enumerate(lines[:]):
			line = line.split()
			if user in line[5]:
				message = ' '.join(str(x) for x in line[9:len(line)]) + "\r\n"
				print message
				self.irc.send('PRIVMSG %s :%s, %s wanted me to remind you that %s' % (line[7],line[5], line[3], message))
				del lines[i]
		
		open('remind_log.txt', 'w').writelines(lines)

	def set_alert(self, text, user, alert_log): #Note this should create a dictionary to use rather than .txt file
		"""
		Adds user to a dictionary where nick_ is the key,
		if the key doesn't exist, create it, if it does append.
		
		Raises: 
			IndexError: if command is not properly formatted
			KeyError: if key doesn't exist, create it
		"""
		print "Setting alert dict?\n"
		try:
			#alert_log = open('alert_log.txt', 'a+')
			lines = text.split()
			print lines
			
			if(lines[4] != "if" or lines[5] == None):
				raise IndexError
			
			
			for x in lines[5:len(lines)]:
				#alert_log[str(x).rstrip(',')] = my_dict.get(x.strip(','), user)
				try:
					alert_log[str(x).rstrip(',')].append(user)
				except KeyError:
					alert_log[str(x).rstrip(',')] = user
			
			pickle.dump(alert_log, open("alertlog.p", "wb"))
		except IndexError:
			print "ERROR! Improperly formatted alert list"
			self.irc.send(("PRIVMSG %s:" % user) + " Error! Improperly formatted commmand. (Format: !alert_me if [nick1, nick2, ..., nickN")

	def alert(self, alert_log):
		"""
		alert all users that have requested to be notified for
		an individual user. 
		"""
		for x in range(len(alert_log[1])):
			self.irc.send("PRIVMSG %s :%s IS NOW ONLINE!\r\n" % (alert_log[1][x], alert_log[0]))
