import network
import urequests  # for fetch requests
from measure import measure
import time
import webrepl
import config
import ubinascii
import machine
import ubluetooth
import binascii


sleep_time = True
connected = False
bt_connected = False

# Access point for device configuration
ap = network.WLAN(network.AP_IF)
ap.config(essid="test", authmode=network.AUTH_WPA_WPA2_PSK,
          password="1234567890")
ap.config(max_clients=1)
ap.active(True)


def generate_mac_address():
    unique_id = machine.unique_id()
    return ubinascii.hexlify(unique_id).decode("utf-8")


# Mac address generation and storage
try:
    if not config.DEVICE_ID:
        mac_address = generate_mac_address()
        config.DEVICE_ID = mac_address
        with open("config.py", "a") as config_file:
            config_file.write(f"DEVICE_ID = \"{mac_address}\"")
        print("Generated and stored MAC Address:", mac_address)
    else:
        mac_address = config.DEVICE_ID
        print("Stored MAC Address:", mac_address)
except AttributeError:
    mac_address = generate_mac_address()
    config.DEVICE_ID = mac_address
    with open("config.py", "a") as config_file:
        config_file.write(f"DEVICE_ID = \"{mac_address}\"")
    print("Generated and stored MAC Address:", mac_address)

# Connect to wifi


def connect_to_wifi():
    if config.WIFI_SSID and config.WIFI_PASS:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.connect(config.WIFI_SSID, config.WIFI_PASS)
        while not sta.isconnected():
            time.sleep(1)
            print("Connecting to WiFi...")
        print("Connected to WiFi")
        global connected
        connected = True
        return True
    else:
        print("No wifi credentials provided")
        return False

# API request


def request_data(temp, hum):
    data = {
        "device": 1,
        "temperature": temp,
        "humidity": hum,
        "light_intensity": 0
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ESP32 MicroPython"
    }

    dest = config.API_URL + "measurements/"

    try:
        response = urequests.post(url=dest, headers=headers, json=data)
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print("Error sending data")

    except OSError as e:
        print("Error sending data")
        print(e)

# Function to get WebREPL IP and port


def get_webrepl_info():
    sta_if = network.WLAN(network.STA_IF)
    ifconfig = sta_if.ifconfig()
    ip = ifconfig[0]
    port = 8266
    return ip, port

# Activate Bluetooth and make device visible


def bt_irq(event, data):
    global bt_connected
    if event == 1:
        print("Central connected")
        bt_connected = True
    elif event == 2:
        print("Central disconnected")
        bt_connected = False


def activate_bluetooth():
    bt = ubluetooth.BLE()
    bt.active(True)

    print("Bluetooth activated")

    device_name = "ESP32"

    uuid_bytes = binascii.unhexlify(config.UUID.replace("-", ""))

    adv_data = bytearray([
        0x02, 0x01, 0x06,
        len(device_name) + 1, 0x09
    ]) + bytearray(device_name, "utf-8")

    adv_data += bytearray([len(uuid_bytes) + 1, 0x07]) + uuid_bytes

    bt.gap_advertise(100, adv_data, connectable=True)
    print(f"Bluetooth advertising with name: {device_name}")

    bt.irq(bt_irq)


while True:
    if connected:
        webrepl.start()
        ip, port = get_webrepl_info()
        print(f"WebREPL running at ws://{ip}:{port}")
        while True:
            temp, hum = measure()
            request_data(temp, hum)
            time.sleep(5 if sleep_time else 30)
    else:
        if bt_connected:
            pass
        else:
            activate_bluetooth()
            while not bt_connected:
                print("Waiting for Bluetooth connection...")
                time.sleep(2)
