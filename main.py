import time
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

buffer = bytearray()
while True: 
    if uart.any():

        data = uart.read()
        if not data:
            continue

        speeds = []
        buffer.extend(data)
        while len(buffer) >= 10:
            frame_start = buffer.find(b'\x55\xA2\xC1') # finding header

            if frame_start == -1 or frame_start + 10 > len(buffer):
                break

            frame = buffer[frame_start:frame_start+10]
            buffer = buffer[frame_start+10:] # Removing invalid bytes before a frame and the frame itself from buffer

            speed = frame[5]*256 + frame[6]
            speed *= 0.0223694
            speeds.append(speed)

        if not speeds:
            continue

        if max(speeds) > 10:
            # Clearing oled then display velocity
            oled.fill(0)
            oled.draw_text_max(f"{max(speeds):.0f} mph")
            oled.show()

    time.sleep(0.01)