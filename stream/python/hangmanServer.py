import socket, sys

# Hardcoded - should grab own IP programmatically
HOST = '192.168.0.13'
PORT = int(sys.argv[1])

# create INET, SOCK_STREAM socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind
server.bind((HOST, PORT))

# listen
server.listen(5)

# game variables
incorrectGuesses = 0
maxGuesses = 6

# ASCII art
# Decided to use 'O' instead of '☺ ' - it seems to be two chars wide, awkward
stages = [
    '''   
 ┌─═══╗
      ║
      ║
      ║
╦╦╦╦╦╦╢
''',
    '''   
 ┌─═══╗
 O    ║
      ║
      ║
╦╦╦╦╦╦╢
''',
    '''   
 ┌─═══╗
 O    ║
 |    ║
      ║
╦╦╦╦╦╦╢
''',
    '''   
 ┌─═══╗
 O    ║
 |    ║
/     ║
╦╦╦╦╦╦╢
''',
    '''   
 ┌─═══╗
 O    ║
 |    ║
/ \   ║
╦╦╦╦╦╦╢
''',
    '''   
 ┌─═══╗
 O    ║
/|    ║
/ \   ║
╦╦╦╦╦╦╢
''',
    '''   
 ┌─═══╗
 O    ║
/|\   ║
/ \   ║
╦╦╦╦╦╦╢
'''
]

def uncover(word, coveredWord, letter):
    '''Takes in a word, a string of that word which has some letters
    covered by asterisks, and a letter to uncover. Replaces asterisks
    with the letter that should be there in the word.'''
    
    if len(word) != len(coveredWord):
        print('uncover(): strings word and coveredWord should be of the same length.')
        return
    
    newWord = ''
    
    # For each letter in the word,
    for i in range(len(word)):
        # If it is the letter to uncover, add the letter
        if word[i] == letter:
            newWord += letter
        # Otherwise, add whatever was there, be it an irrelevant letter or an asterisk.
        else:
            newWord += coveredWord[i]
    
    return newWord

# Outer game loop, continues over different matches of Hangman.
while True:
    # accept connection
    client, address = server.accept()

    # Inner game loop starts a match.
    while True:
        print('Select the word for the other player to guess:')
        incorrectGuesses = 0
        word = str(input())
        coveredWord = '.' * len(word)
        
        # Guessing loop
        while True:
            # Check if player won
            if coveredWord == word:
                client.send('-YOU WON!\n'.encode('utf-8'))
                print('Guesser won!')
                word = 'testwordshouldneverbeseen'
                incorrectGuesses = 0
                break
            
            # Check if player lost
            if maxGuesses == incorrectGuesses:
                client.send('-GAME OVER!\n'.encode('utf-8'))
                print('Game over - guesser ran out of guesses!')
                word = 'testwordshouldneverbeseen'
                incorrectGuesses = 0
                break

            # construct the message
            # hangman graphic + coveredWord
            message = stages[incorrectGuesses] + '\n' + coveredWord
            # server side (word chooser) should see it too
            print(message)

            # send to client side (word guesser)
            client.send(message.encode('utf-8'))

            # get a guess from the client (word guesser)
            guess = client.recv(1024).decode('utf-8')
            
            print(f'Player asks: Is there a {guess}?')
            
            # check the guess against the word, making sure it's a single char
            if guess[0] in word:
                coveredWord = uncover(word, coveredWord, guess)
            else:
                incorrectGuesses += 1
            
            
            
            print(f'The player has {maxGuesses - incorrectGuesses} guesses left.')
        
        client.send('Play again? [y/n]'.encode('utf-8'))
        
        playAgain = client.recv(1024).decode('utf-8')
        
        if playAgain != 'y':
            sys.exit(0)         
