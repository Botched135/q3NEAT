from __future__ import print_function
import os,sys, subprocess,argparse,time
import shlex 
import neat
import atexit
import numpy as np
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u
import q3Visualize as q3v

pOpens = []
pipeNames = []
iterations = 0

def exit_handler():
    print('Killing off subprocesses')
    for p in pOpens:
        p.kill()
    print('Deleting pipes')
    for pipe in pipeNames:
        os.remove(pipe)

atexit.register(exit_handler)


parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--init',action='store_true',help="Initiliaze training(remove previous NNs)")
parser.add_argument('--sPath',type=str,default="../ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-s','--servers',type=int, default=2,help="Numbers of server instances")
parser.add_argument('-a','--agents',type=int, default=1,help="Numbers of agents per server instance")
parser.add_argument('-t','--speed',type=float, default=5.0,help="Speed/timescale of each server")
parser.add_argument('-g','--gLength',type=int, default=180,help="Length of each generation in seconds")
parser.add_argument('-d',type=int,default=0, help="Dry run (no training)")
parser.add_argument('-checkpoint',type=str,help="Path to checkpoint to start from")

args = parser.parse_args()


#INITIALIZATIONimUnboundLocalError
pausing = False

pipeNames = q3u.SetupPipes(args.servers,args.pipePath)
population, config = q3n.Initialize(args.configPath)
populationDict = population.population
if not args.init and args.checkpoint is not None:
    population = neat.restore_checkpoint(args.checkpoint)
#Indexer array
keyIter = iter(populationDict.keys())
#indicers = np.zeros([args.servers,args.agents],dtype=int)

#assert(indicers.size == config.pop_size),("Indicers size is {0}, but should be {1}").format(indicers.size,config.pop_size)

#for indexer in np.nditer(indicers, op_flags=['writeonly']):
 #   indexer[...] = next(keyIter)

#Open servers
for pipePath in pipeNames:
    _pipe = '+pipe={0}'.format(pipePath);
    params = ("xterm","-hold","-e",args.sPath,"+exec","server.cfg","+exec","levels.cfg","+exec","bots.cfg",_pipe)
    pOpens.append(subprocess.Popen(params))

#Setup NEAT-reporter
#Parameter is whether or not to show speices details
population.add_reporter(neat.StdOutReporter(True))
#Parameters is generations or seconds
population.add_reporter(neat.Checkpointer(25, 900,filename_prefix='checkpoints/quake3-checkpoint-'))
stats = neat.StatisticsReporter()
population.add_reporter(stats)



# MAIN
if(args.d == 0):
    while True: #population.generation < 51:
            pausing = (True if (iterations > 1000) else False)
            q3n.TrainingRun(pipeNames,populationDict, config,pausing)
            iterations+=1
            if pausing == True:
                done = q3n.RunNEAT(population,config)
                populationDict = population.population
                keyIter = iter(populationDict.keys())

                #for indexer in np.nditer(indicers, op_flags=['writeonly']):
                    #indexer[...] = next(keyIter)
                
                iterations = 0
                #Some kind of break here
               

    q3v.plot_stats(stats, ylog=True, view=True,filename='visualizations/q3-fitness.svg')
    q3v.plot_species(stats, view = True, filename = 'visualizations/q3-species.svg')

    #node_names={} draw winner 
    #visualize.draw_net


if __name__ == '__main__':
    pOpens[0].wait()






