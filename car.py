import pygame
import math

car_velocity = 4
car_downscaling = 0.025

class Car(pygame.sprite.Sprite):
    def __init__(self, car, window):
        super().__init__()
        self.window = window
        self.original_car = car
        self.image = self.original_car
        self.rect = self.image.get_rect(center=(425, 460))
        self.drive_state = False
        self.velocity_vector = pygame.math.Vector2(0.7, 0) #velocidad en la dirección x e y
        self.steering_angle = 0
        self.rotation_velocity = 5
        self.direction = 0 #-1 cuando giramos a la izquierda y 1 al girar a la derecha

    def update(self):
        self.drive()
        self.rotate()
        self.radar()
    

    def drive(self):
        if self.drive_state:
            self.rect.center += self.velocity_vector * car_velocity
    
    def rotate(self):
        if self.direction == 1:
            self.steering_angle -= self.rotation_velocity
            self.velocity_vector.rotate_ip(self.rotation_velocity)
        if self.direction == -1:
            self.steering_angle += self.rotation_velocity
            self.velocity_vector.rotate_ip(-self.rotation_velocity)
        
        self.image = pygame.transform.rotozoom(self.original_car, self.steering_angle, car_downscaling)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self):
        lenght = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])
        print(x, y)
        while not self.window.get_at((x,y)) == pygame.Color(0,0,0) and lenght < 200:
            lenght += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.steering_angle)) * lenght)
            y = int(self.rect.center[1] - math.sin(math.radians(self.steering_angle)) * lenght)

        #DRAW RADAR
        pygame.draw.line(self.window, (255,255,255,255), self.rect.center, (x, y), 1)
        pygame.draw.circle(self.window, (0, 255, 0, 0), (x, y), 3)
