from gpiozero import AngularServo, Button, LED
from time import sleep
from util import comms
import argparse

SERVO_GPIO          = 19
SERVO_MIN_ANGLE     = 0
SERVO_MAX_ANGLE     = 179
SERVO_INITIAL_ANGLE = 179

BUTTON_GPIO         = 5
LED1_GPIO           = 17
LED2_GPIO           = 27


class Zoltar(object):
    def __init__(self):
        print('Finally, a Zoltar!')
        self.is_moving = False
        self.left_eye = LED(LED1_GPIO)
        self.right_eye = LED(LED2_GPIO)

    def begin_moving(self):
        self.left_eye.on()
        self.right_eye.on()
        servo = AngularServo(SERVO_GPIO,
                     min_angle=SERVO_MIN_ANGLE,
                     max_angle=SERVO_MAX_ANGLE,
                     initial_angle=SERVO_INITIAL_ANGLE)
        while self.is_moving:
            for x in reversed(range(0, 179)):
                servo.angle = x
                sleep(0.01)
            for x in range(0, 179):
                servo.angle = x
                if servo.angle == 0 :
                    sleep(0.5)
                else:
                    sleep(0.01)
        self.finale()

    def eyes_off(self):
        self.right_eye.off()
        self.left_eye.off()

    def eyes_on(self):
        self.left_eye.on()
        self.right_eye.on()

    def finale(self):
        self.eyes_off()
        sleep(1)
        self.eyes_on()
        sleep(1)
        self.eyes_off()
        sleep(1)
        self.eyes_on()
        sleep(1)
        self.eyes_off()

    def stop_moving(self):
        print('Button detected')
        self.is_moving = False
        self.right_eye.off()
        self.left_eye.off()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', action='store_true', help='local mode - play game over and over')
    args = parser.parse_args()

    wof = comms.Comms()
    wof.begin('zoltar')

    while True:
        button = Button(BUTTON_GPIO)
        if args.local:
            a_zoltar = Zoltar()
            button.when_pressed = a_zoltar.stop_moving
            a_zoltar.is_moving = True
            a_zoltar.begin_moving()
        if wof.available():
            (origin, message) = wof.recv()
            if message == 'RESET':
                a_zoltar = Zoltar()
                button.when_pressed = a_zoltar.stop_moving
                a_zoltar.is_moving = True
                a_zoltar.begin_moving()
            else:
                print('Unknown message: ', message)
        sleep(1)
