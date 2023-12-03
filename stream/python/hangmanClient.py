import socket
import sys

HOST = '127.0.0.1'  # loopback
PORT = 39337  # 'man' decoded as base64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'connecting to {HOST}:{PORT}..')
s.connect((HOST, PORT))

print('connect success!')


def inputGuess():
    print(f"[Enter a letter, or 'exit' to quit]:")
    while True:
        guess = input()
        if guess == 'exit':
            return guess
        if guess.isalpha() and len(guess) == 1:
            return guess
        print('Enter exactly one letter of the alphabet, or \'exit\' to quit the game.')


while s:
    message = s.recv(1024).decode('utf-8')
    if message.startswith('-'):
        # some messages expect no response, these start with a hyphen.
        print(message[1:])
        continue
    if message == '':
        print('connection abort.')
        break

    print(message)

    guessToSend = inputGuess()
    if guessToSend == 'exit':
        s.close()
        s = None
        break
    s.send(guessToSend.encode('utf-8'))
