import pygame
import math
import sys
class Car(pygame.sprite.Sprite):
    def __init__(self, car, window, track_number):
        super().__init__()
        self.window = window
        self.width = self.window.get_width()
        self.height = self.window.get_height()
        self.original_car = car
        self.image = self.original_car
        self.max_car_velocity = 6
        self.car_velocity = 0.01
        self.car_downscaling = 0.025 #Downscaling factor to show the car on the track

        #Rotate and place the car according to track finish line orientation
        if track_number == 1:
            self.init_pos = (536, 553)
            self.finish_line_crossed_threshold = [(-40, -20), (-50, 50)]
            self.rect = self.image.get_rect(center=self.init_pos)
            self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
            self.steering_angle = 0
        elif track_number == 2 or track_number == 6 or track_number == 7:
            self.init_pos = (195, 263)
            self.finish_line_crossed_threshold = [(-50, 50), (0, 15)]
            self.rect = self.image.get_rect(center=self.init_pos)
            self.velocity_vector = pygame.math.Vector2(0, -0.7) #x and y velocity
            self.steering_angle = 90
        elif track_number == 3:
            self.init_pos = (506,840)
            self.finish_line_crossed_threshold = [(-20, 0), (-50, 50)]
            self.rect = self.image.get_rect(center=self.init_pos)
            self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
            self.steering_angle = 0
        elif track_number == 4:
            self.init_pos = (318, 81)
            self.finish_line_crossed_threshold = [(-20, 0), (-50, 50)]
            self.rect = self.image.get_rect(center=self.init_pos)
            self.velocity_vector = pygame.math.Vector2(0.7, 0) #x and y velocity
            self.steering_angle = 0
        elif track_number == 5:
            self.init_pos = (78, 302)
            self.finish_line_crossed_threshold = [(-50, 50), (10, 25)]
            self.rect = self.image.get_rect(center=self.init_pos)
            self.velocity_vector = pygame.math.Vector2(0, -0.7) #x and y velocity
            self.steering_angle = 90

        self.rotation_velocity = 6
        self.direction = 0 # Turn left: -1; Turn right: 1
        self.radar_angles = (-60, -30, 0, 30, 60) #(-120, -90, -45, 0, 45, 90, 120) #(-120, -45, 0, 45, 120)#(-60, -30, 0, 30, 60)#(-90, -45, 0, 45, 90)
        self.radars_data = []
        self.crashed = False #Flag to measure if the car has crashed
        self.laps_counter = 0
        self.completed_lap = False
        self.lap_counter_flag = True #Flag to allow lap_counter used to avoid false positives during finish line detection
        self.active_radar = True #Flag to activate or not the radar measurement

        #Atributtes used for travelled distance calculation
        self.distance_travelled = 0
        self.prev_pos_x = int(self.rect.center[0])
        self.prev_pos_y =  int(self.rect.center[1])

    def reset(self):
        self.completed_lap = False
        self.radars_data.clear() #Clean radars data   
    
    def update(self):
        #Update the state of each car every loop
        self.reset()
        self.drive() 
        self.rotate() 
        for radar_angle in self.radar_angles:
            self.radar(radar_angle, active=self.active_radar) 
        self.collision()       
        self.lap_counter()
        self.update_distance_traveled()
        self.data() 

    def drive(self):
        #self.rect.center += self.velocity_vector * self.max_car_velocity
        self.rect.center += self.velocity_vector * self.car_velocity
    
    def collision(self):
        if not self.crashed:
            '''
            #Detect when two points of the car collide with the track border (it must be black [0,0,0]) OR complete a lap (collide with finish line)
            length = 22 #Distance between the center of the car and the car collision point
            collision_angle = 18 #Angle from the center of the car to the car collision point
            front_right_collition_point = [int(self.rect.center[0] + math.cos(math.radians(self.steering_angle + collision_angle)) * length),
                                    int(self.rect.center[1] - math.sin(math.radians(self.steering_angle + collision_angle)) * length)]
            front_left_collition_point = [int(self.rect.center[0] + math.cos(math.radians(self.steering_angle - collision_angle)) * length),
                                    int(self.rect.center[1] - math.sin(math.radians(self.steering_angle - collision_angle)) * length)]

            back_right_collition_point_2 = [int(self.rect.center[0] - math.cos(math.radians(self.steering_angle + collision_angle)) * length),
                                    int(self.rect.center[1] + math.sin(math.radians(self.steering_angle + collision_angle)) * length)]
            back_left_collition_point_2 = [int(self.rect.center[0] - math.cos(math.radians(self.steering_angle - collision_angle)) * length),
                                    int(self.rect.center[1] + math.sin(math.radians(self.steering_angle - collision_angle)) * length)]
            center_collition_point = self.rect.center

            try:
                if self.window.get_at(front_right_collition_point) == pygame.Color(0,0,0) or self.window.get_at(front_left_collition_point) == pygame.Color(0,0,0) \
                    or self.window.get_at(back_right_collition_point_2) == pygame.Color(0,0,0) or self.window.get_at(back_left_collition_point_2) == pygame.Color(0,0,0) \
                    or center_collition_point == pygame.Color(0,0,0):
                    self.crashed = True
                    #print("The car crashed")
            except:
                #print("Error: car outside of playing area")
                self.crashed = True
                
            #Draw collision points
            #pygame.draw.circle(self.window, (0, 255, 255, 0), right_collition_point_2, 3)
            #pygame.draw.circle(self.window, (0, 255, 255, 0), left_collition_point_2, 3)
        
            '''

            for [_, distance] in self.radars_data:
                if distance < 5:
                    self.crashed = True


    def lap_counter(self):
            car_pos = self.rect.center
            if (self.init_pos[0]+self.finish_line_crossed_threshold[0][0] < car_pos[0] < self.init_pos[0]+self.finish_line_crossed_threshold[0][1]) \
                    and (self.init_pos[1]+self.finish_line_crossed_threshold[1][0] < car_pos[1] < self.init_pos[1]+self.finish_line_crossed_threshold[1][1]):
                if self.lap_counter_flag:
                    self.completed_lap = True
                    self.laps_counter += 1
                    self.lap_counter_flag = False
            else:
                self.lap_counter_flag = True

            #pygame.draw.line(self.window, (0,0,0,255), [int(self.init_pos[0]+self.finish_line_crossed_threshold[0][0]), int(self.init_pos[1]+self.finish_line_crossed_threshold[1][0])],
            #                [int(self.init_pos[0]+self.finish_line_crossed_threshold[0][1]), int(self.init_pos[1]+self.finish_line_crossed_threshold[1][1])])

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

    def radar(self, radar_angle, active=True):
        if active:
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
    
    def data(self):
        input = [0] * len(self.radar_angles) #[0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars_data):
            input[i] = int(radar[1])
        return input

    def update_distance_traveled(self):
        self.distance_travelled += int(math.sqrt((self.prev_pos_x - self.rect.center[0])**2 + (self.prev_pos_y - self.rect.center[1])**2))
        self.prev_pos_x = self.rect.center[0]
        self.prev_pos_y = self.rect.center[1]

