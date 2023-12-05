import socket
import threading
import os

server = socket.socket(socket.AF_INET , socket.SOCK_DGRAM )
server.bind(('127.0.0.1', 2023))
print("UDP Chat based on code by Shubham Rasal")
print("\nType 'quit' to exit.")

IP,PORT = input("Enter IP and port, sep. by spaces: ").split()

def send():
    while True:
        message = input(">> ")
        if message == "quit":
            os._exit(1)
        sendMessage = f"You: {message}"
        sendMessage.sendto(sendMessage.encode() , (IP,int(PORT)))

def rec():
    while True:
        message = server.recvfrom(1024)
        print("\t\t\t\t >> " +  message[0].decode())
        print(">> ")

x1 = threading.Thread(target = send)
x2 = threading.Thread(target = rec)

x1.start()
x2.start()
