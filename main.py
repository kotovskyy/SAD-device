import network
import socket
import time
import urequests
import machine

import config


def configure_wifi(ssid, password):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, password)
    for _ in range(10): 
        if sta.isconnected():
            break
        time.sleep(1)
    if not sta.isconnected():
        print('Failed to connect to WiFi')
        return False
    print('Connected to', ssid)
    print('Network config:', sta.ifconfig())
    return True

# Function to send measurement data
def send_measurement_data(api_url, data):
    try:
        response = urequests.post(api_url, json=data)
        print('Response from server:', response.text)
        response.close()
    except Exception as e:
        print('Error sending data:', e)


def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32_AP', password='password')
    print('AP IP address:', ap.ifconfig()[0])
    return ap


def listen_for_config(ap):
    port = 8080
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print(f'Listening on {addr}')
    
    while not network.WLAN(network.STA_IF).isconnected():
        cl, addr = s.accept()
        print('Client connected from', addr)
        data = cl.recv(1024).decode('utf-8').strip()
        print('Received data:', data)
        
        try:
            ssid = data.split('SSID=')[1].split(';')[0]
            password = data.split('PASSWORD=')[1]
            print('SSID:', ssid)
            print('Password:', password)
            save_config(ssid, password)
            cl.send('Wi-Fi configured successfully. Restarting...'.encode('utf-8'))
            machine.reset() 
        except Exception as e:
            print('Error parsing configuration:', e)
            cl.send('Failed to configure Wi-Fi'.encode('utf-8'))
        cl.close()

    ap.active(False)
    s.close()


def save_config(ssid, password):
    with open('config.py.template', 'r') as template_file:
        template = template_file.read()
    
    config_content = template.format(WIFI_SSID=ssid, WIFI_PASS=password)
    
    with open('config.py', 'w') as config_file:
        config_file.write(config_content)


sta = network.WLAN(network.STA_IF)
sta.active(True)

if not configure_wifi(config.WIFI_SSID, config.WIFI_PASS):
    ap = start_ap()
    listen_for_config(ap)


while True:
    measurement_data = {
        'temperature': 25.5,  
        'humidity': 60  
    }
    send_measurement_data(config.API_URL, measurement_data)
    time.sleep(5)
