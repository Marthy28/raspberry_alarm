#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from multiprocessing import Process
import signal
import asyncio
import time
import datetime
import threading
from google.cloud import firestore

# Create an Event for notifying main thread.
callback_done_firestore = threading.Event()
callback_done_reader_nfc = threading.Event()

# Alarm Active
isActive = False
users = []


# # # # # # # # # # # # # # # # # # # # # # # #
#
# GPIO LED and Captor
#
# # # # # # # # # # # # # # # # # # # # # # # #
GPIO.setwarnings(False)
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


def alarmBlink(alarm=23, numBlink=50):
    print("Alarm Blink", alarm)
    for i in range(numBlink):
        GPIO.output(alarm, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(alarm, GPIO.LOW)
        time.sleep(0.1)


def alertBlink(alarm=23):
    global isActive
    while isActive:
        GPIO.output(alarm, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(alarm, GPIO.LOW)
        time.sleep(0.1)


# # # # # # # # # # # # # # # # # # # # # # # #
#
# Reader NFC
#
# # # # # # # # # # # # # # # # # # # # # # # #
nfc_text = "No Data"
reader = SimpleMFRC522()


def on_reader_nfc():
    # global nfc_id
    global nfc_text
    nfc_id, nfc_text = reader.read()
    callback_done_reader_nfc.set()

# # # # # # # # # # # # # # # # # # # # # # # #
#
# Firestore / Database
#
# # # # # # # # # # # # # # # # # # # # # # # #


# Add a new document
db = firestore.Client()

# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    global isActive
    global users
    for doc in doc_snapshot:
        print(f'Received document snapshot: {doc.id}')
        print(doc.to_dict())
        isActive = doc.to_dict().get("isActive", False)
        users = doc.to_dict().get("users", [])
        print(isActive)
        print(users)

    callback_done_firestore.set()


# Watch the alarm
alarm_ref = db.collection('alarms').document('xshiCmkPvzXIfBCHiju3')
doc_watch = alarm_ref.on_snapshot(on_snapshot)


# # # # # # # # # # # # # # # # # # # # # # # #
#
# Program Logic
#
# # # # # # # # # # # # # # # # # # # # # # # #
def waitForScan():
    global isActive
    global users
    global nfc_text

    # Start Scaner NFC
    threading.Thread(target=on_reader_nfc).start()

    scanned = False
    GPIO.output(readyToScan, GPIO.HIGH)
    print("en attente d'un badge...")
    while scanned == False and isActive:
        time.sleep(1)

        print("Id User : '" + nfc_text.replace(" ", "") +
              "' - len : " + str(len(nfc_text.replace(" ", ""))))
        if nfc_text and nfc_text.replace(" ", "") in users:
            print("Bienvenue !")
            alarm_ref.collection('history').document().set({
                'date': str(datetime.datetime.now()),
                'type': 'scan',
                'user_id': nfc_text.replace(" ", "")
            })
            scanned = True
            nfc_text = "No Data"

        else:
            print("Erreur d\'Authentification")
    isActive = False
    alarm_ref.update({'isActive': False})
    GPIO.output(readyToScan, GPIO.LOW)


class CronTimer:
    def __init__(self):
        self._running = True

    def kill(self):
        self._running = False

    def start(self):
        print("début de l'attente")
        time.sleep(10)
        print("fin de l'attente")
        alarm_ref.collection('history').document().set({
            'date': str(datetime.datetime.now()),
            'type': 'alert',
        })
        if isActive and self._running:
            alertBlink()


# # # # # # # # # # # # # # # # # # # # # # # #
#
# Start Program
#
# # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == '__main__':
    print("Start Program")
    # Start / Test LED
    t_buzzer = threading.Thread(target=alarmBlink, args=(buzzer, 5))
    t_buzzer.start()
    t_readyToScan = threading.Thread(target=alarmBlink, args=(readyToScan, 5))
    t_readyToScan.start()
    t_buzzer.join()
    t_readyToScan.join()
    GPIO.output(buzzer, GPIO.LOW)
    GPIO.output(readyToScan, GPIO.LOW)
    time.sleep(1)

    loop = True
    while loop:
        print("GPIO.input(sensor)", GPIO.input(sensor))
        print("isActive", isActive)
        time.sleep(1)
        # si ça détecte quelque chose
        if GPIO.input(sensor) and isActive:

            print("Vous êtes qui ?")
            # Start Scanner
            p1 = threading.Thread(target=waitForScan)
            p1.start()

            # Start Timer Alert
            timer = CronTimer()
            p2 = threading.Thread(target=timer.start)
            p2.start()

            # End
            p1.join()
            timer.kill()
