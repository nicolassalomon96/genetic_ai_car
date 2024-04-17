import os
import sys
import math
import pygame
import neat
#from utils import scale_image
from car_ai import Car
import pickle

track_number = 2
track = pygame.image.load(rf'images\track_{track_number}.png')
red_car = pygame.image.load(r'images\car_f1.png')

width, height = track.get_width(), track.get_height()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("GENETIC AI CAR")


def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)


def eval_genomes(genomes, config):
    global cars, ge, nets

    cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car(red_car, window, track_number)))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #run = False #End the generation when closing the window 
                quit() #End the program when closing the window

        window.blit(track, (0,0))

        if len(cars) == 0:
            break

        #Update distance traveled and fitness or remove the car
        for i, car in enumerate(cars):
            
            car.sprite.update_distance_traveled()
            #print(car.sprite.distance_travelled)

            ge[i].fitness += (1 + car.sprite.distance_travelled*0.01) #Consider time and distance travelled by the car adjusted by a factor of 0.01
            #ge[i].fitness += 1 #Only consider time metric
            
            if car.sprite.crashed:
                remove(i)
                

        for i, car in enumerate(cars):
            
            #Try to use 2 outputs: (left or right) and throttle
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.5:
                car.sprite.direction = 1
            elif output[0] < -0.5:
                car.sprite.direction = -1
            elif output[0] <= 0.5 and output[0] >= -0.5:
                car.sprite.direction = 0
            
            car.sprite.car_velocity = ((output[1] + 1) / 2) * car.sprite.max_car_velocity #output[1] scaled from tanh to [0, 6]
            if car.sprite.car_velocity == 0:
                ge[i].fitness = 0
                remove(i)
            #print(car.sprite.car_velocity)

            '''
            #Original using only 2 output (left, right) and a constant throttle
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
            

            #Try to use 3 outputs: left, right and throttle
            output = nets[i].activate(car.sprite.data())
            #print(output)

            output_vel_scaled = ((output[2] + 1) / 2) * 6
            print(output_vel_scaled)


            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
            if output[2] > 0:
                car.sprite.car_velocity = output_vel_scaled #output[2]
            else:
                car.sprite.car_velocity = 1
            '''

        #UPDATE
        for car in cars:
            car.draw(window)
            car.update()
        pygame.display.update()

#Setup NEAT Neural Network
def run(config_path, resume=False):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    if resume:
        pop = neat.Checkpointer.restore_checkpoint(r'checkpoints\neat-checkpoint-4')
    else:
        pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(1, filename_prefix=r'checkpoints\neat-checkpoint-'))

    winner = pop.run(eval_genomes, 50)
    with open("best.pickel", "wb") as f:
        pickle.dump(winner, f)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    run(config_path, resume=False)

