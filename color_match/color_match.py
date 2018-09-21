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


SECS_PER_REV = 1.06
REVS_PER_DISPENSE = 2
MOT_DIR_PIN = 26
MOT_STEP_PIN = 19
MOT_SPEED = 400 # in steps per second


BUTTONS = {
    'rbit1': {'btn': gpiozero.Button(4, pull_up=True), 'latched': True, 'pressed': False },
    'rbit2': {'btn': gpiozero.Button(17, pull_up=True), 'latched': True, 'pressed': False },
    'rbit3': {'btn': gpiozero.Button(27, pull_up=True), 'latched': True, 'pressed': False },
    'gbit1': {'btn': gpiozero.Button(22, pull_up=True), 'latched': False, 'pressed': False },
    'gbit2': {'btn': gpiozero.Button(5, pull_up=True), 'latched': False, 'pressed': False },
    'gbit3': {'btn': gpiozero.Button(6, pull_up=True), 'latched': True, 'pressed': False },
    'bbit1': {'btn': gpiozero.Button(20, pull_up=True), 'latched': True, 'pressed': False },
    'bbit2': {'btn': gpiozero.Button(21, pull_up=True), 'latched': False, 'pressed': False }
}


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


motor = gpiozero.PhaseEnableMotor(MOT_DIR_PIN, MOT_STEP_PIN)


def setupButtons():
    for btn in BUTTONS:
        if not BUTTONS[btn]['latched']:
            BUTTONS[btn]['btn'].when_pressed = handleToggle(btn)


def handleToggle(pressedBtn):
    for btn in BUTTONS:
        if BUTTONS[btn]['btn'] == pressedBtn:
            BUTTONS[btn]['pressed'] = not BUTTONS[btn]['pressed']


def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def readSwitch(btn):
    if BUTTONS[btn]['latched']:
        return BUTTONS[btn]['btn'].value
    else:
        return BUTTONS[btn]['pressed']


def readSwitches():
    rbyte = 0
    gbyte = 0
    bbyte = 0

    # FIXME: use LS bits or MS bits of each color byte for best color?
    rbyte |= readSwitch('rbit1') << 7
    rbyte |= readSwitch('rbit2') << 6
    rbyte |= readSwitch('rbit3') << 5

    gbyte |= readSwitch('gbit1') << 7
    gbyte |= readSwitch('gbit2') << 6
    gbyte |= readSwitch('gbit3') << 5

    bbyte |= readSwitch('bbit1') << 7
    bbyte |= readSwitch('bbit2') << 6

    return (rbyte << 16) | (gbyte << 8) | bbyte


def dispense(items=1):

    motor.backward(0.5)
    motor.enable_device.frequency = MOT_SPEED

    time.sleep(SECS_PER_REV * REVS_PER_DISPENSE * items)

    motor.stop()


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
        setupButtons()

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