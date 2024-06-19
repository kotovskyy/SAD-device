import socket

def send_wifi_config(ssid, password):
    esp32_ip = '192.168.4.1' 
    esp32_port = 8080 
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


if __name__ == "__main__":
    ssid = "Slava UKRAINE"  
    password = "simpledimple"
    user_id = "1"

    send_wifi_config(ssid, password)
