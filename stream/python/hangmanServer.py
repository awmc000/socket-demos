import socket
import sys
import random

HOST = '0.0.0.0'  # listen on all
PORT = 39337  # 'man' decoded as base64
HUMAN_SERVER = False  # is a human providing the words?

# a wordlist for nonhuman servers to use
wordlist = ['alphabet', 'bravado', 'crunchy', 'delight', 'epistle', 'fearful', 'ghastly', 'heroine', 'incident', 'jugular', 'kentucky', 'lawless', 'mophead',
            'neighbor', 'ointment', 'procure', 'quotient', 'rulebook', 'suppose', 'tyrannic', 'ucluelet', 'voyageur', 'wrought', 'xylitol', 'youthful', 'zoology']

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
maxGuesses = 7


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


def cover(word):
    '''Takes in a word, replaces all latin letters with periods.
    Leaves spaces, hyphens, underscores, etc.. untouched'''
    return ''.join(('.' if c.isalpha() else c) for c in word)


def uncover(word, coveredWord, letter):
    '''Takes in a word, a string of that word which has some letters
    covered by periods, and a letter to uncover. Replaces periods
    with the letter that should be there in the word.'''

    if len(word) != len(coveredWord):
        print('uncover(): strings word and coveredWord should be of the same length.')
        return

    letter = letter.lower()
    return ''.join((plain if plain.lower() == letter else covered) for plain, covered in zip(word, coveredWord))


def inputTargetWord():
    if HUMAN_SERVER:
        print('Select the word for the other player to guess:')
        return str(input())
    else:
        return random.choice(wordlist)


# Outer game loop, continues over different matches of Hangman.
while True:
    # accept connection
    print('waiting for connection...')
    client, address = server.accept()

    # Inner game loop starts a match.
    while client:
        incorrectGuesses = 0
        word = inputTargetWord()
        coveredWord = cover(word)

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
                client.send(f'-GAME OVER! word was {word}\n'.encode('utf-8'))
                print('Game over - guesser ran out of guesses!')
                word = None
                incorrectGuesses = 0
                break

            # construct the message
            # hangman graphic + coveredWord
            message = getGraphic(
                maxGuesses - incorrectGuesses) + '\n' + coveredWord + '\n'
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

            # make sure it's a single char
            guess = guess[0]

            print(f'Player asks: Is there a {guess}?')

            # check the guess against the word
            newCoveredWord = uncover(word, coveredWord, guess)
            if newCoveredWord == coveredWord:
                incorrectGuesses += 1
            coveredWord = newCoveredWord

            print(f'Player has {maxGuesses - incorrectGuesses} guesses left.')

        if not client:
            break

        print('Offering to play again...')
        client.send('Play again? [y/n]'.encode('utf-8'))

        playAgain = client.recv(1024).decode('utf-8')

        if playAgain != 'y':
            print('Player declined offer to play again')
            client.close()
            client = None
