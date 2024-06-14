import socket
import network

# Set up Access Point (AP) with SSID and password
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32_AP', password='password')

print('AP IP address:', ap.ifconfig()[0])

#TCP Server to receive data via AP
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    data = cl.recv(1024)
    data = data.decode('utf-8').strip()
    print('Received data:', data)