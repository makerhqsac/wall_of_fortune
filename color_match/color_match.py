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
from utils import comms


# game configuration:
GAME_TIMEOUT_SECS       = 90
DEBUG_STATUS_SECS       = 5
COLOR_HIGHEST_BIT       = 7


# stepper motor configuration:
MOT_DIR_PIN             = 26
MOT_STEP_PIN            = 19
MOT_SPEED               = 400 # in steps per second


# button mapping configuration:
BUTTONS = {
    'r1': {'btn': gpiozero.Button(4, pull_up=True, bounce_time=0.01), 'latched': True, 'pressed': False },
    'r2': {'btn': gpiozero.Button(17, pull_up=True, bounce_time=0.01), 'latched': True, 'pressed': False },
    'r3': {'btn': gpiozero.Button(27, pull_up=True, bounce_time=0.01), 'latched': True, 'pressed': False },
    'g1': {'btn': gpiozero.Button(22, pull_up=True, bounce_time=0.01), 'latched': False, 'pressed': False },
    'g2': {'btn': gpiozero.Button(5, pull_up=True, bounce_time=0.01), 'latched': False, 'pressed': False },
    'g3': {'btn': gpiozero.Button(6, pull_up=True, bounce_time=0.01), 'latched': False, 'pressed': False },
    'b1': {'btn': gpiozero.Button(20, pull_up=True, bounce_time=0.01), 'latched': False, 'pressed': False },
    'b2': {'btn': gpiozero.Button(21, pull_up=True, bounce_time=0.01), 'latched': True, 'pressed': False }
}

# dispensing configuration:
SECS_PER_REV            = 1.06
REVS_PER_DISPENSE       = 1


# led strip configuration:
LED_COUNT               = 2       # Number of LED pixels.
LED_PIN                 = 18      # GPIO pin connected to the pixels. (Y on RetroHAT)
LED_FREQ_HZ             = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA                 = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS          = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT              = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL             = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


PIXEL_CURRENT           = 0      # LED number of current color
PIXEL_TARGET            = 1      # LED number of target color


motor = gpiozero.PhaseEnableMotor(MOT_DIR_PIN, MOT_STEP_PIN)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, ws.WS2812_STRIP)
strip.begin()

wof = comms.Comms()


def setup_buttons(args):
    for btn in BUTTONS:
        if not BUTTONS[btn]['latched']:
            BUTTONS[btn]['btn'].when_pressed = handle_toggle


def handle_toggle(pressedBtn):
    for btn in BUTTONS:
        if BUTTONS[btn]['btn'] == pressedBtn:
            BUTTONS[btn]['pressed'] = not BUTTONS[btn]['pressed']


def color_wipe(color, wait=0.05):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait)


def read_switch(btn):
    if BUTTONS[btn]['latched']:
        return BUTTONS[btn]['btn'].value
    else:
        return BUTTONS[btn]['pressed']


def read_switches():
    rbyte = 0
    gbyte = 0
    bbyte = 0

    # FIXME: use LS bits or MS bits of each color byte for best color?
    rbyte |= read_switch('r1') << COLOR_HIGHEST_BIT
    rbyte |= read_switch('r2') << COLOR_HIGHEST_BIT - 1
    rbyte |= read_switch('r3') << COLOR_HIGHEST_BIT - 2

    gbyte |= read_switch('g1') << COLOR_HIGHEST_BIT
    gbyte |= read_switch('g2') << COLOR_HIGHEST_BIT - 1
    gbyte |= read_switch('g3') << COLOR_HIGHEST_BIT - 2

    bbyte |= read_switch('b1') << COLOR_HIGHEST_BIT
    bbyte |= read_switch('b2') << COLOR_HIGHEST_BIT - 1

    return (rbyte << 16) | (gbyte << 8) | bbyte


def dispense(items=1):

    motor.backward(0.5)
    motor.enable_device.frequency = MOT_SPEED

    time.sleep(SECS_PER_REV * REVS_PER_DISPENSE * items)

    motor.stop()


def blink_panels(color, times, delay, wait=0):
    for i in range(times):
        color_wipe(color, wait)
        time.sleep(delay)
        color_wipe(0, 0)
        time.sleep(delay)


def run_game(args):

    target_color = 0
    switch_color = read_switches()

    if args.target:
        target_color = int(args.target)
    else:
        while target_color == 0 or target_color == switch_color:
            target_r = random.randint(1, 7) << COLOR_HIGHEST_BIT - 2
            target_r &= 0xE0
            target_g = random.randint(1, 7) << COLOR_HIGHEST_BIT - 2
            target_g &= 0xE0
            target_b = random.randint(0, 3) << COLOR_HIGHEST_BIT - 2
            target_b &= 0xC0
            target_color = Color(target_r, target_g, target_b)

    if args.debug:
        print("Starting game with target color bits: {0:08b} {1:08b} {2:08b}".format((target_color >> 16) & 0xFF,
                                                                                     (target_color >> 8) & 0xFF,
                                                                                     target_color & 0xFF))

    strip.setPixelColor(PIXEL_TARGET, target_color)

    start_time = time.time()
    debug_time = start_time

    while True:
        switch_color = read_switches()

        if args.debug:
            if time.time() >= debug_time:
                debug_time = time.time() + DEBUG_STATUS_SECS
                print("Current bits: {0:08b} {1:08b} {2:08b}    ::   target bits:  {3:08b} {4:08b} {5:08b}".format(
                    (switch_color >> 16) & 0xFF,
                    (switch_color >> 8) & 0xFF,
                    switch_color & 0xFF,
                    (target_color >> 16) & 0xFF,
                    (target_color >> 8) & 0xFF,
                    target_color & 0xFF))

        strip.setPixelColor(PIXEL_CURRENT, switch_color)
        strip.show()
        time.sleep(0.1)

        if switch_color == target_color:
            if args.debug:
                print("WINNER WINNER!")
            blink_panels(Color(0, 255, 0), 6, 0.2)
            dispense(1)
            return
        elif start_time + GAME_TIMEOUT_SECS < time.time():
            if args.debug:
                print("TIMEOUT - YOU LOOSE")
            blink_panels(Color(255, 0, 0), 6, 0.3)
            return


def run_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug mode')
    parser.add_argument('-x', '--target', action='store', help='set target to specific color')
    parser.add_argument('-l', '--local', action='store_true', help='local mode - play game over and over')
    args = parser.parse_args()

    if args.target:
        if args.debug:
            print("Target set to {0}.".format(args.target))

    wof.begin("colormatch")

    try:
        setup_buttons(args)

        while True:
            if args.local:
                run_game(args)
                color_wipe(Color(0, 0, 0), 0)
                time.sleep(3)
            elif wof.available():
                (origin, message) = wof.recv()
                if args.debug:
                    print("Received network message from {0}: {1}".format(origin, message))
                if message == 'RESET':
                    run_game(args)
                    color_wipe(Color(0, 0, 0), 0)
                else:
                    if args.debug:
                        print("Unknown message: {0}".format(message))
            else:
                time.sleep(1)

    except KeyboardInterrupt:
        color_wipe(Color(0, 0, 0), 0.1)


# Main program logic follows:
if __name__ == '__main__':
    run_main()