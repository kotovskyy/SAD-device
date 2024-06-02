import socket
import network

# Set up Access Point (AP) with SSID and password
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32_AP', password='password')

print('AP IP address:', ap.ifconfig()[0])


# Create a TCP server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(1)

print('Waiting for connection...')

while True:
    # Accept incoming connection
    client_socket, client_addr = server_socket.accept()
    print('Client connected:', client_addr)

    # Receive data from client
    data = client_socket.recv(1024)
    print('Received data:', data)

    # Close the client socket
    client_socket.close()
