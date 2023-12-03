import socket
import sys

HOST = '127.0.0.1'  # loopback
PORT = 39337  # 'man' decoded as base64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'connecting to {HOST}:{PORT}..')
s.connect((HOST, PORT))

print('connect success!')

while True:
    message = s.recv(1024).decode('utf-8')
    # If the message is "game over" or "you win", skip to the next message.
    if (message == 'Play again?' and guessToSend != 'y'):
        sys.exit(0)
    elif (message == 'Play again?'):
        message = 'test'

    if message[0] == '-':
        print(message)
        message = s.recv(1024).decode('utf-8')
    print(message)

    print(f"[Enter a letter, or 'exit' to quit]:")
    guessToSend = ''
    while True:
        guessToSend = input()
        # stuff after 'or' redundant?
        if guessToSend == 'exit' or (message == 'Play again?' and guessToSend != 'y'):
            sys.exit(0)
        if guessToSend.isalpha() and len(guessToSend) == 1:
            break
        print('Enter exactly one letter of the alphabet, or \'exit\' to quit the game.')
    s.send(guessToSend.encode('utf-8'))
