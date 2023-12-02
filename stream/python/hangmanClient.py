import socket, sys

HOST = '192.168.0.13'
PORT = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


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