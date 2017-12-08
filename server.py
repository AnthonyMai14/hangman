import socket
import sys
from thread import *

HOST = ''	# Symobolic name meaning all avaiable interfaces
PORT = 8074	# Arbitrary non-privileged port

clientArray = []
userDictionary = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

try:
	s.bind((HOST, PORT))
except socket.error, msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'


#------------------------------------------------------
#game_menu function: user will be able to choose if they want to be part of a new game or jump onto one going on
def game_menu(conn):
	conn.sendall('-Game Menu-\n\n')
	while True:
		conn.sendall('1.Start New Game\n2.Get list of the Games\n3.Hall of Fame\n4.Exit\n\n-Choice: ')
		game_choice = conn.recv(1024)
		if not game_choice:
			break
		elif game_choice[0] == '1':
			#Start New game
			break
		elif game_choice[0] == '2':
			#Get list of current games
			break
		elif game_choice[0] == '3':
			#hall of fame
			break
		elif game_choice[0] == '4':
			#Exit
			conn.sendall('See you next time!\n')
			#TODO: sign out from server
			clientArray.remove(conn)
			break
		else:
			conn.sendall('\nERROR: Enter valid choice\n\n')
	#came out of loop

#------------------------------------------------------

#------------------------------------------------------
#login function:
def login(conn):
	conn.sendall('-Login-\n\n')
	while True:
		#request username
		conn.sendall('(\'!q\' to go back to main menu)\nUsername: ')
		username_entry = conn.recv(1024)
		username_entry = username_entry.rstrip()
		if username_entry == '!q':
			clientthread(conn)
		#request password
		conn.sendall('Password: ')
		password_entry = conn.recv(1024)
		password_entry = password_entry.rstrip()
		if password_entry == '!q':
			clientthread(conn)
		#TODO: check for valid username
		if userDictionary[username_entry] == password_entry:
			conn.sendall('\nWelcome, ' + username_entry + '\n\n')
			break
		else:
			conn.sendall('\nInvalid password. Please try again\n\n')
	#end of login do_while loop
	#TODO: game screen
#end of login()
#------------------------------------------------------

#------------------------------------------------------
#userExist function: search to see if user_request exist
#if exist, return 1. Else return 0
def userExist(user_request):
	for username in userDictionary:
		if username == user_request:
			return 1
		#end if username == user_request
	#end for username in userDictionary
	return 0
#end of userExist()
#------------------------------------------------------


#-------------------------------------------------------
#sign_up function: Ask for username and password. Once confirm valid,
#send them to sign in screen
def sign_up(conn):
	username_request = ""
	while True:
		conn.sendall('Type in new username (\'!q\' to go back to main menu): ')
		username_request = conn.recv(1024)
		username_request = username_request.rstrip()
		#TODO: check to see if username is valid/availble
		if not username_request:
			conn.sendall('\nERROR: Your username is invalid. Please type again or try another one.\n')
		elif username_request == '!q':
			#go back to main_menu
			clientthread(conn)
		else:
			#TODO: check for special characters (i.e.' ','/','.',etc.). If in username, invalid
			if userExist(username_request):
				conn.sendall('\nERROR: Your username already exist. Please try another username.\n')
			else:
				break
	#end of username_request do_while loop
	while True:
		#**password cannot end with a ' '
		conn.sendall('Type in a new password (\'!q\' to go back to main menu): ')
		password_request = conn.recv(1024)
		password_request = password_request.rstrip()
		if not password_request:
			conn.sendall('\nERROR: Your password is invalid, Please type again or try another one.\n')
		elif password_request == '!q':
			#go back to main_menu
			clientthread(conn)
		else:
			#insert password in username
			userDictionary[username_request] = password_request
			conn.sendall('New username and password created!\n\n')
			break
	#end of password_request do_while loop
	#go to login()
	login(conn)
#end of sign_up()
#-------------------------------------------------------

#-------------------------------------------------------
#main_menu
#Function for handling connections, This will be used to create threads
def clientthread(conn):
	#Sending message to connected client
	conn.sendall('***Welcome to Hangman!***\n') #send only takes string
	
	#infinite loop so that function do not terminate and thread do not end.
	while True:
		conn.sendall('1.Login\n2.Make New User\n3.Hall of Fame\n4.Exit\n\n-Choice: ')
		choice = conn.recv(1024)
		if not choice:
			break
		elif choice[0] == '1':
			#login
			login(conn)
			break
		elif choice[0] == '2':
			#make new user
			sign_up(conn)
			break
		elif choice[0] == '3':
			#hall of fame
			break
		elif choice[0] == '4':
			#Exit
			conn.sendall('See you next time!\n')
			#TODO: sign out from server
			clientArray.remove(conn)
			break
		else:
			conn.sendall('\nERROR: Enter valid choice\n\n')
	#came out of loop
	conn.close()

#now keep talking with the client
while 1:
	#wait to accept a connection - blocking call
	conn, addr = s.accept()
	#display client information
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
	clientArray.append(conn)
	#start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
	start_new_thread(clientthread ,(conn,))

s.close()
