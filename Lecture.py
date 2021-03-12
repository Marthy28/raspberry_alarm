#!/usr/bin/env python
# -*- coding: utf8 -*-
# Version modifiee de la librairie https://github.com/mxgxw/MFRC522-python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from multiprocessing import Process
import signal
import asyncio
import time
import datetime

GPIO.setwarnings(False)
id_key = 9892398551462

sensor = 14
buzzer = 15
readyToScan = 18
now = 0
secondsLater = 0

GPIO.setmode(GPIO.BCM)  # utilisation des numéros de ports

# pin sensor gpio 14 (8)
GPIO.setup(sensor, GPIO.IN)
# pin buzzer gpio 15 (9)
GPIO.setup(buzzer, GPIO.OUT)
# pin buzzer gpio 15 (9)
GPIO.setup(readyToScan, GPIO.OUT)

reader = SimpleMFRC522()
# Fonction qui arrete la lecture proprement

def end_read(signal, frame):
    global continue_reading
    print("Lecture terminée")
    GPIO.cleanup()

def alarmOn():
    print("Artchung alarm")
    for i in range(50):
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(0.1)

def waitForScan():
    scanned = False
    GPIO.output(readyToScan, GPIO.HIGH)
    print("en attente d'un badge...")
    while scanned == False:
        id, text = reader.read()
        if id == id_key:
            scanned = True
            continue_reading = False
            print("Bienvenue !")
        else:
            print("Erreur d\'Authentification")


def wait():
    print("début de l'attente")
    time.sleep(10)
    print("fin de l'attente")

def end(scanned):
    GPIO.output(readyToScan, GPIO.LOW)
    if scanned == False:
        alarmOn()
    GPIO.cleanup()
        
if __name__ == '__main__':
    GPIO.output(buzzer, GPIO.LOW)
    if GPIO.input(sensor):  # si ça détecte quelque chose
        print("Vous êtes qui ?")
        #now = datetime.datetime.now()
        #secondsLater = now.replace(second = 10)

        p1 = Process(target=waitForScan)
        p1.start()
        p2 = Process(target=wait)
        p2.start()
        # while scanned == False and secondsLater > now:
        #now = datetime.datetime.now()

        # if (scanned == False):
        #    alarmOn()
        #continue_reading = False
