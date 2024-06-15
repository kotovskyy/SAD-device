import network
import socket
import time
import urequests
import machine
import ujson
import uasyncio as asyncio
import measure

# Function to load config from JSON file
def load_config():
    with open('configuration.json', 'r') as f:
        return ujson.load(f)

# Function to save config to JSON file
def save_config(config):
    with open('configuration.json', 'w') as f:
        ujson.dump(config, f)

# Function to configure Wi-Fi
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

# Function to get MAC address
def get_mac_address():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = wlan.config('mac')
    mac_address = ':'.join(['{:02x}'.format(b) for b in mac])
    return mac_address

# Function to send measurement data
async def send_measurement_data(api_url, data, headers):
    try:
        response = urequests.post(api_url, json=data, headers=headers)
        print('Response from server:', response.text)
        response.close()
    except Exception as e:
        print('Error sending data:', e)

# Function to start Access Point
def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32_AP', password='password')
    print('AP IP address:', ap.ifconfig()[0])
    return ap

# Function to fetch settings
async def fetch_settings(api_url, headers):
    data = {
        "device": load_config()['DEVICE_ID']
    }
    query_params = urllib.parse.urlencode(data)
    full_url = f"{api_url}?{query_params}"
    
    try:
        response = urequests.get(full_url, headers=headers)
        print('Response from server:', response.text)
        response.close()
    except Exception as e:
        print("Error sending request: ", e)

# Function to listen for incoming connections and configure Wi-Fi
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
            password = data.split('PASSWORD=')[1].split(';')[0]
            device_id = data.split('DEVICE_ID=')[1].split(';')[0]
            token = data.split('TOKEN=')[1]
            print('SSID:', ssid)
            print('Password:', password)
            print('Device id:', device_id)
            print('Token:', token)
            
            mac_address = get_mac_address()
            config = load_config()
            config['WIFI_SSID'] = ssid
            config['WIFI_PASS'] = password
            config['DEVICE_ID'] = device_id
            config['TOKEN'] = token
            config['MAC_ADDRESS'] = mac_address
            save_config(config)
            
            response = f'{mac_address}'
            cl.send(response.encode('utf-8'))
            machine.reset() 
        except Exception as e:
            print('Error parsing configuration:', e)
            cl.send('Failed to configure Wi-Fi'.encode('utf-8'))
        cl.close()

    ap.active(False)
    s.close()

async def send_measurements_loop(api_url, headers):
    while True:
        temperature, humidity = measure.measure()
        request_temperature = {
            "device": load_config()['DEVICE_ID'],
            "value": temperature,
            "type": 1
        }
        request_humidity = {
            "device": load_config()['DEVICE_ID'],
            "value": humidity,
            "type": 1
        }
        
        await send_measurement_data(api_url + "/measurements/", request_temperature, headers)
        await send_measurement_data(api_url + "/measurements/", request_humidity, headers)
        
        await asyncio.sleep(5)  # Wait for 5 seconds before sending the next measurements

async def fetch_settings_loop(api_url, headers):
    while True:
        await fetch_settings(api_url + "/settings/", headers)
        await asyncio.sleep(10) 

async def main():
    config = load_config()
    headers = {
        "Authorization": "Token " + config['TOKEN']
    }
    
    if not configure_wifi(config['WIFI_SSID'], config['WIFI_PASS']):
        ap = start_ap()
        listen_for_config(ap)
    
    # Run both loops concurrently
    await asyncio.gather(
        send_measurements_loop(config['API_URL'], headers),
        fetch_settings_loop(config['API_URL'], headers)
    )

# Run the main function
asyncio.run(main())
