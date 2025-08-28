from time import sleep
from machine import UART, Pin

uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

while True: 
    if uart.any():
        line = uart.readline()
        if not line:
            continue
        print(line)
    sleep(0.02)