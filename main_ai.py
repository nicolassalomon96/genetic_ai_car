import os
import pygame
import neat
import visualize
from car_ai import Car
import pickle
import argparse

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
        #print(f'Genome: {genome}')
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #run = False #End the generation when closing the window 
                best = pop.best_genome #Ver como guardar los pesos al cerrar la ventana
                with open("best.pickle", "wb") as f:
                    pickle.dump(best, f)
                #print(f'Best saved: {best}')
                quit() #End the program when closing the window

        window.blit(track, (0,0))

        if len(cars) == 0:
            #Si da 2 vueltas vel --> 0 y bandera de que llegó
            #Si choca vel --> 0 y bandera que chocó
            break
            
        #distance_fitness = [0]*len(cars)
        #Update distance traveled and fitness or remove the car
        for i, car in enumerate(cars):
            
            #car.sprite.update_distance_traveled()
            #print(car.sprite.distance_travelled)
            #distance_fitness[i] += car.sprite.distance_travelled
            #if distance_fitness[i] % 30 == 0:
                #ge[i].fitness += (1 + car.sprite.distance_travelled*0.01) #Consider time and distance travelled by the car adjusted by a factor of 0.01
            #    ge[i].fitness *= 2
            #else:
            #    ge[i].fitness += 1
            
            if car.sprite.crashed:
                car.sprite.car_velocity = 0
                #ge[i].fitness = ge[i].fitness
                #remove(i)
            #elif car.llego_linea_final:
                #Si llega la meta car.sprite.car_velocity == 0 y fitness*2
                #pass
            else:
                ge[i].fitness += 1 #Only consider time metric. Ver de multiplicar por la ""inversa"" de la cantidad de pesos (mas pesos, menos fitness)
                

        for i, car in enumerate(cars):
            
            #Try to use 2 outputs: (left or right) and throttle. CHANGE line in Car.drive() method
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.5:
                car.sprite.direction = 1
            elif output[0] < -0.5:
                car.sprite.direction = -1
            elif output[0] <= 0.5 and output[0] >= -0.5:
                car.sprite.direction = 0
            
            if not car.sprite.crashed:
                car.sprite.car_velocity = ((output[1] + 1) / 2) * car.sprite.max_car_velocity #output[1] scaled from tanh to [0, max_car_velocity]
            #if car.sprite.car_velocity == 0:
                #Remove car when it stops
                #ge[i].fitness = 0
            #    remove(i)
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
def train(config_path, resume=False, resume_path=r'checkpoints\neat-checkpoint-4'):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    if resume:
        pop = neat.Checkpointer.restore_checkpoint(resume_path)
    else:
        pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(1, filename_prefix=r'checkpoints\neat-checkpoint-'))

    best = pop.run(eval_genomes, 50)
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)
    #print(winner)

def test(config_path):
    with open("best.pickle", "rb") as f:
        best = pickle.load(f)
    #print(best)
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    #Function to visualize the loaded net
    visualize.draw_net(config, best, True, filename='test_net')

    car = pygame.sprite.GroupSingle(Car(red_car, window, track_number))
    net = neat.nn.FeedForwardNetwork.create(best, config)
       
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False #End the generation when closing the window

        window.blit(track, (0,0))

        if len(car) == 0:
            break

        if car.sprite.crashed:
            break
                
        '''
        #Try to use 2 outputs: (left or right) and throttle
        output = nets[i].activate(car.sprite.data())
        if output[0] > 0.5:
            car.sprite.direction = 1
        elif output[0] < -0.5:
            car.sprite.direction = -1
        elif output[0] <= 0.5 and output[0] >= -0.5:
            car.sprite.direction = 0
        
        car.sprite.car_velocity = ((output[1] + 1) / 2) * car.sprite.max_car_velocity #output[1] scaled from tanh to [0, max_car_velocity]
        if car.sprite.car_velocity == 0:
            #Remove car when it stops
            #ge[i].fitness = 0
            remove(i)
        #print(car.sprite.car_velocity)

        '''
        #Original using only 2 output (left, right) and a constant throttle
        output = net.activate(car.sprite.data())
        if output[0] > 0.7:
            car.sprite.direction = 1
        if output[1] > 0.7:
            car.sprite.direction = -1
        if output[0] <= 0.7 and output[1] <= 0.7:
            car.sprite.direction = 0
        
        #UPDATE
        car.draw(window)
        car.update()
        pygame.display.update()



if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')

    parser = argparse.ArgumentParser()
    parser.add_argument('track', type=int, help ='Select the track: 1 - 5')
    parser.add_argument('type', type=str, help = 'Train or Test mode')
    args = parser.parse_args()

    ############################### GAME WINDOW ##############################
    track_number = args.track 
    track = pygame.image.load(rf'images\track_{track_number}.png')
    red_car = pygame.image.load(r'images\car_f1.png')

    width, height = track.get_width(), track.get_height()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("GENETIC AI CAR")

    if args.type == 'train':
        train(config_path, resume=False)
    elif args.type == 'test':
        test(config_path)
