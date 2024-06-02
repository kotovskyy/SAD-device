
import network
import socket

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-AP', password='12345678')

print('Access Point IP:', ap.ifconfig()[0])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 8080))
sock.listen(1)

print('Listening on', ap.ifconfig()[0])
