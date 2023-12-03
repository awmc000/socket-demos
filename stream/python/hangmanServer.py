import socket
import sys

HOST = '0.0.0.0'  # listen on all
PORT = 39337  # 'man' decoded as base64

# create INET, SOCK_STREAM socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind
print(f'attempting to bind to {HOST}:{PORT}')
server.bind((HOST, PORT))

# listen
print(f'bind success; now listening')
server.listen(5)

# game variables
incorrectGuesses = 0
maxGuesses = 6


def getGraphic(guesses_remaining):
    # ASCII art
    # Decided to use 'O' instead of '☺ ' - it seems to be two chars wide, awkward
    full = '''
 ┌─═══╗
 O    ║
/|\   ║
/ \   ║
╦╦╦╦╦╦╢
'''

    # strokes[0] is the last stroke of the man to draw
    strokes = [
        # note that each line of the full graphic is 7 chars followed by a newline
        19,  # right arm
        17,  # left arm
        27,  # right leg
        25,  # left leg
        18,  # torso
        10  # head
    ]

    # erase the strokes that haven't been drawn yet
    partial = full
    for stroke in strokes[:guesses_remaining]:
        partial = partial[:stroke] + ' ' + partial[stroke + 1:]

    return partial


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
    print('waiting for connection...')
    client, address = server.accept()

    # Inner game loop starts a match.
    while client:
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
                word = None
                incorrectGuesses = 0
                break

            # Check if player lost
            if maxGuesses == incorrectGuesses:
                client.send('-GAME OVER!\n'.encode('utf-8'))
                print('Game over - guesser ran out of guesses!')
                word = None
                incorrectGuesses = 0
                break

            guessesLeft = maxGuesses - incorrectGuesses

            # construct the message
            # hangman graphic + coveredWord
            message = getGraphic(guessesLeft) + '\n' + coveredWord + '\n'
            # server side (word chooser) should see it too
            print(message)

            # send to client side (word guesser)
            client.send(message.encode('utf-8'))

            # get a guess from the client (word guesser)
            print('Waiting for player guess...')
            guess = client.recv(1024).decode('utf-8')

            if not guess:
                print('connection abort.')
                client.close()
                client = None
                break

            print(f'Player asks: Is there a {guess}?')

            # check the guess against the word, making sure it's a single char
            guess = guess[0]
            if guess in word:
                coveredWord = uncover(word, coveredWord, guess)
            else:
                incorrectGuesses += 1

            print(f'Player has {guessesLeft} guesses left.')

        if not client:
            break

        print('Offering to play again...')
        client.send('Play again? [y/n]'.encode('utf-8'))

        playAgain = client.recv(1024).decode('utf-8')

        if playAgain != 'y':
            print('Player declined offer to play again')
            client.close()
            client = None
