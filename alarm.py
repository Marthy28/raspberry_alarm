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

from google.cloud import firestore

# Add a new document
db = firestore.Client()

# Then query for documents
users_ref = db.collection(u'alarms').document(u'xshiCmkPvzXIfBCHiju3')

for doc in users_ref.stream():
    print(u'{} => {}'.format(doc.id, doc.to_dict()))

GPIO.setwarnings(False)
id_key = "9892398551462"

now = 0
secondsLater = 0

GPIO.setmode(GPIO.BCM)  # utilisation des numéros de ports

# Captor of presence
# pin sensor gpio 18 (8)
sensor = 18
GPIO.setup(sensor, GPIO.IN)

# Red LED
# pin buzzer gpio 23 (9)
buzzer = 23
GPIO.setup(buzzer, GPIO.OUT)

# Blue LED
# pin buzzer gpio 24 (9)
readyToScan = 24
GPIO.setup(readyToScan, GPIO.OUT)

reader = SimpleMFRC522()
# Fonction qui arrete la lecture proprement


def alarmBlink(alarm=23, numBlink=50):
    print("Alarm Blink", alarm)
    for i in range(numBlink):
        GPIO.output(alarm, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(alarm, GPIO.LOW)
        time.sleep(0.1)


def waitForScan():
    scanned = False
    GPIO.output(readyToScan, GPIO.HIGH)
    print("en attente d'un badge...")
    while scanned == False:
        id, text = reader.read()
        print("text : " + text.replace(" ", "") +
              " - " + str(len(text.replace(" ", ""))))
        print("id : " + str(id) + " - " + str(len(str(id))))
        print("id_key : " + str(id_key) + " - " + str(len(str(id_key))))
        if text.replace(" ", "") == id_key:
            scanned = True
            continue_reading = False
            print("Bienvenue !")
        else:
            print("Erreur d\'Authentification")
    onDetect = True
    end(True)


def wait():
    print("début de l'attente")
    time.sleep(10)
    print("fin de l'attente")
    end(False)


def end(scanned):
    GPIO.output(readyToScan, GPIO.LOW)
    if scanned == False:
        alarmBlink(buzzer)
    GPIO.cleanup()


if __name__ == '__main__':
    print("Start")
    a1 = Process(target=alarmBlink, args=(buzzer, 5))
    a1.start()
    a2 = Process(target=alarmBlink, args=(readyToScan, 5))
    a2.start()
    a1.join()
    a2.join()
    time.sleep(1)

    GPIO.output(buzzer, GPIO.LOW)
    loop = True
    onDetect = True

    while loop:
        # print("GPIO.input(sensor)", GPIO.input(sensor))
        # print("onDetect", onDetect)
        # time.sleep(1)
        # si ça détecte quelque chose
        if GPIO.input(sensor) and onDetect:

            print("Vous êtes qui ?")
            p1 = Process(target=waitForScan)
            p1.start()
            p2 = Process(target=wait)
            p2.start()

            p1.join()
            p2.kill()

            GPIO.setup(sensor, GPIO.IN)
            GPIO.setup(buzzer, GPIO.OUT)
            GPIO.setup(readyToScan, GPIO.OUT)

            onDetect = False
