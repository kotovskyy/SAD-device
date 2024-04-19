import dht
import machine
import config


def measure():
    d = dht.DHT22(machine.Pin(config.DHT_22_PIN))
    d.measure()
    return d.temperature(), d.humidity()
