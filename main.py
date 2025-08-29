from time import sleep
from machine import I2C, UART, Pin
from ssd1306 import SSD1306_I2C

# Communication via UART (for radar module)
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

# Communication via I2C (for oled)
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)

# Init oled
oled = SSD1306_I2C(128, 32, i2c)

while True: 
    if uart.any():

        # Getting UART data
        data = uart.read()

        # If line is falsy 
        if not data:
            continue

        # If its valid data, print speed (increments of 52cm/s)
        if len(data) == 10:
            v = data[5]*256 + data[6] # converting corresponding bytes (big endian) to velocity 

            # Clearing oled then display velocity
            oled.fill(0)
            oled.draw_text_scaled(str(v), 10, 10, 2)
            oled.show()

    sleep(0.02)