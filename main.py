from time import sleep
from machine import I2C, UART, Pin
from ssd1306 import SSD1306_I2C
from wifi import wifiManager
import utime as time

# Communication via UART (for radar module)
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

# Communication via I2C (for oled)
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)

# Init oled
oled = SSD1306_I2C(128, 32, i2c)

#############################
# wifi related code 
# (not critical for radar gun function)

# Creating manager and connecting to a network
manager = wifiManager()
manager.connect_known()
#############################

while True: 
    if uart.any():

        # Getting UART data
        data = uart.read()

        # If line is falsy 
        if not data:
            continue

        # If its valid data, print speed (increments of 52cm/s)
        if len(data) == 10:
            # converting corresponding bytes (big endian) to velocity (cm/s)
            v = data[5]*256 + data[6] 

            # Converting to mph
            v = (v*100)/(3600 * 1.6)

            if v >= 10: # lower constraint for testing

                # Clearing oled then display velocity
                oled.fill(0)
                oled.draw_text_max(f"{v:.0f} mph")
                oled.show()

                ############################
                # Data upload related code 
                # (not critical for radar gun function)

                # Wrapping data in a dict and sending data to api via post
                send_json = {"speed":v, "time":time.time()}
                manager.send_POST(send_json,"https://210bd431398fe0.lhr.life")

                ############################


    sleep(0.01)