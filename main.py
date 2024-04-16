import network
import urequests  # for fetch requests
from measure import measure
import time

sleep_time = False

# Access point for device configuration
ap = network.WLAN(network.AP_IF)
ap.config(essid="test", authmode=network.AUTH_WPA_WPA2_PSK,
          password="1234567890")
ap.config(max_clients=1)
ap.active(True)


def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)

        while not wlan.isconnected():
            pass

    print("Connected to Wi-Fi")
    print("IP Address:", wlan.ifconfig()[0])


# Wifi Data
wifi_ssid = "Slava UKRAINE"
wifi_password = "simpledimple"

connect_to_wifi(wifi_ssid, wifi_password)

while True:
    if sleep_time:
        temp, hum = measure()
        time.sleep(5)
        print("Temperature:", temp, " Humidity:", hum)

    if not sleep_time:
        temp, hum = measure()
        time.sleep(30)
        print("Temperature:", temp, " Humidity:", hum)
