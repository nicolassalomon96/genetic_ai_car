#AL PRESIONAR LA LETRA 'Q' FINALIZA LA GENERACIÓN, GUARDA EL MEJOR INDIVIDUO Y PASA A LA GENERACIÓN SIGUIENTE

#MEJORAR LA DETECCIÓN DE BORDES PORQUE EN TRACK 4 POR EJEMPLO NO DETECTA BIEN: HAY QUE HACER LOS BORDES MAS GRUESOS Y NEGROS

import os
import pygame
import neat
import visualize
from car_ai import Car
import pickle
import argparse

FPS = 60
pygame.init() 
font = pygame.font.Font(None, 32)
current_gen = 0

def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)

def save_best():
    best = pop.best_genome
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)

def eval_genomes(genomes, config):
    global cars, ge, nets, current_gen, stopped_cars

    cars = []
    ge = []
    nets = []
    fitness = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car(red_car, window, track_number)))
        ge.append(genome)
        #print(f'Genome: {genome}')
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
    clock = pygame.time.Clock()

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

        #When pressing 'q', finish the current generation, save the state into a .pickle and begins a new generation
        keyState = pygame.key.get_pressed()   
        if keyState[pygame.K_q]:
            pygame.time.wait(500)
            current_gen += 1
            run = False
        pygame.event.pump() # process event queue
    
        for i, car in enumerate(cars):
            breaker = False
            if car.sprite.completed_lap:# and car.sprite.stop:
                #car.sprite.crashed = True
                #breaker = True
                #break
            #elif car.sprite.completed_lap:
                ge[i].fitness *= 2
                #pygame.time.wait(100) 
                print(f"Car: {i}, Laps: {car.sprite.laps_counter}")
                if car.sprite.laps_counter == 2:
                    breaker = True
                    break            

            if car.sprite.crashed:
                car.sprite.car_velocity = 0
                car.sprite.direction = 0
                car.sprite.active_radar = False 

            elif car.sprite.car_velocity != 0:
            #else:
                output = nets[i].activate(car.sprite.data())
                if output[0] > 0.5:
                    car.sprite.direction = 1
                elif output[0] < -0.5:
                    car.sprite.direction = -1
                elif output[0] <= 0.5 and output[0] >= -0.5:
                    car.sprite.direction = 0
                
                car.sprite.car_velocity = ((output[1] + 1) / 2) * car.sprite.max_car_velocity #output[1] scaled from tanh to [0, max_car_velocity]
                
                ge[i].fitness += car.sprite.distance_travelled/100  #Only consider time metric. Ver de multiplicar por la ""inversa"" de la cantidad de pesos (mas pesos, menos fitness)
                                                                    #Considering the distance travelled we avoid a car turning around itself and increasing its fitness
                fitness.append(ge[i].fitness)
            else:
                car.sprite.crashed = True
                #car.sprite.active_radar = False 
                #car.sprite.direction = 0
        if breaker:
            current_gen += 1
            break     
        
        #UPDATE
        stopped_cars = 0        
        window.blit(track, (0,0))

        for car in cars:
            car.draw(window)
            car.update()

            if not car.sprite.active_radar:
                stopped_cars += 1

        text_1 = font.render(f'Mode: Train', True, (0,0,0), (255,255,255))
        text_2 = font.render(f'Generation:{current_gen}', True, (0,0,0), (255,255,255))
        text_3 = font.render(f'Alive:{len(cars)-stopped_cars} - Dead:{stopped_cars}', True, (0,0,0), (255,255,255))
        text_4 = font.render(f'Best fitness:{int(max(fitness))}', True, (0,0,0), (255,255,255))
        window.blit(text_1, (int(window.get_width()*0.02), int(window.get_height()*0.75)))
        window.blit(text_2, (int(window.get_width()*0.02), int(window.get_height()*0.79)))
        window.blit(text_3, (int(window.get_width()*0.02), int(window.get_height()*0.83)))
        window.blit(text_4, (int(window.get_width()*0.02), int(window.get_height()*0.87)))
    
        if stopped_cars == len(cars):
            current_gen += 1
            break
       
        save_best()
        pygame.display.update()
        clock.tick(FPS)

#Setup NEAT Neural Network
def train(config_path, resume=False, resume_path=r'checkpoints\neat-checkpoint-12', generations=10):
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

    best = pop.run(eval_genomes, generations)
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
    clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False #End the generation when closing the window
        
        window.blit(track, (0,0))

        if car.sprite.crashed:
            car.sprite.car_velocity = 0
            car.sprite.direction = 0
            #break               
        else:
            #Try to use 2 outputs: (left or right) and throttle
            output = net.activate(car.sprite.data())
            if output[0] > 0.5:
                car.sprite.direction = 1
            elif output[0] < -0.5:
                car.sprite.direction = -1
            elif -0.5 <= output[0] <= 0.5:
                car.sprite.direction = 0
            
            car.sprite.car_velocity = ((output[1] + 1) / 2) * car.sprite.max_car_velocity #output[1] scaled from tanh to [0, max_car_velocity]

        #UPDATE
        car.draw(window)
        car.update()
        
        text_1 = font.render(f'Mode: Test', True, (0,0,0), (255,255,255))
        window.blit(text_1, (20,750))
        pygame.display.update()
        clock.tick(FPS)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')

    parser = argparse.ArgumentParser()
    parser.add_argument('track', type=int, help ='Select the track: 1 - 5')
    parser.add_argument('type', type=str, help = 'Train or Test mode')
    parser.add_argument('--resume', type=str, help = 'Resume from checkpoint')
    parser.add_argument('--generations', type=int, help = 'Number of total generations')
    args = parser.parse_args()

    ############################### GAME WINDOW ##############################
    track_number = args.track 
    track = pygame.image.load(rf'images\track_{track_number}.png')
    red_car = pygame.image.load(r'images\car_f1.png')

    width, height = track.get_width(), track.get_height()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("GENETIC AI CAR")

    if args.type == 'train':
        train(config_path, resume=args.resume, generations=args.generations)
    elif args.type == 'test':
        test(config_path)
