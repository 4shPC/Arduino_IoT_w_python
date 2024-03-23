"""
Ashutosh Chaudhari
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

LOWER_TEMPERATURE_THRESHOLD = 22
HIGHER_TEMPERATURE_THRESHOLD = 24

# A callback function to display the distance
def callback(data):
    global TEMPERATURE
    global HUMIDITY
    global DATE
    
    if data[1]:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[4]))
        print(f'DHT Error:'
              f'Pin: {data[2]} DHT Type: {data[3]} Error: {data[1]}  Time: {date}')
        board.shutdown()
        sys.exit(0)

    else:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[6]))
        TEMPERATURE = data[5]
        HUMIDITY = data[4]
        DATE = date
        print(f'DHT Report: '
        f'Humidity: {HUMIDITY} Temperature: {TEMPERATURE} Time: {DATE}')

    

def map_function(value, from_low, from_high, to_low, to_high):
  scaled_value = (value - from_low) * ((to_high - to_low) / (from_high - from_low))
  return max(min(scaled_value + to_low, to_high), to_low)
            
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
board.set_pin_mode_analog_output(MOTOR_PIN1)
board.set_pin_mode_digital_output(MOTOR_PIN2)


try:
    send_message("Machine Starting Up!!!")
    dht(board, DHT_PIN1, callback, 11)
    while True:
        isOverHeated = True if TEMPERATURE>HIGHER_TEMPERATURE_THRESHOLD else False
        fan_speed = int(map_function(TEMPERATURE, LOWER_TEMPERATURE_THRESHOLD, HIGHER_TEMPERATURE_THRESHOLD, 150, 255))
        board.analog_write(MOTOR_PIN1, fan_speed)

        if isOverHeated and not isMsgSent: 
            board.digital_write(GREEN_LED, 0)
            board.digital_write(RED_LED, 1)
            board.digital_write(MOTOR_PIN2, 0)
            send_message("Machine Overheated!!  |  FAN AT FULL SPEED")
            isMsgSent = True


        elif not isOverHeated: 
            isMsgSent = False
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

