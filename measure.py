import dht
import machine

DHT_PIN = 14


def measure():
    d = dht.DHT22(machine.Pin(DHT_PIN))
    d.measure()
    return d.temperature(), d.humidity()
