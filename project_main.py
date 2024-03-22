"""
1. Keep fan on at low speed all the time 
2. speed should be proportional to the temperature of the machine

"""

import sys
import time
import pywhatkit as wk
from telemetrix import telemetrix

# PINS
DHT_PIN1 = 8
GREEN_LED = 2
RED_LED = 3

MOTOR_PIN1 = 5
MOTOR_PIN2 = 6 

TEMPERATURE = -273
HUMIDITY = 0

isOverHeated = False
isMsgSent = False

# A callback function to display the distance
def callback(data):
    global TEMPERATURE
    global HUMIDITY
    
    if data[1]:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[4]))
        print(f'DHT Error Report:'
              f'Pin: {data[2]} DHT Type: {data[3]} Error: {data[1]}  Time: {date}')
        
    else:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[6]))
        TEMPERATURE = data[5]
        HUMIDITY = data[4]
        print(f'DHT Valid Data Report:'
              f'Pin: {data[2]} DHT Type: {data[3]} Humidity: {data[4]} Temperature:'
              f' {data[5]} Time: {date}')
    

            
def dht(board, pin, callback, dht_type):
    board.set_pin_mode_dht(pin, callback, dht_type)

def send_message(message):
    try:
        wk.sendwhatmsg_instantly("+17653374741",f"{message}", 10, tab_close=True)
    except:
        print("Network Error Occurred")

board = telemetrix.Telemetrix()   # Telemetrix Object

board.set_pin_mode_digital_output(RED_LED)
board.set_pin_mode_digital_output(GREEN_LED)
board.set_pin_mode_digital_output(MOTOR_PIN1)
board.set_pin_mode_digital_output(MOTOR_PIN2)


try:
    send_message("Machine Starting Up!!!")
    dht(board, DHT_PIN1, callback, 11)
    while True:
        isOverHeated = True if TEMPERATURE>22.75 else False

        if isOverHeated and not isMsgSent: 
            board.digital_write(GREEN_LED, 0)
            board.digital_write(RED_LED, 1)
            board.digital_write(MOTOR_PIN1, 1)
            board.digital_write(MOTOR_PIN2, 0)
            send_message("Machine Overheated!!  |  FAN STARTED")
            isMsgSent = True


        elif not isOverHeated: 
            isMsgSent = False
            board.digital_write(MOTOR_PIN1, 0)
            board.digital_write(MOTOR_PIN2, 0)
            board.digital_write(GREEN_LED, 1)
            board.digital_write(RED_LED, 0)


        try:
            time.sleep(.01)
        except KeyboardInterrupt:
            board.shutdown()
            sys.exit(0)
            
except (KeyboardInterrupt, RuntimeError):
    board.shutdown()
    sys.exit(0)

