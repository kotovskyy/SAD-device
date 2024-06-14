import socket

def send_wifi_config(ssid, password):
    """
    Connects to the ESP32 AP and sends Wi-Fi configuration data.

    Args:
    ssid (str): The SSID of the target Wi-Fi network.
    password (str): The password of the target Wi-Fi network.
    """
    esp32_ip = '192.168.4.1'  # Default IP address of the ESP32 when acting as an AP
    esp32_port = 8080  # Port on which the ESP32 is listening
    data = f'SSID={ssid};PASSWORD={password}'
    
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connecting to {esp32_ip}:{esp32_port}...")
        
        # Connect to the ESP32
        s.connect((esp32_ip, esp32_port))
        print("Connected to ESP32")

        # Send the data
        print(f"Sending data: {data}")
        s.send(data.encode('utf-8'))

        # Receive response
        response = s.recv(1024)
        print('Received:', response.decode('utf-8'))

        # Close the connection
        s.close()
        print("Connection closed")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    ssid = "YourSSID"  # Replace with the SSID of your Wi-Fi network
    password = "YourPassword"  # Replace with the password of your Wi-Fi network

    send_wifi_config(ssid, password)
