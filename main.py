from time import sleep
from machine import UART, Pin

# Communication via UART
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

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
            print(f"speed: {v}")


    sleep(0.02)