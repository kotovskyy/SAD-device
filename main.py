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
    
    print(ssid, password)
    
    sta.connect(ssid, password)
    for _ in range(30): 
        if sta.isconnected():
            break
        time.sleep(0.5)
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
    ap.config(essid='ESP32', password='password', authmode=network.AUTH_WPA2_PSK)
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
    print('AP IP address:', ap.ifconfig()[0])
    return ap

# Function to fetch settings
async def fetch_settings(api_url, headers, device_id):
    data = {
        "device": device_id
    }
    query_params = '&'.join([f"{k}={v}" for k, v in data.items()])
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
            device_name = data.split('DEVICE_NAME=')[1].split(';')[0]
            token = data.split('TOKEN=')[1]
            print('SSID:', ssid)
            print('Password:', password)
            print('Device name:', device_name)
            print('Token:', token)
            
            mac_address = get_mac_address()
            config = load_config()
            config['WIFI_SSID'] = ssid
            config['WIFI_PASS'] = password
            config['DEVICE_NAME'] = device_name
            config['TOKEN'] = token
            config['MAC_ADDRESS'] = mac_address
            save_config(config)
            
            machine.reset() 
        except Exception as e:
            print('Error parsing configuration:', e)
            cl.send('Failed to configure Wi-Fi'.encode('utf-8'))
        cl.close()

    ap.active(False)
    s.close()

async def create_device(api_url, data, headers):
    try:
        response = urequests.post(api_url, json=data, headers=headers)
        response_data = response.json()
        print('Response from server:', response.text)
        
        config = load_config()
        config['DEVICE_ID'] = response_data['id']
        config['CREATED'] = 1
        
        save_config(config)
        
        response.close()
    except Exception as e:
        print('Error sending data:', e)

async def send_measurements_loop(api_url, headers, device_id):
    while True:
        temperature, humidity = measure.measure()
        request_temperature = {
            "device": device_id,
            "value": temperature,
            "type": 1
        }
        request_humidity = {
            "device": device_id,
            "value": humidity,
            "type": 1
        }
        print(device_id)
        await send_measurement_data(api_url + "/measurements/", request_temperature, headers)
        await send_measurement_data(api_url + "/measurements/", request_humidity, headers)
        
        await asyncio.sleep(5) #Send data every 1 minute in the future

async def fetch_settings_loop(api_url, headers, device_id):
    while True:
        await fetch_settings(api_url + "/settings/", headers, device_id)
        await asyncio.sleep(10) #Fetch every 5 minutes in production

async def main():
    config = load_config()
    headers = {
        "Authorization": "Token " + config['TOKEN']
    }
    
    print(config)
    
    if not configure_wifi(config['WIFI_SSID'], config['WIFI_PASS']):
        ap = start_ap()
        listen_for_config(ap)
    
    config = load_config()  # Reload the config after potential reset

    if config['CREATED'] == 0:
        await create_device(config['API_URL'] + "/devices/", {
            "name": config['DEVICE_NAME'],
            "mac_address": config['MAC_ADDRESS'],
            "type": 1
        }, headers)
        config = load_config()  # Reload the config after device creation
        config['CREATED'] = 1
        save_config(config)
    else:
        pass  # Patch device if necessary

    config = load_config()
    device_id = config['DEVICE_ID']
    
    print(config)
    
    await asyncio.gather(
        send_measurements_loop(config['API_URL'], headers, device_id),
        fetch_settings_loop(config['API_URL'], headers, device_id)
    )

# Run the main function
asyncio.run(main())
