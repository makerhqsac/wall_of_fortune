#!/usr/bin/env python3
###############################################################################
# hall_detect.py                                                              #
#                                                                             #
#    Detect magnet over surface of map for Cartesian game                     #
#                                                                             #
#    For more information, see https://github.com/makerhqsac/wall_of_fortune  #
#                                                                             #
#    Written By:                                                              #
#    Sean Walker <me@seanwalker.org>                                          #
#    Richard Julian <richard@rjulian.net>                                     #
#    Sponsored by MakerHQ - http://www.makerhq.org                            #
#                                                                             #
#    Licensed under the GPLv3 - https://www.gnu.org/licenses/gpl-3.0.txt      #
###############################################################################


# Import required libraries
import time
import datetime
import RPi.GPIO as GPIO
import spidev

HALL_PIN = 17
LEDS = [25, 5, 6, 12, 13, 19, 26]

current = 0

ROUTES = [
[0,1,2],
[1,2,3],
[2,3,4],
[3,4,5],
[4,5,6],
[5,6,0],
[6,0,1]
];

LED_MAPPING = {
        25 : 'NewAmsterdam',
        5 : 'Lima',
        6 : 'BuenosAires',
        12 : 'London',
        13 : 'Venice',
        19 : 'Capetown',
        26 : 'Ceylon'
        }

ROUTELENGTH = 3
ROUTES = 5
current_route = 0
route_index = 0
timeout = 60
threshold = 3

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)

# Set Switch GPIO as input
# Pull high by default
GPIO.setup(HALL_PIN , GPIO.IN, pull_up_down=GPIO.PUD_UP)

for l in LEDS:
  GPIO.setup(l, GPIO.OUT)
GPIO.add_event_detect(HALL_PIN, GPIO.BOTH, callback=sensor_callback, bouncetime=200)


# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def read_channel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def convert_volts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts

def sensor_callback(channel):
  # Called if sensor output changes
  timestamp = time.time()
  stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
  if GPIO.input(channel):
    # No magnet
    print("Sensor HIGH " + stamp + " " + str(current))
  else:
    # Magnet
    print("Sensor LOW " + stamp)
    next_location()

def next_location():
  route_index += 1
  # Do game logic here. Advance to next location or win the level.
  if route_index < ROUTELENGTH :
    current = ROUTES[current_route][route_index]
    clear_leds()
    set_led_on(current)
  else:
    winner()

def winner():
    print("winner!")
    current_route += 1
    route_index = 0
    if current_route >= 5:
      current_route = 0

def loser():
    print("loser!")
    current_route += 1
    route_index = 0
    if current_route >= 5:
      current_route = 0

def clear_leds():
  for l in LEDS:
    GPIO.output(l,GPIO.LOW)

def set_led_on(channel):
  GPIO.output(LEDS[channel],GPIO.HIGH)



def main():
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.

  current = 0

  # Get initial reading
  sensor_callback(HALL_PIN)

  try:
    start_time = time.time()
    # Loop until users quits with CTRL-C
    clear_leds()
    set_led_on(current)
    while True :
      mag_level = read_channel(current)
      mag_volts = convert_volts(mag_level,2)
      if (mag_volts > threshold):
        next_location()
        clear_leds()
        set_led_on(current)
      if (time.time() - start_time > timeout):
        loser()

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

if __name__=="__main__":
   main()
