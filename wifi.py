# Wifi manager class
# Add a known_networks.json file in the following format to use connect_known() method:
# [
#   {"ssid":"Home","password":"homepass"},
#   {"ssid":"Lab","password":"labpass"},
#   {"ssid":"Hotspot","password":"12345678"}
# ]

import network, uos as os, time

class wifiManager:

    # Constitutes to a timeout of 12 s
    MAX_TRIES = 3
    RETRY_DELAY = 4

    def __init__(self):
        # Setup as client and enable wifi hardware on pico
        self.__wlan = network.WLAN(network.STA_IF)
        self.__wlan.active(True)


    # Method to connect to a specific wifi
    def connect(self, SSID, PW):



        # Retry logic
        for _ in range(wifiManager.MAX_TRIES):

            # Connect to specified SSID
            self.__wlan.connect(SSID, PW)

            # wait for max of 4 seconds before retry
            for _ in range(wifiManager.RETRY_DELAY):
                if not self.__wlan.isconnected():

                    # Breaking out of loop for low level network issue (e.g. bad ssid or pass)
                    if self.__wlan.status() < 0:
                        break

                    # Displaying message while connecting
                    print("connecting...")
                    time.sleep(1)

                else:
                    break

            # Break out of retry logic if connected
            if self.__wlan.isconnected():
                break  

            # Handling bad ssid/pass situation
            else:

                if self.__wlan.status() < 0:
                    print("unable to connect: bad ssid/pass or other connect error")
                    break

                self.__wlan.disconnect()      

        # Displaying connected message
        self.__wlan.ifconfig(('192.168.68.249', '255.255.255.0', '192.168.68.1', '8.8.8.8')) # hardcoded ipconfig
        print(f"Connected to: {SSID}, config: {self.__wlan.ifconfig()}")

    # Method to connect to known networks (defined by known_networks.json)
    def connect_known(self):
        
        try:
            os.stat("known_networks.json")
        except:
            return "unable to connect: no 'known_networks.json'"

    # Method to send data to an api via POST
    def send_POST(self, send_json, url):
        
        if self.__wlan.isconnected():
            pass

        else:
            return "unable to send: no connection"
        
if __name__ == "__main__":
    wifi = wifiManager()
    # wifi.connect("","") # -- works with actual wifi