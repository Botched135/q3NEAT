from __future__ import print_function
import os,sys, subprocess,argparse,time
import neat
import atexit
import numpy as np
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u
import q3Visualize as q3v
import copy

pOpens = []
pipeNames = []
iterations = 0
prevPop = None

parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--init',action='store_true',help="Initialize training(start with new population)")
parser.add_argument('--sPath',type=str,default="../debug/ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-s','--servers',type=int, default=2,help="Numbers of server instances")
parser.add_argument('-a','--agents',type=int, default=4,help="Numbers of agents per server instance")
parser.add_argument('-t','--speed',type=float, default=5.0,help="Speed/timescale of each server")
parser.add_argument('-g','--gLength',type=int, default=180,help="Length of each generation in seconds")
parser.add_argument('-d','--dry', action='store_true', help="Dry run (no training)")
parser.add_argument('--checkpoint',type=str,help="Path to checkpoint for restoring population from disk")
parser.add_argument('-id','--experimentID', type=str, help="Experiment ID used to track iterations")

args = parser.parse_args()

experimentID = args.experimentID
#INITIALIZATIONimUnboundLocalError
pausing = False

pipeNames = q3u.SetupPipes(args.servers,args.pipePath)
cfgPrefix = ""
if args.dry is True:
    cfgPrefix = 'debug'

if args.init is True:
    if args.checkpoint is not None:
        print('Initialization has been set to true. Not restoring from checkpoint!') 
    population, config = q3n.Initialize(args.configPath)
    populationDict = population.population
    keyIter = iter(populationDict.keys())
elif args.checkpoint is not None:
    population = q3n.RestoreFromCheckpoint(args.checkpoint)
    config = population.config
    populationDict = population.population
    keyIter = iter(populationDict.keys())
elif args.dry is False:
    raise Exception('Poplation has neither been loaded from disk or initialized! Exiting now!')

if experimentID is None and args.dry is False:
    raise Exception("No exerpimentID! Exiting now!")
elif args.dry is False:
    if os.path.exists("winnerGenomes/Experiment{0}/".format(experimentID)):
        raise Exception('Experiment ID has already been used! Exiting now!')
#indicers = np.zeros([args.servers,args.agents],dtype=int)

#assert(indicers.size == config.pop_size),("Indicers size is {0}, but should be {1}").format(indicers.size,config.pop_size)

#for indexer in np.nditer(indicers, op_flags=['writeonly']):
 #   indexer[...] = next(keyIter)
#Open servers
for pipePath in pipeNames:
    _pipe = '+pipe={0}'.format(pipePath);
    params = ("xterm","-hold","-e",args.sPath,"+exec","{0}server.cfg".format(cfgPrefix),"+exec","levels.cfg","+exec","{0}bots.cfg".format(cfgPrefix),_pipe)
    pOpens.append(subprocess.Popen(params))

#Setup NEAT-reporter
#Parameter is whether or not to show species details
if args.dry is False:
    population.add_reporter(neat.StdOutReporter(True))
    #Parameters is generations or seconds
    population.add_reporter(neat.Checkpointer(25, 900,filename_prefix='checkpoints/quake3-checkpoint-'))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.reporters.start_generation(population.generation)

def exit_handler():
    print('Killing off subprocesses')
    for p in pOpens:
        p.kill()
    print('Deleting pipes')
    for pipe in pipeNames:
        os.remove(pipe)
    if args.dry is False:
        if population.generation > 5:
            q3n.EndNEAT(prevPop,experimentID,stats,config)

atexit.register(exit_handler)

test = 0
# MAIN
if args.dry is False:
    #So rather than simply using ready for switch a-roo, it will be used to choose if the next generetation should start
    #Example: Bots runs a test --> All Bots are done --> next frame it checks if all the bots are done --> sends note to python to
    while True: #population.generation < 51:
            pausing = (True if (iterations > 900 ) else False)
            q3n.TrainingRun(pipeNames,populationDict, config,pausing)
            iterations+=1
            if pausing == True:

                done, prevPop = q3n.RunNEAT(population,config)
                populationDict = population.population
                keyIter = iter(populationDict.keys())
                iterations = 0
                test +=1
                population.reporters.start_generation(population.generation)
                #Some kind of break here.. Consider using a thread for the trainer to keep the pipe flow

    q3n.EndNEAT(prevPop,experimentID,stats,config)


if __name__ == '__main__':
    pOpens[0].wait()






