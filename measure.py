import dht
import machine
import ujson

# Function to load config from JSON file
def load_config():
    with open('configuration.json', 'r') as f:
        return ujson.load(f)

# Load configuration
config = load_config()

def measure():
    d = dht.DHT22(machine.Pin(config['DHT_22_PIN']))
    d.measure()
    return d.temperature(), d.humidity()
