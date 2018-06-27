import neat
import q3Genome
import q3Utilities as q3u
from neat.six_util import iteritems, itervalues

def Initialize(config_file):
    c = neat.Config(q3Genome.QuakeGenome, neat.DefaultReproduction, 
			 neat.DefaultSpeciesSet, neat.DefaultStagnation,
		         config_file)

    p = neat.Population(c)
    return p, c

def Eval_Genomes(genomes, fitnessParams, config):
    for genome, p in zip(genomes,fintessParams):
        genome.evaluateGenome(p)

def Activate_Genomes(pop,inputValues,config,pipeNumber):
    outputList = []
    for _input, genome in zip(inputValues, itervalues(pop.population)): 
        outputList.append(genome.activate(tuple(_input),config,pipeNumber))
    return outputList

def RunNEAT(pop,fitnessParams,config):
    # Get varibles out of object
    # Evaluate fitness for each genome based on custom fitness function
    Eval_Genomes(list(iteritems(pop.population)),fitnessParams,config)
    # Gather and report statistics.
    best = None
    for genomes in itervalues(pop.population):
        if best is None or genomes.fitness > best.fitness:
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
