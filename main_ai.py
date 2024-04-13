import os
import sys
import math
import pygame
import neat
#from utils import scale_image
from car_ai import Car

track_number = 1
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
                run = False
        
        window.blit(track, (0,0))

        if len(cars) == 0:
            break
    
        for i, car in enumerate(cars):
            ge[i].fitness += 1
            if car.sprite.crashed:
                remove(i)
        
        for i, car in enumerate(cars):
            '''
            output = nets[i].activate(car.sprite.data())
            if output[0] >= 0.5:
                car.sprite.direction = 1
            elif output[0] <= 0.5:
                car.sprite.direction = -1
            else:
                car.sprite.direction = 0
            
            car.sprite.car_velocity = output[1]
            #print(output)
            '''
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
            '''
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
            if output[2] > 0:
                car.sprite.car_velocity = output[2]
            else:
                car.sprite.car_velocity = 0
            '''
        #UPDATE
        for car in cars:
            car.draw(window)
            car.update()
        pygame.display.update()

#Setup NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    run(config_path)

