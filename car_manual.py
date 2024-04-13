import pygame
import math

class Car(pygame.sprite.Sprite):
    def __init__(self, car, window, track_number):
        super().__init__()
        self.window = window
        self.width = self.window.get_width()
        self.height = self.window.get_height()
        self.original_car = car
        self.image = self.original_car
        self.car_velocity = 4
        self.car_downscaling = 0.025 #Downscaling factor to show the car on the track
        self.drive_state = False

        #Rotate and place the car according to track finish line orientation
        if track_number == 1: 
            self.rect = self.image.get_rect(center=(516, 553))
            self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
            self.steering_angle = 0
        elif track_number == 2:
            self.rect = self.image.get_rect(center=(195, 263))
            self.velocity_vector = pygame.math.Vector2(0, -0.7) #x and y velocity
            self.steering_angle = 90
        elif track_number == 3:
            self.rect = self.image.get_rect(center=(506,840))
            self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
            self.steering_angle = 0
        elif track_number == 4:
            self.rect = self.image.get_rect(center=(318, 81))
            self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
            self.steering_angle = 0
        elif track_number == 5:
            self.rect = self.image.get_rect(center=(78, 302))
            self.velocity_vector = pygame.math.Vector2(0, -0.7) #x and y velocity
            self.steering_angle = 90

        self.rotation_velocity = 3
        self.direction = 0 # Turn left: -1; Turn right: 1
        self.radar_angles = (-90, -45, 0, 45, 90)
        self.radars_data = []
        self.crashed = False

    def update(self):
        #Update the state of each car every loop
        self.radars_data.clear() #Clean radars data
        self.drive() 
        self.rotate() 
        for radar_angle in self.radar_angles:
            self.radar(radar_angle) 
        self.collision() 
        
        #print(self.radars_data)
        #print("NEW UPDATE")    

    def drive(self):
        #Allow driving the car when self.drive_state is set to True.
        #Moves the center of the car a certain amount of pixels according to velocity_vector and car_velocity
        if self.drive_state:
            self.rect.center += self.velocity_vector * self.car_velocity
    
    def collision(self):
        #Detect when two points of the car collide with the track border (it must be black [0,0,0])
        length = 22 #Distance between the center of the car and the car collision point
        collision_angle = 18 #Angle from the center of the car to the car collision point
        right_collition_point = [int(self.rect.center[0] + math.cos(math.radians(self.steering_angle + collision_angle)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.steering_angle + collision_angle)) * length)]
        left_collition_point = [int(self.rect.center[0] + math.cos(math.radians(self.steering_angle - collision_angle)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.steering_angle - collision_angle)) * length)]

        try:
            if self.window.get_at(right_collition_point) == pygame.Color(0,0,0) or self.window.get_at(left_collition_point) == pygame.Color(0,0,0):
                self.crashed = True
                print("The car crashed")
        except:
            print("Error: car outside of playing area")
        
        #Draw collision points
        pygame.draw.circle(self.window, (0, 255, 255, 0), right_collition_point, 3)
        pygame.draw.circle(self.window, (0, 255, 255, 0), left_collition_point, 3)


    def rotate(self):
        #Rotate the car according to self.direction
        # maybe steering angle can be controled by self.rotation_velocity, if it is positive "self.steering_angle -= self.rotation_velocity" otherwise "self.steering_angle += self.rotation_velocity"
        if self.direction == 1:
            self.steering_angle -= self.rotation_velocity
            self.velocity_vector.rotate_ip(self.rotation_velocity)
        if self.direction == -1:
            self.steering_angle += self.rotation_velocity
            self.velocity_vector.rotate_ip(-self.rotation_velocity)
        
        self.image = pygame.transform.rotozoom(self.original_car, self.steering_angle, self.car_downscaling) #Image rotation
        self.rect = self.image.get_rect(center=self.rect.center) #Update car rectangle center

    def radar(self, radar_angle):
        #Get each radar measurements with a simple ray-cast algorithm    
        lenght = 0 #Step to the object
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
        
        #distance = lenght
        distance = int(math.sqrt((x - self.rect.center[0])**2 + (y - self.rect.center[1])**2))
        self.radars_data.append([radar_angle, distance])
        
        #Draw radar lines
        pygame.draw.line(self.window, (255,255,255,255), self.rect.center, (x, y), 1)
        pygame.draw.circle(self.window, (0, 255, 0, 0), (x, y), 3)
        
        return distance