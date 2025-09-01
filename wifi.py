# Wifi manager class
# Add a known_networks.json file in the following format to use connect_known() method:
# [
#   {"SSID":"Home","PASS":"homepass","IPCONFIG":(ip,subnetmask,gateway,DNS server)},
#   {"SSID":"Lab","PASS":"labpass"},
#   {"SSID":"Hotspot","PASS":"12345678"}
# ]

import network, uos as os, time, ujson as json

class wifiManager:

    # Constitutes to a timeout of 12 s
    MAX_TRIES = 3
    RETRY_DELAY = 4

    def __init__(self):
        # Setup as client and enable wifi hardware on pico
        self.__wlan = network.WLAN(network.STA_IF)
        self.__wlan.active(True)


    # Method to connect to a specific wifi
    def connect(self, SSID, PW, IPCONFIG):



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
                    return False

                self.__wlan.disconnect()      

        # Displaying connected message
        self.__wlan.ifconfig(IPCONFIG) # hardcoded ipconfig
        print(f"Connected to: {SSID}, config: {self.__wlan.ifconfig()}")
        return True

    # Method to connect to known networks (defined by known_networks.json)
    def connect_known(self):
        
        try:

            # Raises an error if known_networks.json doesn't exist
            os.stat("known_networks.json")

            # Opening json file
            with open("known_networks.json", "r") as f:

                # Parsing json to list (list of dict)
                networks = json.load(f)
                print(networks)

                # trying to connect to each known network (in the order they are listed in)
                for network in networks:
                    SSID = network["SSID"]
                    PASS = network["PASS"]
                    IPCONFIG = eval(network["IPCONFIG"]) # Turns it into python tuple
                    self.connect(SSID=SSID, PW=PASS, IPCONFIG=IPCONFIG)

        except Exception as e:
            print(e)
            return False

    # Method to send data to an api via POST
    def send_POST(self, send_json, url):
        
        if self.__wlan.isconnected():
            pass

        else:
            return "unable to send: no connection"
        
if __name__ == "__main__":
    wifi = wifiManager()
    wifi.connect_known()