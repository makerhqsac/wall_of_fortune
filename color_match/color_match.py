#!/usr/bin/env python3
###############################################################################
# color_match.py                                                              #
#                                                                             #
#    Run the Wall of Fortune Color Match game                                 #
#                                                                             #
#    For more information, see https://github.com/makerhqsac/wall_of_fortune  #
#                                                                             #
#    Written By Mike Machado <mike@machadolab.com>                            #
#    Sponsored by MakerHQ - http://www.makerhq.org                            #
#                                                                             #
#    Licensed under the GPLv3 - https://www.gnu.org/licenses/gpl-3.0.txt      #
###############################################################################


import time
from neopixel import *
import _rpi_ws281x as ws
import argparse
import gpiozero
import random

SWITCH_RBIT1        =  4   # pin for red bit 1
SWITCH_RBIT2        = 17   # pin for red bit 2
SWITCH_RBIT3        = 27   # pin for red bit 3
SWITCH_GBIT1        = 22   # pin for green bit 1
SWITCH_GBIT2        =  5   # pin for green bit 2
SWITCH_GBIT3        =  6   # pin for green bit 3
SWITCH_BBIT1        = 20   # pin for blue bit 1
SWITCH_BBIT2        = 21   # pin for blue bit 2


# LED strip configuration:
LED_COUNT      = 2       # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels. (Y on RetroHAT)
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

PIXEL_CURRENT   = 0      # LED number of current color
PIXEL_TARGET    = 1      # LED number of target color


btn_rbit1 = gpiozero.Button(SWITCH_RBIT1, pull_up=True)
btn_rbit2 = gpiozero.Button(SWITCH_RBIT2, pull_up=True)
btn_rbit3 = gpiozero.Button(SWITCH_RBIT3, pull_up=True)
btn_gbit1 = gpiozero.Button(SWITCH_GBIT1, pull_up=True)
btn_gbit2 = gpiozero.Button(SWITCH_GBIT2, pull_up=True)
btn_gbit3 = gpiozero.Button(SWITCH_GBIT3, pull_up=True)
btn_bbit1 = gpiozero.Button(SWITCH_BBIT1, pull_up=True)
btn_bbit2 = gpiozero.Button(SWITCH_BBIT2, pull_up=True)


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def readSwitches():
    rbyte = 0
    gbyte = 0
    bbyte = 0

    # FIXME: use LS bits or MS bits of each color byte for best color?
    rbyte |= btn_rbit1.value << 7
    rbyte |= btn_rbit2.value << 6
    rbyte |= btn_rbit3.value << 5

    gbyte |= btn_gbit1.value << 7
    gbyte |= btn_gbit2.value << 6
    gbyte |= btn_gbit3.value << 5

    bbyte |= btn_bbit1.value << 7
    bbyte |= btn_bbit2.value << 6

    return (rbyte << 16) | (gbyte << 8) | bbyte


def run_main():
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    # parser.add_argument('-t', '--target', action='store_true', help='set specific target color')
    args = parser.parse_args()

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, ws.WS2812_STRIP)
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        # TODO: implement color override (useful for testing)
        target_r = random.randint(1, 7) << 5
        target_r &= 0xE0
        target_g = random.randint(1, 7) << 5
        target_g &= 0xE0
        target_b = random.randint(0, 3) << 5
        target_b &= 0xC0

        target_color = Color(target_r, target_g, target_b)

        print("Target color bits: {0:08b} {1:08b} {2:08b}".format((target_color>>16)&0xFF, (target_color>>8)&0xFF, target_color&0xFF))

        strip.setPixelColor(PIXEL_TARGET, target_color)


        while True:
            switch_color = readSwitches()

            print("Current bits: {0:08b} {1:08b} {2:08b}".format((switch_color>>16)&0xFF, (switch_color>>8)&0xFF, switch_color&0xFF))

            strip.setPixelColor(PIXEL_CURRENT, switch_color)
            strip.show()
            time.sleep(0.5)

            if switch_color == target_color:
                print("WINNER WINNER!")
                #return

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)


# Main program logic follows:
if __name__ == '__main__':
    run_main()