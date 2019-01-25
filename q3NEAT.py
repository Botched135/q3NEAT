import neat
import pickle
import q3Genome
import q3Utilities as q3u
import q3Visualize as q3v
import time
import datetime
import os
import copy
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
        try:
            genome = next(popIterator)
            genome.evaluateGenome(fitness)
        except StopIteration:
            pass

def Activate_Genomes(popIterator,inputValues,config):
    outputList = []
    for _input in inputValues:
        try:
            genome = next(popIterator)
            outputList.append(genome.activate(tuple(_input[:-1]),config))
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

    combatState = 0
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
    pipeIn.close()

    
    # RUN STATES THROUGH THE GENOMES
    neatString = "error"
    if len(botState) >0:
        q3Data = q3u.ConvertPipeDataToFloatList(botState)
        NNOutputs = genome.activate(tuple(q3Data[0][:-1]),config)
        neatString = q3u.NEATDataToString(NNOutputs)
        combatState = q3Data[0][-1]
        neatString = '1.000,-1.000,-0.600,-1.000,'
        print(neatString)
        print(q3Data)

    # WRITE TO Q3

    pipeOut = open(pipeName,'w')
    pipeOut.write(neatString)
    pipeOut.close()

    return combatState


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
    prevPop = copy.deepcopy(pop)
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

    return True, prevPop

def EndNEAT(pop, experimentID,stats,config):
    winnerID = "Experiment{0}Generation{1}".format(experimentID,pop.generation)
    winnerFolder = "Experiment{0}/".format(experimentID)
    winnerPath = "winnerGenomes/{0}".format(winnerFolder)


    if not os.path.exists(winnerPath):
        os.makedirs(winnerPath)
        os.makedirs("{0}visualizations/".format(winnerPath))

    q3v.plot_stats(stats, ylog=True, view=True,filename='{0}visualizations/q3-fitness{1}.svg'.format(winnerPath,winnerID))
    q3v.plot_species(stats, view = True, filename = '{0}visualizations/q3-species{1}.svg'.format(winnerPath, winnerID))
    node_name = {-1:'wallRadar[1,0]',-2:'wallRadar[0,1]',-3:'enemyRadar[Front-20ø]',
                 -4:'enemyRadar[1st-Right-20ø]', -5:'enemyRadar[1st-Left-20ø]',
                 -6:'enemyRadar[2nd-Right-25ø]', -7:'enemyRadar[2nd-Left-25ø]',
                 -8:'enemyRadar[3rd-Right-30ø]', -9:'enemyRadar[3rd-Left-30ø]',
                 -10:'enemyRadar[4th-Right-40ø]', -11:'enemyRadar[4th-Left-40ø]',
                 -12:'enemyRadar[Back-Right-55ø]', -13:'enemyRadar[Back-Left-55ø]',
                 -14:'OnTarget',
                  0:'Shoot',1:'Move Forward/Backward',2:'Turn left/right', 3:'Negate Turn'}

   

    _species = pop.species.species

    for speciesKey in _species:
        genomes = _species[speciesKey].members
        localBest = None
        localBestPath = ""
        for genomeKey in genomes:
            genome = genomes[genomeKey]
            print(genome.fitness)
            if localBest is None or localBest.fitness < genome.fitness:
                localBest = genome
                
        if(localBest.fitness > 2.0):
            localBestPath = "{0}{2}FitnessSpecie{1}".format(winnerPath,speciesKey,localBest.fitness)

            with open(localBestPath,'wb') as f:
                pickle.dump(localBest,f)
            
            q3v.draw_net(config,localBest,view=True,node_names=node_name,filename="{0}Network".format(localBestPath))


#0:'Shoot',1:'Jump/Crouch',2:'Move Forward/Backward',3:'Move Left/Right',4:'Turn Left/Right'} ,-22:'Health',-23:'TakingDmg'

#-3:'wallRadar[-1,0]',-4:'wallRadar[0,-1]',
         #        -5:'wallRadar[0.7,0.7]',-6:'wallRadar[-0.7,0.7]',-7:'wallRadar[-0.7,-0.7]',-8:'wallRadar[0.7,-0.7]'