import socket
import os
import time
import csv
import random
import threading

def read_csv_file(file_path):
    data = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

file_path = 'vs_p1_wertpapiere.csv'
data = read_csv_file(file_path)

print("Started")

localIP = ""
localPort = int(os.environ.get("PORT",12345))
bufferSize = 1024

msgFromServer = "Hello UDP Client"
bytesToSend = str.encode(msgFromServer)

# Create a datagram socket
print("Setting up socket with IP: {} and Port: {}".format(localIP, localPort))
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

# A dictionary to keep track of connected clients and their addresses
connected_clients = {}

# A function that listens for incoming datagrams and sends price changes to connected clients
def listen_for_datagrams():
    # Receive datagram and get the client's address
    bytes_address_pair = UDPServerSocket.recvfrom(bufferSize)
    message = bytes_address_pair[0]
    address = bytes_address_pair[1]
    while True:

        # If the client is not already connected, add it to the dictionary of connected clients
        if address not in connected_clients:
            connected_clients[address] = True
            print("New client connected: {}".format(address))

        # Send the current prices to the client
        #for row in data:
         #   bytesToSend = str.encode(row['Kuerzel'] + ";" + str(row['Wert']))
          #  UDPServerSocket.sendto(bytesToSend, address)

    # Close the socket when the thread is finished
    UDPServerSocket.close()

# A function that randomly changes the prices of the stocks
def change_prices():
    while True:
        # Generate a random price change and apply it to a random stock
        wId = random.randint(0, len(data) - 1)
        priceChange = random.randint(-10, 10)
        data[wId]['Wert'] = float(data[wId]['Wert']) + priceChange

        # Send the new prices to all connected clients
        for address in connected_clients.keys():
            bytesToSend = str.encode(data[wId]['Kuerzel'] + ";" + str(data[wId]['Wert']))
            UDPServerSocket.sendto(bytesToSend, address)

        # Wait for a random amount of time before generating the next price change
        time.sleep(random.uniform(0.5, 2.0))

# Start the thread that listens for incoming datagrams
t1 = threading.Thread(target=listen_for_datagrams)
t1.start()

# Start the thread that changes the prices of the stocks
t2 = threading.Thread(target=change_prices)
t2.start()
