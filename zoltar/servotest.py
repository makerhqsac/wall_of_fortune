from gpiozero import AngularServo
from time import sleep

SERVO_GPIO          = 17
SERVO_MIN_ANGLE     = 0
SERVO_MAX_ANGLE     = 179
SERVO_INITIAL_ANGLE = 90



servo = AngularServo(SERVO_GPIO,
                     min_angle=SERVO_MIN_ANGLE,
                     max_angle=SERVO_MAX_ANGLE,
                     initial_angle=SERVO_INITIAL_ANGLE)

while True:
    servo.angle(0)
    print("0")
    sleep(0.5)
    servo.angle(90)
    print("90")
    sleep(1)
    servo.angle(135)
    print("135")
    sleep(0.5)
    servo.angle(179)
    print("179")
    sleep(1)