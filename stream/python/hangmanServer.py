import socket
import sys
import random

HOST = '0.0.0.0'  # listen on all
PORT = 39337  # 'man' decoded as base64
HUMAN_SERVER = False  # is a human providing the words?
EASY_MODE = True

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

# game parameters
maxMistakes = 7 if not EASY_MODE else 11


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

    if EASY_MODE:
        # give man hands and feet
        full = '''
  ┌─══╗
  O   ║
_/|\_ ║
_/ \_ ║
╦╦╦╦╦╦╢
'''
        strokes = [
            # note that each line of the full graphic is 7 chars followed by a newline
            21,  # right hand
            17,  # left hand
            29,  # right foot
            25,  # left foot
            20,  # right arm
            18,  # left arm
            28,  # right leg
            26,  # left leg
            19,  # torso
            11  # head
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


client, address = None, None

while True:
    if not client:
        print('waiting for connection...')
        client, address = server.accept()

        word = None
        incorrectGuesses = set()
        ask_playagain = False

    if ask_playagain:
        ask_playagain = False
        client.send('Play Again? [y/n]\n'.encode('utf-8'))
        if not client.recv(1024).decode('utf-8').lower().startswith('y'):
            print('Player declined offer to play again')
            client.close()
            client = None
            continue

    if not word:
        print('Starting a new round!')
        word = inputTargetWord()
        coveredWord = cover(word)
        incorrectGuesses = set()

    if coveredWord == word:
        client.send(f'-YOU WON! word was {word}\n'.encode('utf-8'))
        print('Guesser won!')
        word = None
        ask_playagain = True
        continue

    guesses_remaining = maxMistakes - len(incorrectGuesses)
    graphic = getGraphic(guesses_remaining)
    if guesses_remaining <= 0:
        client.send(
            f'-{graphic}\nGAME OVER! word was {word}\n'.encode('utf-8'))
        print('Game over - guesser made too many mistakes!')
        word = None
        ask_playagain = True
        continue

    # construct the guess prompt
    message = f'{graphic}\n{coveredWord}\n'
    if len(incorrectGuesses) > 0:
        formattedGuesses = ''.join(guess for guess in sorted(incorrectGuesses))
        message += f'already guessed: {formattedGuesses}\n'

    # send prompt to client side (word guesser)
    # server side (word chooser) should see it too
    print(message)
    client.send(message.encode('utf-8'))

    # get a guess from the client (word guesser)
    print('Waiting for player guess...')
    guess = client.recv(1024).decode('utf-8')

    if not guess:
        print('connection abort.')
        client.close()
        client = None
        continue

    # truncate guess to a single letter
    guess = guess[0]

    # say "an" if it guess' pronounciation starts with a vowel, else "a"
    guess_an = 'an' if guess in [
        'a', 'e', 'f', 'h', 'i', 'l', 'm', 'n', 'o', 'r', 's', 'x', 'y'] else 'a'
    print(f'Guesser asks: Is there {guess_an} \'{guess}\'?')

    # check the guess against the word
    newCoveredWord = uncover(word, coveredWord, guess)
    if newCoveredWord == coveredWord:
        incorrectGuesses.add(guess.upper())
    coveredWord = newCoveredWord

    print(f'Guesser has {maxMistakes - len(incorrectGuesses)} mistakes left.')
