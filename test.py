def parsing(data):
    ssid = data.split('SSID=')[1].split(';')[0]
    password = data.split('PASSWORD=')[1].split(';')[0]
    device_name = data.split('DEVICE_NAME=')[1].split(';')[0]
    token = data.split('TOKEN=')[1]

    return ssid, password, device_name, token


print(parsing("SSID=Gandonishe;PASSWORD=Dasha290605*;DEVICE_NAME=ESPconnected;TOKEN=d8546310f4afa07467b00cf4076ac38b8340f096"))
