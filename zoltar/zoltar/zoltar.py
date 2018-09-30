from gpiozero import AngularServo, Button
from time import sleep

SERVO_GPIO          = 19
SERVO_MIN_ANGLE     = 0
SERVO_MAX_ANGLE     = 179
SERVO_INITIAL_ANGLE = 90

BUTTON_GPIO         = 5

class Zoltar(object):
    def __init__(self):
        print('Finally, a Zoltar!')
        self.is_moving = False

    def begin_moving(self):
        servo = AngularServo(SERVO_GPIO,
                     min_angle=SERVO_MIN_ANGLE,
                     max_angle=SERVO_MAX_ANGLE,
                     initial_angle=SERVO_INITIAL_ANGLE)
        print('We are moving')
        while self.is_moving:
            servo.angle = 0
            print("0")
            sleep(2.5)
            servo.angle = 90
            print("90")
            sleep(1)
            servo.angle = 135
            print("135")
            sleep(0.5)
            servo.angle = 179
            print("179")
            sleep(1)

    def stop_moving(self):
        print('Button detected')
        self.is_moving = False


if __name__ == "__main__":
    button = Button(BUTTON_GPIO)
    a_zoltar = Zoltar()
    button.when_pressed = a_zoltar.stop_moving
    a_zoltar.is_moving = True
    a_zoltar.begin_moving()

