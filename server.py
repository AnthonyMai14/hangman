import socket
import sys
import random
from thread import *

HOST = ''	# Symobolic name meaning all avaiable interfaces
PORT = 1111	# Arbitrary non-privileged port

clientList = []
userDictionary = {} #username: password

hofList = ['']*10 #list of players

wordbankList = ['ucr','anthony', 'yeet', 'sd'] #default values
activeGameList = []

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
class Player:
	def __init__(self, conn, username):
		self.conn = conn
		self.username = username
		self.points = 0 #default points is zero for each new game/join game
	
#end of class Player 
#------------------------------------------------------


#------------------------------------------------------
class Game:
		
	def __init__(self, newPlayer, gId):
		self.gId = gId
		self.difficulty = 1 #default difficulty to Easy (1)
		self.word = ''
		self.playersInGameList = []
		self.playersInGameList.append(newPlayer)

		self.correctGuess = '' 
		self.incorrectGuess = ''
		self.guessesLeft = 0
		self.playerTurn = 0
	
	def randomWord(self):
			#potential inifinite loop if len(activeGameList) == len(wordBankList)
			while True:
				rand_index = random.randint(0, len(wordbankList))
				potential_word = wordbankList[rand_index-1]
				for game_index in range(len(activeGameList)):
					if activeGameList[game_index].word != potential_word:
						self.word = potential_word
						break
					#end if activeGameList[game_index].word != potential_word:
 				#end for game_index in range(len(activeGameList)):
				if self.word != '':
					break
			#end while True
	
	def start_menu(self, conn):
		while True:
			conn.sendall('\nChoose the difficulty:\n1.Easy\n2.Medium\n3.Hard\n\n-Choice: ')
			game_start_choice = conn.recv(1024)
			if not game_start_choice:
				conn.sendall('***ERROR: NULL input!\n')
				break
			elif game_start_choice[0] == '1':
				if len(activeGameList) != len(wordbankList):
					self.difficulty = 1
				break
			elif game_start_choice[0] == '2':
				if len(activeGameList) != len(wordbankList):
					self.difficulty = 2
				break
			elif game_start_choice[0] == '3':
				if len(activeGameList) != len(wordbankList):
					self.difficulty = 3
				break
			else:
				conn.sendall('Invalid choice. Please try again')
		#end game_start_choice do_while loop
	#end game_start()

	def setDifficulty(self):
		if self.difficulty == 2:
			self.guessesLeft = len(self.word) * 2
		elif self.difficulty == 3:
			self.guessesLeft = len(self.word)
		else:
			#cannot detect bug because 'difficulty == 1' is not check. Assume that 'difficulty == 1' is true
			self.guessesLeft = len(self.word) * 3
	#end setDifficulty
	
	def existInCorrectGuess(self, guess):
		for letter in range(len(self.correctGuess)):
			if self.correctGuess[letter] == guess:
				return True
			#end if
		#end for
		return False
	#end def

	def findletter(self, guess):
		found = 0
		for letter in range(len(self.word)):
			if self.word[letter] == guess:
				correctGuessList = list(self.correctGuess)
				correctGuessList[letter] = guess
				self.correctGuess = ''.join(correctGuessList)
				found = found + 1
			#end if
		#end for
		return found
	
	#print correct guess/incorrect guesses/ on menu
	def print_hangman(self):
		#iterate through the players that are in the current game
		for player in range(len(self.playersInGameList)):
			conn = self.playersInGameList[player].conn
                        conn.sendall(self.correctGuess + '\n' + 'Incorrect letters: ' + self.incorrectGuess + '\nGuesses Left: ' + str(self.guessesLeft) + '\n')		
			#print players // print which players turn
			for name in range(len(self.playersInGameList)):
				conn.sendall(self.playersInGameList[name].username + ' ' + str(self.playersInGameList[name].points))
				if name == self.playerTurn:
					#name of player's turn, insert '*' at the end
					conn.sendall('*')
				#end if name == playerTurn
				conn.sendall('\n')
			#end for name in len(playerInGameList)
		#end for player in playersInGameList

	def begin(self):
		wordIsGuessed = False
		while self.guessesLeft != 0 and self.correctGuess != self.word: 
			self.print_hangman()
			#wait response from player's who turn it is
			current_player = self.playersInGameList[self.playerTurn]
			conn = current_player.conn
			conn.sendall('Guess a letter or the whole word: ')
			guess = conn.recv(1024)
			guess = guess.rstrip()
			if len(guess) == 1:
				#find if guess is in word // duplicate guess
				if self.existInCorrectGuess(guess) == False and self.findletter(guess) != 0:
					valid_letter = self.findletter(guess)
					if valid_letter != 0:
						#if correct, add point. if duplicate move on. if wrong guess add word to wrong guess and decrement guesesLeft
						self.playersInGameList[self.playerTurn].points = current_player.points + valid_letter
						if self.correctGuess == self.word:
							wordIsGuessed = True  
				else:
					self.incorrectGuess = self.incorrectGuess + guess
					self.guessesLeft = self.guessesLeft - 1
					#change players
					if self.playerTurn + 1 == len(self.playersInGameList):
						self.playerTurn = 0
					else:
						self.playerTurn = self.playerTurn + 1
			else:
				#if guess is correct, add point worth to the length of word in addition to the points already have
				if guess == self.word:
					self.playersInGameList[self.playerTurn].points = current_player.points + len(self.word)
					self.correctGuess = guess
					wordIsGuessed = True
				else:
					#if incorrect, get kicked out of game
					conn.sendall('Incorrect word guess. Thanks for playing!\n')
					del self.playersInGameList[self.playerTurn]
					break #TODO: potenail bug with multiple players
			#if the word is guessed, print_hangman(), see if player can be add to HOF, End Game
			if wordIsGuessed:
				self.print_hangman()
				#Check to see if can be added to HOF
				for index in range(len(hofList)):
					if hofList[index] == '':
						hofList[index] = self.playersInGameList[self.playerTurn]
						break
					elif self.playersInGameList[self.playerTurn].points == hofList[index].points:
						break
					elif self.playersInGameList[self.playerTurn].points > hofList[index].points:
								#need to consider case if inserting into index == 10
								for backward in xrange(len(hofList) - 1 ,index, -1):
									hofList[backward] = hofList[backward - 1]
								#end for-loop
								hofList[index] = self.playersInGameList[self.playerTurn]
								break
				#restart points
			#end if guess == self.word
			
		#end while self.guessesLeft != 0 and self.correctGuess != self.word
		
		#End Game & take out of activeGameList
	#end begin()
	def start(self, conn):
		self.start_menu(conn)
		self.randomWord()
		self.setDifficulty()
		#generate '_' for users	
		for letter in range(len(self.word)):
			self.correctGuess = self.correctGuess + '_'
		#end for letter in len(word)
		self.begin()
		activeGameList.pop(self.gId)
	#end game_start()
#end of class Game
#------------------------------------------------------


#------------------------------------------------------
#hall of fame function: print out the top 10 scorers. If not present, will print out empty list
def hall_of_fame(conn):
	conn.sendall('-Hall Of Fame-\n')
	val = 1
	for item in hofList:
		conn.sendall(str(val) + '. ')
		if item != '':			 
			conn.sendall(item.username + ': ' + str(item.points) + '\n')
		else:
			conn.sendall(': \n')
		val = val + 1
	conn.sendall('\n')
	#end for val in hofList			
#end hall_of_fame()	
#------------------------------------------------------

#game_menu function: user will be able to choose if they want to be part of a new game or jump onto one going on
def game_menu(conn, username_entry):
	conn.sendall('-Game Menu-\n\n')
	while True:
		conn.sendall('1.Start New Game\n2.Get list of the Games\n3.Hall of Fame\n4.Exit\n\n-Choice: ')
		game_choice = conn.recv(1024)
		if not game_choice:
			conn.sendall('***ERROR: NULL input!\n')
			break
		elif game_choice[0] == '1':
			#Start New game. Return flag: determin if break or not
			activeGameList_length = len(activeGameList)
			if activeGameList_length != len(wordbankList) or activeGameList_length == 0:
				player = Player(conn, username_entry) #set new instance of player 
				newGame = Game(player, activeGameList_length)
				activeGameList.append(newGame)
				newGame.start(conn)
		elif game_choice[0] == '2':
			#Get list of current games. Return flag: determin if break or not
			while True:
				conn.sendall('-List of Games-\n')
				if len(activeGameList) ==  0:
					conn.sendall('No Active Games!!\n')
				else:
					for i in range(len(activeGameList)):
						conn.sendall(str(i + 1) + '. Game ' + str(activeGameList[i].gId) + '\n')
				conn.sendall('Please choose a game to join (or \'!q\' to exit): ')
				choice_join = conn.recv(1024)
				choice_join = choice_join.rstrip()
				if (choice_join == '!q'):
					break
				elif (int(choice_join) <= (len(activeGameList)) and choice_join != '0'):
					player = Player(conn, username_entry) #set new instance of player 
					activeGameList[int(choice_join) - 1].playersInGameList.append(player)
					activeGameList[int(choice_join) - 1].begin()
					break
				else:
					conn.sendall('\n\n***ERROR: Invalid choice! Please try again.\n')
		elif game_choice[0] == '3':
			#hall of fame
			hall_of_fame(conn)
		elif game_choice[0] == '4':
			#Exit
			conn.sendall('See you next time!\n')
			clientList.remove(conn)
			break
		else:
			conn.sendall('\n***ERROR: Enter valid choice\n\n')
	#came out of loop

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


#------------------------------------------------------
#login function:
def login(conn):
	conn.sendall('-Login-\n\n')
	username_entry = ""
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
		if userExist(username_entry) and userDictionary[username_entry] == password_entry:
			conn.sendall('\nWelcome, ' + username_entry + '\n\n')
			break
		else:
			conn.sendall('\nInvalid username or password. Please try again\n\n')
	#end of login do_while loop
	game_menu(conn, username_entry)
#end of login()
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
			conn.sendall('\n******ERROR: Your username is invalid. Please type again or try another one.\n')
		elif username_request == '!q':
			#go back to main_menu
			clientthread(conn)
		else:
			#TODO: check for special characters (i.e.' ','/','.',etc.). If in username, invalid
			if userExist(username_request):
				conn.sendall('\n***ERROR: Your username already exist. Please try another username.\n')
			else:
				break
	#end of username_request do_while loop
	while True:
		#**password cannot end with a ' '
		conn.sendall('Type in a new password (\'!q\' to go back to main menu): ')
		password_request = conn.recv(1024)
		password_request = password_request.rstrip()
		if not password_request:
			conn.sendall('\n***ERROR: Your password is invalid, Please type again or try another one.\n')
		elif password_request == '!q':
			#go back to main_menu
			clientthread(conn)
		else:
			#insert password in username
			userDictionary[username_request] = password_request
			#insert user into score dictionary list and set to default score of '0'
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
			hall_of_fame(conn)
		elif choice[0] == '4':
			#Exit
			conn.sendall('See you next time!\n')
			#TODO: sign out from server
			clientList.remove(conn)
			break
		else:
			conn.sendall('\n***ERROR: Enter valid choice\n\n')
	#came out of loop
	conn.close()

def word_true_valid(word_to_add):
	#check if have special character
	if word_to_add.isalpha() == False:
		print ('\n***ERROR: Invalid Character. Alphabetic characters only!\n\n')
		return False
	#check if already exist in wordbankList
	for word in wordbankList:
		if  word == word_to_add:
			print ('\n***ERROR: \''+ word_to_add +'\' already exist in word bank! Please try another word.\n')
			return False
		#end if
	#end for-loop
	return True

def serverthread(s_conn):
	while True:
		server_choice = raw_input('-HANGMAN SERVER MENU-\n1.Current List of Users\n2.Current List of Words\n3.Add New Word to List of Words\n\n-Choice: ')
		if server_choice == '1':
			print '-List of Users-\n'
			if len(userDictionary) == 0:
				print ('No users!\n')
			for user in userDictionary:
				print (user + '\n')
			#end for-loop
		elif server_choice == '2':
			print '-List of Words-\n'
			if len(wordbankList) == 0:
				print ('Empty word bank!\n')
			for word in wordbankList:
				print word
			print '\n'
			#end for-loop
		elif server_choice == '3':
			word_to_add = ""
			while True:
				word_to_add = raw_input('Word to add (\'!q\' to return to main menu): ')
				if word_to_add == '!q':
					break
				if word_true_valid(word_to_add):
					wordbankList.append(word_to_add)
					print ('\n\n\'' + word_to_add + '\' added to word bank..\n')
					break
			#end while-loop
#now keep talking with the client

start_new_thread(serverthread, (0,))
while 1:
	#wait to ac default valuecept a connection - blocking call
	conn, addr = s.accept()
	#display client information
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
	clientList.append(conn)
	#start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
	start_new_thread(clientthread ,(conn,))

s.close()
