#!/usr/bin/env python3

import time
from neopixel import *
from gpiozero import Button
import argparse

# LED strip configuration:
LED_COUNT      = 5      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 150
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

button1 = Button(14)
button2 = Button(15)

# Define functions which animate LEDs in various ways.

def set_red(strip, value=200):
    """Set HAL to the correct brightness of red based on how many buttons are pressed"""
    for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0,value,0))
    strip.show()


# Main program logic follows:
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:

            if button1.is_pressed and button2.is_pressed:
                set_red(strip,120)
            elif button1.is_pressed or button2.is_pressed:
                set_red(strip, 180)
            else:
                set_red(strip, 250)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)

