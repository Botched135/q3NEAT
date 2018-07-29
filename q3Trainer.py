from __future__ import print_function
import os,sys, subprocess,argparse,time
import shlex 
import neat
import atexit
import numpy as np
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u

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

# RUNNING

def TrainingRun(_pipeNames,_population,_config,pausing):
    resList = []
    pausingStr = 'p' if pausing else 'n'
    populationIterator = iter(_population.values())
    for pipeName in _pipeNames:
        
        # CHECK IF READY
        pipeIn = open(pipeName,'r')
        pipeIn.read()
        pipeIn.close()
        
        # WRITE PAUSING
        pipeOut = open(pipeName,'w')
        pipeOut.write(pausingStr)
        pipeOut.close()
        
        # READ FITNESS
        if pausing == True:
            pipeOut = open(pipeName,'r')
            fitnessData = pipeOut.read()
            fitnessList = 0
            #if len(fitnessData) >0:
                #fitnessList = q3u.ConvertPipeDataToFloatList(fitnessData)
            q3n.Eval_Genomes(populationIterator,fitnessList,_config)
            pipeOut.close()
            continue;

        
        #READING STATES
        pipeIn = open(pipeName,'r')
        botState = pipeIn.read()
        pipeIn.close()

        if len(botState) >0:
            q3Data = q3u.ConvertPipeDataToFloatList(botState)

       
        # RUN STATES THROUGH THE GENOMES
        neatString = ""
        if len(botState) >0:
            NNOutputs = q3n.Activate_Genomes(populationIterator,q3Data,_config)
            neatString = q3u.ConvertNEATDataToString(NNOutputs)
     
        # WRITE TO Q3
        pipeOut = open(pipeName,'w')
        pipeOut.write(neatString)
        pipeOut.close()
   

parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--init',action='store_true',help="Initiliaze training(remove previous NNs)")
parser.add_argument('--sPath',type=str,default="../ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-s','--servers',type=int, default=2,help="Numbers of server instances")
parser.add_argument('-a','--agents',type=int, default=4,help="Numbers of agents per server instance")
parser.add_argument('-t','--speed',type=float, default=5.0,help="Speed/timescale of each server")
parser.add_argument('-g','--gLength',type=int, default=180,help="Length of each generation in seconds")
parser.add_argument('-d',type=int,default=0, help="Dry run (no training)")

args = parser.parse_args()


#INITIALIZATIONimUnboundLocalError
pausing = False
pipeNames = q3u.SetupPipes(args.servers,args.pipePath)
population, config = q3n.Initialize(args.configPath)
populationDict = population.population
#Indexer array
keyIter = iter(populationDict.keys())
indicers = np.zeros([args.servers,args.agents],dtype=int)

assert(indicers.size == config.pop_size),("Indicers size is {0}, but should be {1}").format(indicers.size,config.pop_size)

for indexer in np.nditer(indicers, op_flags=['writeonly']):
    indexer[...] = next(keyIter)

#Open servers
for pipePath in pipeNames:
    _pipe = '+pipe={0}'.format(pipePath);
    params = ("xterm","-hold","-e",args.sPath,"+exec","server.cfg","+exec","levels.cfg","+exec","bots.cfg",_pipe)
    print(params)
    pOpens.append(subprocess.Popen(params))


# MAIN
if(args.d == 0):
    while True:
            pausing = (True if (iterations > 20) else False)
            TrainingRun(pipeNames,populationDict, config,pausing)
            iterations+=1
            if pausing == True:
                populationDict = population.population
                done = q3n.RunNEAT(population,config)
                populationDict = population.population
                keyIter = iter(populationDict.keys())

                for indexer in np.nditer(indicers, op_flags=['writeonly']):
                    indexer[...] = next(keyIter)
                
                iterations = 0
                print("do we get here?")

if __name__ == '__main__':
    pOpens[0].wait()






