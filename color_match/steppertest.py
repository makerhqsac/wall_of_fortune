#!/usr/bin/env python3

import time
from gpiozero import PhaseEnableMotor


secs_per_rev = 1.06
revs_per_dispense = 2
dir_pin = 26
step_pin = 19



speed = 400 # in steps per second

motor = PhaseEnableMotor(dir_pin, step_pin)


def dispense(items=1):

    motor.backward(0.5)
    motor.enable_device.frequency = speed

    time.sleep(secs_per_rev * revs_per_dispense * items)

    motor.stop()


dispense(2)