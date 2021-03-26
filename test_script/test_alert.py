import pygame
pygame.mixer.init()
pygame.mixer.music.load("alarm.wav")
while True:
    pygame.mixer.music.play()

