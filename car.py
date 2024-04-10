import pygame
import math

car_velocity = 3
car_downscaling = 0.025

class Car(pygame.sprite.Sprite):
    def __init__(self, car, window):
        super().__init__()
        self.window = window
        self.width = self.window.get_width()
        self.height = self.window.get_height()
        self.original_car = car
        self.image = self.original_car
        self.rect = self.image.get_rect(center=(425, 460))
        self.drive_state = False
        self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
        self.steering_angle = 0
        self.rotation_velocity = 2
        self.direction = 0 # Turn left: -1; Turn right: 1
        self.radar_angles = (-90, -45, 0, 45, 90)
        self.radars_data = []
        self.crashed = False

    def update(self):
        self.radars_data.clear()
        self.drive()
        self.rotate()
        for radar_angle in self.radar_angles:
            self.radar(radar_angle)
        self.collision()
        #print(self.radars_data)
        #print("NEW UPDATE")    

    def drive(self):
        if self.drive_state:
            self.rect.center += self.velocity_vector * car_velocity
    
    def collision(self):
        length = 22 #Distance between the center of the car and the collision point
        right_collition_point = [int(self.rect.center[0] + math.cos(math.radians(self.steering_angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.steering_angle + 18)) * length)]
        left_collition_point = [int(self.rect.center[0] + math.cos(math.radians(self.steering_angle - 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.steering_angle - 18)) * length)]
        
        #DIE WHEN COLLISION
        try:
            if self.window.get_at(right_collition_point) == pygame.Color(0,0,0) or self.window.get_at(left_collition_point) == pygame.Color(0,0,0):
                self.crashed = True
                #print(self.crashed)
        except:
            print("Error: car outside of playing area")
        
        #DRAW COLLISION POINT
        pygame.draw.circle(self.window, (0, 255, 255, 0), right_collition_point, 3)
        pygame.draw.circle(self.window, (0, 255, 255, 0), left_collition_point, 3)


    def rotate(self):
        if self.direction == 1:
            self.steering_angle -= self.rotation_velocity
            self.velocity_vector.rotate_ip(self.rotation_velocity)
        if self.direction == -1:
            self.steering_angle += self.rotation_velocity
            self.velocity_vector.rotate_ip(-self.rotation_velocity)
        
        self.image = pygame.transform.rotozoom(self.original_car, self.steering_angle, car_downscaling)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):    
        lenght = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        while (0 < x < self.width) and (0 < y < self.height) and (not self.window.get_at((x,y)) == pygame.Color(0,0,0)): 
            #self.window.get_at((x,y) --> get color pixel (x,y)
            lenght += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.steering_angle + radar_angle)) * lenght)
            y = int(self.rect.center[1] - math.sin(math.radians(self.steering_angle + radar_angle)) * lenght)
      
            #if lenght > 199:
                #Set a max_distance to measure
            #    break
        
        distance = lenght
        #distance = round(math.sqrt((x - self.rect.center[0])**2 + (y - self.rect.center[1])**2),2)
        self.radars_data.append([radar_angle, distance])   
        #DRAW RADAR
        pygame.draw.line(self.window, (255,255,255,255), self.rect.center, (x, y), 1)
        pygame.draw.circle(self.window, (0, 255, 0, 0), (x, y), 3)
        
        return distance