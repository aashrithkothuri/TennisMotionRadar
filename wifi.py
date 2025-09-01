# Wifi manager class
# Add a known_networks.json file in the following format to use connect_known() method:
# [
#   {"SSID":"Home","PASS":"homepass"},
# ]

import network, uos as os, time, ujson as json, urequests as requests

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

        self.__wlan.disconnect()

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

            # give DHCP a little more time without changing constants elsewhere
            # (light wait loop that only runs if still not connected and no fatal status)
            if (not self.__wlan.isconnected()) and (self.__wlan.status() >= 0):
                t0 = time.ticks_ms()
                while (not self.__wlan.isconnected()) and (time.ticks_diff(time.ticks_ms(), t0) < 12000):
                    # additional brief wait for IP assignment
                    time.sleep_ms(250)
                    if self.__wlan.status() < 0:
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
        if self.__wlan.isconnected():  # guard print with check
            print(f"Connected to: {SSID}, config: {self.__wlan.ifconfig()}")
            return True
        else:  # explicit failure path if we exhausted retries
            print("unable to connect: timed out")
            return False

    # Method to connect to known networks (defined by known_networks.json)
    def connect_known(self):

        self.__wlan.disconnect()
        
        try:

            # Raises an error if known_networks.json doesn't exist
            os.stat("known_networks.json")

            # Opening json file
            with open("known_networks.json", "r") as f:

                # Parsing json to list (list of dict)
                networks = json.load(f)

                # trying to connect to each known network (in the order they are listed in)
                for network in networks:
                    SSID = network["SSID"]
                    PASS = network["PASS"]
                    # return immediately on first success; otherwise keep trying
                    if self.connect(SSID=SSID, PW=PASS):
                        return True

                # if we iterated all and none worked, return False
                return False

        except Exception as e:
            print(e)
            return False

    # Method to send data to an api via POST
    def send_POST(self, send_json, url):
        
        if self.__wlan.isconnected():
            
            try:
                # making request
                r = requests.post(
                    url,
                    data=json.dumps(send_json),
                    headers={"Content-Type": "application/json", "Connection": "close"},
                )       
                try:
                    _ = r.text  # force read to drain socket
                finally:
                    r.close()
                return True  # signal success
            except Exception as e:
                print(e)
                return False  # signal failure

        else:
            return False
        
if __name__ == "__main__":
    wifi = wifiManager()
    ok = wifi.connect_known()

    if not ok:  # bail out if we failed to connect
        raise SystemExit("No known network connected")

    wifi.send_POST({},"https://httpbin.org/post")
