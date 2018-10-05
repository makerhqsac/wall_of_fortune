#!/usr/bin/env python3
from time import sleep
import time
import datetime
from gpiozero import LED, Button

ROUTES = [
['NewAmsterdam','Lima','BuenosAires'],
['Lima','BuenosAires','London'],
['BuenosAires','London','Venice'],
['London','Venice','Capetown'],
['Venice','Capetown','Ceylon'],
['Capetown','Ceylon','NewAmsterdam'],
['Ceylon','NewAmsterdam','Lima']
]

LED_MAPPING = {
        25 : 'NewAmsterdam',
        5 : 'Lima',
        6 : 'BuenosAires',
        12 : 'London',
        13 : 'Venice',
        19 : 'Capetown',
        26 : 'Ceylon'
        }

HALL_MAPPING = {
        4 : 'NewAmsterdam',
        17 : 'Lima',
        18 : 'BuenosAires',
        27 : 'London',
        22 : 'Venice',
        23 : 'Capetown',
        24 : 'Ceylon'
        }

TIMEOUT = 60

def read_introduction():
    print('You are the captain')

class XyChase(object):
    def __init__(self):
        print('A new chase begins')
        self.initiate_buttons()
        self.initiate_leds()
        self.create_mapping()
        self.routes_completed = 0
        self.current_route = 0
        self.current_destination = 0
        self.route_status = [ 'Uninitiated', 'Uninitiated', 'Uninitiated' ]


    def initiate_buttons(self):
        self.button1 = Button(4)
        self.button2 = Button(17)
        self.button3 = Button(18)
        self.button4 = Button(27)
        self.button5 = Button(22)
        self.button6 = Button(23)
        self.button7 = Button(24)

    def initiate_leds(self):
        self.led1 = LED(25)
        self.led2 = LED(5)
        self.led3 = LED(6)
        self.led4 = LED(12)
        self.led5 = LED(13)
        self.led6 = LED(19)
        self.led7 = LED(26)

    def cleanup_hardware(self):
        self.close_buttons()
        self.close_leds()

    def close_buttons(self):
        self.button1.close()
        self.button2.close()
        self.button3.close()
        self.button4.close()
        self.button5.close()
        self.button6.close()
        self.button7.close()

    def close_leds(self):
        self.led1.close()
        self.led2.close()
        self.led3.close()
        self.led4.close()
        self.led5.close()
        self.led6.close()
        self.led7.close()

    def create_mapping(self):
        self.mapping = {
                'NewAmsterdam' : [self.button1, self.led1],
                'Lima' : [self.button2, self.led2],
                'BuenosAires' : [self.button3, self.led3],
                'London' : [self.button4, self.led4],
                'Venice' : [self.button5, self.led5],
                'Capetown' : [self.button6, self.led6],
                'Ceylon' : [self.button7, self.led7]
                }

    def next_destination(self):
        destination = ROUTES[self.current_route][self.current_destination]
        self.route_status[self.current_destination] = 'Completed'
        self.mapping[destination][0].when_pressed = None
        self.mapping[destination][1].off()
        self.current_destination += 1

    def pickup_cargo(self):
        destination = ROUTES[self.current_route][self.current_destination]
        print('Pick up cargo at', destination)
        self.mapping[destination][0].when_pressed = self.next_destination
        sleep(0.5)
        self.mapping[destination][1].on()
        self.route_status[self.current_destination] = 'InProgress'

    def safe_harbor(self):
        destination = ROUTES[self.current_route][self.current_destination]
        self.deliver_next_cargo()
        print('There is a storm at sea.')
        print('Take safe harbor at ', destination)
        self.mapping[destination][0].when_pressed = self.next_destination
        sleep(0.5)
        self.mapping[destination][1].on()
        self.route_status[self.current_destination] = 'InProgress'

    def deliver_cargo(self):
        destination = ROUTES[self.current_route][self.current_destination]
        print('The seas have calmed')
        print('Deliver your cargo to ', destination)
        self.mapping[destination][0].when_pressed = self.next_destination
        sleep(0.5)
        self.mapping[destination][1].on()
        self.route_status[self.current_destination] = 'InProgress'

    def deliver_next_cargo(self):
        destination = ROUTES[self.current_route + 1][self.current_destination]
        print('Deliver your cargo to ', destination)

    def check_game_status(self):
        if self.route_status[self.current_destination] == 'Uninitiated':
            route_state = self.route_status[self.current_destination]
            if self.current_destination == 0 and route_state != 'InProgress':
                self.pickup_cargo()
            if self.current_destination == 1 and route_state != 'InProgress':
                self.safe_harbor()
            if self.current_destination == 2 and route_state != 'InProgress':
                self.deliver_cargo()

    def lose_game(self):
        print('Oh no, you lost')
        self.cleanup_hardware()

    def win_game(self):
        print('You won, congrats!')
        self.cleanup_hardware()

    def begin_game(self):
        read_introduction()
        self.start_time = time.time()
        while True:
            if time.time() - self.start_time > TIMEOUT:
                self.lose_game()
                break
            if self.current_destination == 3:
                self.win_game()
                break
            self.check_game_status()

def main():
    while True :
        chase = XyChase()
        chase.begin_game()
        sleep(10)

if __name__=="__main__":
   main()
