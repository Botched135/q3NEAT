import neat
import pickle
import q3Genome
import q3Utilities as q3u
import q3Visualize as q3v
import time
import datetime
from neat.six_util import iteritems, itervalues

class CompleteExtinctionException(Exception):
    pass

def Initialize(config_file):
    c = neat.Config(q3Genome.QuakeGenome, neat.DefaultReproduction, 
			 neat.DefaultSpeciesSet, neat.DefaultStagnation,
		         config_file)

    p = neat.Population(c)
    return p, c

def RestoreFromCheckpoint(checkpoint):
    p = neat.Checkpointer.restore_checkpoint(checkpoint)
    return p

def Eval_Genomes(popIterator, fitnessParams, config):
    for fitness in fitnessParams:
            genome = next(popIterator)
            genome.evaluateGenome(fitness)

def Activate_Genomes(popIterator,inputValues,config):
    outputList = []
    for _input in inputValues:
        try:
            genome = next(popIterator)
            outputList.append(genome.activate(tuple(_input),config))
        except StopIteration:
            pass
    return outputList

def TrainingRun(_pipeNames,_population,_config,pausing):
    resList = []
    pausingStr = 'p' if pausing else 'n'
    populationIterator = iter(_population.values())
    for pipeName in _pipeNames:
        
        # CHECK IF READY
        pipeIn = open(pipeName,'r') #Seems to be problems here
        pipeIn.read()
        pipeIn.close()
        
        # WRITE PAUSING
        pipeOut = open(pipeName,'w')
        pipeOut.write(pausingStr)
        pipeOut.close()
        
        # READ FITNESS
        if pausing == True:
            pipeIn = open(pipeName,'r')
            fitnessData = pipeIn.read()
            pipeIn.close()
            if len(fitnessData) >0:
                fitnessList = q3u.ConvertPipeDataToFloatList(fitnessData)
                Eval_Genomes(populationIterator,fitnessList,_config)
            pipeOut = open(pipeName,'w')
            pipeOut.write("f")
            pipeOut.close()
            continue

        
        #READING STATES
        pipeIn = open(pipeName,'r')
        botState = pipeIn.read()
        pipeIn.close()

        # RUN STATES THROUGH THE GENOMES
        neatString = "error"
        if len(botState) >0:
            q3Data = q3u.ConvertPipeDataToFloatList(botState)
            NNOutputs = Activate_Genomes(populationIterator,q3Data,_config)
            neatString = q3u.ConvertNEATDataListToString(NNOutputs)


        # WRITE TO Q3
        pipeOut = open(pipeName,'w')
        pipeOut.write(neatString)
        pipeOut.close()

def ActivationRun(pipeName,genome,config):
    

    # CHECK IF READY
    pipeIn = open(pipeName,'r')
    pipeIn.read()
    pipeIn.close()

    # NOTE READY
    pipeOut = open(pipeName,'w')
    pipeOut.write('n')
    pipeOut.close()

    # THE GOOD OLD SWITCHAROO

    #READING STATES
    pipeIn = open(pipeName,'r')
    botState = pipeIn.read()
    print("Botstates: "+botState)
    pipeIn.close()

       
    # RUN STATES THROUGH THE GENOMES
    neatString = "error"
    if len(botState) >0:
        q3Data = q3u.ConvertPipeDataToFloatList(botState)
        NNOutputs = genome.activate(tuple(q3Data[0]),config)
        neatString = q3u.NEATDataToString(NNOutputs)

    # WRITE TO Q3
    pipeOut = open(pipeName,'w')
    pipeOut.write(neatString)
    pipeOut.close()


def RunNEAT(pop,config):
    # Get varibles out of object
    # Evaluate fitness for each genome based on custom fitness function
    # Gather and report statistics.
  

    best = None
    for g in iter(pop.population.values()):
        if best is None or g.fitness > best.fitness:
            best = g

    # Consider prining this to some log of a sort 
    pop.reporters.post_evaluate(config, pop.population, pop.species, best)

    # Track the best genome ever seen.
    if pop.best_genome is None or best.fitness > pop.best_genome.fitness:
        pop.best_genome = best

    if not pop.config.no_fitness_termination:
        # End if the fitness threshold is reached.
        fv = pop.fitness_criterion(g.fitness for g in itervalues(pop.population))
        if fv >= pop.config.fitness_threshold:
            pop.reporters.found_solution(config, pop.generation, best)

    # Create the next generation from the current generation.
    pop.population = pop.reproduction.reproduce(config,pop.species,config.pop_size,pop.generation)

     
    # Check for complete extinction.
    if not pop.species.species:
        pop.reporters.complete_extinction()

         # If requested by the user, create a completely new population,
         # otherwise raise an exception.
        if config.reset_on_extinction:
            pop.population = pop.reproduction.create_new(config.genome_type,
                                                      config.genome_config,
                                                      config.pop_size)
        else:
            raise CompleteExtinctionException()
            return False

     # Divide the new population into species.
    pop.species.speciate(config, pop.population, pop.generation)
    pop.reporters.end_generation(config, pop.population, pop.species)

    pop.generation += 1

    return True

def EndNEAT(pop, stats,config):
    winner = pop.best_genome
    q3v.plot_stats(stats, ylog=True, view=True,filename='visualizations/q3-fitness.svg')
    q3v.plot_species(stats, view = True, filename = 'visualizations/q3-species.svg')
    node_name = {-1:'wallRadar[1,0]',-2:'wallRadar[0,1]',-3:'wallRadar[-1,0]',-4:'wallRadar[0,-1]',
                 -5:'wallRadar[0.7,0.7]',-6:'wallRadar[-0.7,0.7]',-7:'wallRadar[-0.7,-0.7]',-8:'wallRadar[0.7,-0.7]',
                 -9:'enemyRadar[RightBack]',-10:'enemyRadar[LeftBack]',-11:'enemyRadar[Right45ø]',-12:'enemyRadar[Left45ø]',
                 -13:'enemyRadar[RightFront20ø]',-14:'enemyRadar[LeftFront20ø]',-15:'enemyRadar[RightFront15ø]',-16:'enemyRadar[LeftFront15ø]',
                 -17:'enemyRadar[RightFront7.5ø]',-18:'enemyRadar[LeftFront7.5ø]',-19:'enemyRadar[RightFront2.5ø]',-20:'enemyRadar[LeftFront2.5ø]',
                 -21:'OnTarget',-22:'TakingDmg',-23:'bias',
                0:'Shoot',1:'Move Forward',2:' Move Backward',3:'Move Left',4:'Move right', 5:'Turn Left',6:'Turn Right'}

    winnerName = "Time{1}WinnerG{0}.gv".format(pop.generation,datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
    winnerPath = "winnerGenomes/{0}".format(winnerName)

    with open(winnerName,'wb') as f:
        pickle.dump(winner,f)

    q3v.draw_net(config,winner,view=True,node_names=node_name,filename=winnerPath)


#0:'Shoot',1:'Jump/Crouch',2:'Move Forward/Backward',3:'Move Left/Right',4:'Turn Left/Right'} ,-22:'Health',-23:'TakingDmg'