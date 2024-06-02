import ntptime
import time

ntptime.host = "1.europe.pool.ntp.org"


def get_ntp_time():
    ntptime.settime()
    print("Time set from NTP server")
    print(time.localtime())
