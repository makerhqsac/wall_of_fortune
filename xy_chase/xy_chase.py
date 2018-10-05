#!/usr/bin/env python3
from time import sleep
from utils import comms
import time
import subprocess
import datetime
import random
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

def send_signal(message):
    wof = comms.Comms()
    wof.begin('cartography')
    wof.send(message)

def read_introduction():
    play_static_audio('YouAreTheCaptain.ogg')

def play_static_audio(file_name):
    file_path = './xy_chase/audio/%s' % (file_name)
    subprocess.call(['ogg123',file_path])


class XyChase(object):
    def __init__(self):
        print('A new chase begins')
        self.initiate_buttons()
        self.initiate_leds()
        self.create_mapping()
        self.routes_completed = 0
        self.current_route = random.randint(0,6)
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
        cargo_file = 'TakeCargo%s.ogg' % (destination)
        play_static_audio(cargo_file)
        self.mapping[destination][0].when_pressed = self.next_destination
        sleep(0.5)
        self.mapping[destination][1].on()
        self.route_status[self.current_destination] = 'InProgress'

    def safe_harbor(self):
        destination = ROUTES[self.current_route][self.current_destination]
        self.deliver_next_cargo()
        play_static_audio('StormAtSea.ogg')
        harbor_file = 'MakeHarbors%s.ogg' % (destination)
        play_static_audio(harbor_file)
        self.mapping[destination][0].when_pressed = self.next_destination
        sleep(0.5)
        self.mapping[destination][1].on()
        self.route_status[self.current_destination] = 'InProgress'

    def deliver_cargo(self):
        destination = ROUTES[self.current_route][self.current_destination]
        play_static_audio('SeasHaveCalmed.ogg')
        deliver_file = 'Deliver%s.ogg' % (destination)
        play_static_audio(deliver_file)
        self.mapping[destination][0].when_pressed = self.next_destination
        sleep(0.5)
        self.mapping[destination][1].on()
        self.route_status[self.current_destination] = 'InProgress'

    def deliver_next_cargo(self):
        destination = ROUTES[self.current_route][self.current_destination + 1]
        deliver_file = 'Deliver%s.ogg' % (destination)
        play_static_audio(deliver_file)
        self.mapping[destination][0].when_pressed = self.next_destination
        self.mapping[destination][1].on()
        sleep(5)
        self.mapping[destination][0].when_pressed = None
        self.mapping[destination][1].off()

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
        play_static_audio('PirateLost.ogg')
        self.cleanup_hardware()
        send_signal('RESET')

    def win_game(self):
        play_static_audio('PirateWon.ogg')
        self.cleanup_hardware()
        send_signal('CARTDONE')

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
    wof = comms.Comms()
    wof.begin('cartography')

    while True :
        if wof.available():
            (origin, message) = wof.recv()
            if message == 'COMPLETE' and origin == 'zoltar':
                chase = XyChase()
                chase.begin_game()

if __name__=="__main__":
   main()
