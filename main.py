import os
import sys
import math
import pygame
import neat
from utils import scale_image
from car import Car

track = pygame.image.load(r'images\track_2.png')
red_car = pygame.image.load(r'images\car_f1.png')

width, height = track.get_width(), track.get_height()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("GENETIC AI CAR")

car = pygame.sprite.GroupSingle(Car(red_car, window))

def eval_genomes():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        window.blit(track, (0,0))

        #USER CONTROL
        user_input = pygame.key.get_pressed()
        if sum(pygame.key.get_pressed()) <= 1:
            car.sprite.drive_state = False
            car.sprite.direction = 0
        #DRIVE
        if user_input[pygame.K_UP]:
            car.sprite.drive_state = True
        
        #STEER
        if user_input[pygame.K_RIGHT]:
            car.sprite.direction = 1
        if user_input[pygame.K_LEFT]:
            car.sprite.direction = -1
        
        #UPDATE
        car.draw(window)
        car.update()
        pygame.display.update()

eval_genomes()

