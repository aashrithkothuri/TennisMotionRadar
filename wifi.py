# Wifi manager class
# Add a known_networks.json file in the following format to use connect_known() method:
# [
#   {"ssid":"Home","password":"homepass"},
#   {"ssid":"Lab","password":"labpass"},
#   {"ssid":"Hotspot","password":"12345678"}
# ]

import network, uos as os

class wifiManager:

    # Method to connect to a specific wifi
    def connect(self, SSID, PW):
        pass

    # Method to connect to known networks (defined by known_networks.json)
    def connect_known(self):
        
        try:
            os.stat("known_networks")
        except:
            return "unable to connect: no 'known_networks.json'"

    # Method to send data to an api via POST
    def send_POST(self, send_json, url):
        
        if self.__is_connected():
            pass

        else:
            return "unable to send: no connection"

    # Method to check if pico is connected to wifi
    def __is_connected(self):
        return False