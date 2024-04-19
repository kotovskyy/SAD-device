import network
import urequests  # for fetch requests
from measure import measure
import time
import config
import ubinascii
import machine

sleep_time = True

# Access point for device configuration
ap = network.WLAN(network.AP_IF)
ap.config(essid="test", authmode=network.AUTH_WPA_WPA2_PSK,
          password="1234567890")
ap.config(max_clients=1)
ap.active(True)


def generate_mac_address():
    unique_id = machine.unique_id()

    custom_prefix = b"ESP-32"
    mac_address = custom_prefix + unique_id[-3:]

    formatted_mac_address = ":".join(
        "{:02x}".format(byte) for byte in mac_address)

    return formatted_mac_address


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


def connect_to_wifi():
    if config.WIFI_SSID and config.WIFI_PASS:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.connect(config.WIFI_SSID, config.WIFI_PASS)
        while not sta.isconnected():
            time.sleep(1)
            print("Connecting to WiFi...")
        print("Connected to WiFi")
        return True
    else:
        print("No wifi credentials provided")
        return False


def request_data(temp, hum):
    data = {"temperature": temp, "humidity": hum}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ESP32 MicroPython"
    }

    dest = config.API_URL + "sensor-data/"

    try:
        response = urequests.post(url=dest, headers=headers, json=data)
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print("Error sending data")

    except OSError as e:
        print("Error sending data")
        print(e)


if connect_to_wifi():
    while True:
        temp, hum = measure()
        request_data(temp, hum)
        time.sleep(5 if sleep_time else 30)
