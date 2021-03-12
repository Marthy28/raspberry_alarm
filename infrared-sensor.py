#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import time

sensor = 14
buzzer = 15

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #utilisation des numéros de ports 
#pin sensor gpio 14 (8) 
GPIO.setup(sensor,GPIO.IN)
#pin buzzer gpio 15 (9)
GPIO.setup(buzzer,GPIO.OUT)
continue_reading = True
# Fonction qui arrete la lecture proprement 
def end_read(signal,frame):
    global continue_reading
    print ("fin du programme")
    continue_reading = False
    GPIO.cleanup()

while continue_reading:
    
    if (GPIO.input(sensor)): 
        print ("objet détecté")
        GPIO.output(buzzer, GPIO.HIGH)
    else : 
        print ("objet détecté")
        GPIO.output(buzzer, GPIO.LOW)
    time.sleep(0.5)