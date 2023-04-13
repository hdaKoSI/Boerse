import socket
import os
import time
import csv
import random
import threading

print("Server started")

def read_csv_file(file_path):
    kuerzel = []
    wert = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            kuerzel.append(row['Kuerzel'])
            wert.append(float(row['Wert']))
    return kuerzel, wert

file_path = 'vs_p1_wertpapiere.csv'
kuerzel, wert = read_csv_file(file_path)

print("Loaded {} stocks".format(len(kuerzel)))

LOCAL_IP = ""
LOCAL_PORT = int(os.environ.get("PORT",12345))
BUFFER_SIZE = 1024

# Create a datagram socket
print("Setting up socket with IP: {} and Port: {}".format(LOCAL_IP, LOCAL_PORT))
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((LOCAL_IP, LOCAL_PORT))
print("UDP server up and listening")

# A dictionary to keep track of connected clients and their addresses
connected_clients = {}

def send_all_prices(address):
    for i in range(len(kuerzel)):
        send_message(kuerzel[i] + ";" + str(wert[i]), address)

def send_message(message, address):
    bytesToSend = str.encode(message)
    UDPServerSocket.sendto(bytesToSend, address)

def broadcast_message(message):
    for address in connected_clients.keys():
        send_message(message, address)


# A function that listens for incoming datagrams and sends price changes to connected clients
def listen_for_datagrams():
    # Receive datagram and get the client's address
    bytes_address_pair = UDPServerSocket.recvfrom(BUFFER_SIZE)
    message = bytes_address_pair[0]
    address = bytes_address_pair[1]
    while True:

        # If the client is not already connected, add it to the dictionary of connected clients
        if address not in connected_clients:
            connected_clients[address] = True
            print("New client connected: {}".format(address))

        # Send the current prices to the client
        if message == b'all':
            print("Sending all prices to {}".format(address))
            send_all_prices(address)

    # Close the socket when the thread is finished
    UDPServerSocket.close()

# A function that randomly changes the prices of the stocks
def change_prices():
    while True:
        # Generate a random price change and apply it to a random stock
        wId = random.randint(0, len(kuerzel) - 1)
        priceChange = random.randint(-10, 10)
        if priceChange != 0:
            wert[wId] = float(wert[wId]) + priceChange
            print("New price for {}: {} (change: {})".format(kuerzel[wId], wert[wId], priceChange))
            broadcast_message(kuerzel[wId] + ";" + str(wert[wId]))

        # Wait for a random amount of time before generating the next price change
        waitTime = random.uniform(2.0, 10.0)
        print("Waiting for {} seconds".format(waitTime))
        time.sleep(waitTime)

# Start the thread that listens for incoming datagrams
t1 = threading.Thread(target=listen_for_datagrams)
t1.start()

# Start the thread that changes the prices of the stocks
t2 = threading.Thread(target=change_prices)
t2.start()
