#!/usr/bin/env python
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
import argparse
import gpiozero
import random

SWITCH_RBIT1        = 22   # pin for red bit 1 (1 on RetroHAT)
SWITCH_RBIT2        = 23   # pin for red bit 2 (2 on RetroHAT)
SWITCH_RBIT3        = 27   # pin for red bit 3 (3 on RetroHAT)
SWITCH_GBIT1        =  6   # pin for green bit 1 (START on RetroHAT)
SWITCH_GBIT2        =  5   # pin for green bit 2 (SELECT on RetroHAT)
SWITCH_GBIT3        = 12   # pin for green bit 3 (L_SHLDR on RetroHAT)
SWITCH_BBIT1        = 13   # pin for blue bit 1 (R_SHLDR on RetroHAT)
SWITCH_BBIT2        = 20   # pin for blue bit 2 (X on RetroHAT)


# LED strip configuration:
LED_COUNT      = 2       # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0). (Y on RetroHAT)
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
    rbyte |= btn_rbit1.value << 2
    rbyte |= btn_rbit2.value << 1
    rbyte |= btn_rbit3.value << 0

    gbyte |= btn_gbit1.value << 2
    gbyte |= btn_gbit2.value << 1
    gbyte |= btn_gbit3.value << 0

    bbyte |= btn_bbit1.value << 1
    bbyte |= btn_bbit2.value << 0

    return (rbyte << 16) | (gbyte << 8) | bbyte


def run_main():
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    # parser.add_argument('-t', '--target', action='store_true', help='set specific target color')
    args = parser.parse_args()

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        # TODO: implement color override (useful for testing)
        target_bits = random.randint(1, 256)
        target_r = target_bits >> 5
        target_r &= 0x07
        target_g = target_bits >> 2
        target_g &= 0x07
        target_b = target_bits
        target_b &= 0x03
        target_color = Color(target_r, target_g, target_b)
        strip.setPixelColor(PIXEL_TARGET, target_color)

        while True:
            switch_color = readSwitches()
            strip.setPixelColor(PIXEL_CURRENT, switch_color)
            time.sleep(0.05)

            if switch_color == target_color:
                print("WINNER WINNER!")
                return

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)


# Main program logic follows:
if __name__ == '__main__':
    run_main()