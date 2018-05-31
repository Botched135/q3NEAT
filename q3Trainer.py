from __future__ import print_function
import os,sys, subprocess,argparse,time
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

atexit.register(exit_handler)

# RUNNING

def TrainingRun(_pipeNames,_population,_config):
    pausing = False
    global iterations

    pausingStr = ('p' if (iterations > 200) else 'n')
    for _pipeName in _pipeNames:
        #Check if ready
        pipeIn = open(_pipeName,'r')
        pipeIn.read()
        pipeIn.close()
        #WRITE PAUSING
    
        pipeOut = open(_pipeName,'w',1)
        pipeOut.write(pausingStr)
        pipeOut.close()

        '''
        if pausing:
            pipeOut = open(_pipeName,'r')
            fitnessData = pipeOut.read()
            if len(fitnessData) >0:
                fitnessList = q3u.ConvertPipeDataToFloatList(fitnessData)
            iterations = 0
            continue
        
        #READING
        pipeOut = open(_pipeName,'r')
        data = pipeOut.read()
        pipeOut.close()

        if len(data) >0:
            q3Data = q3u.ConvertPipeDataToFloatList(data)
            print(q3Data)
        #Decide when to break
        #if something:
        #    pausing = True
        #    break
        #
    
    
        neatString = ""
        if len(data) >0:
            NNOutputs = q3n.Activate_Genomes(_population,q3Data, _config)
            neatString = q3u.ConvertNEATDataToString(NNOutputs)
     
        #print(neatString)
        #WRITE TO Q3
        pipeIn = open(pipeName,'w',1)
        pipeIn.write(neatString)
        pipeIn.close()'''
    iterations +=1;
    return pausing


parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--init',action='store_true',help="Initiliaze training(remove previous NNs)")
parser.add_argument('--sPath',type=str,default="../ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-s','--servers',type=int, default=1,help="Numbers of server instances")
parser.add_argument('-t','--speed',type=float, default=10.0,help="Speed/timescale of each server")
parser.add_argument('-g','--gLength',type=int, default=180,help="Length of each generation in seconds")
parser.add_argument('-d',type=int,default=0, help="Dry run (no training)")

args = parser.parse_args()


#INITIALIZATIONimUnboundLocalError
pausing = False
pipeNames = q3u.SetupPipes(args.servers,args.pipePath)
population, config = q3n.Initialize(args.configPath)


#Open servers
for pipePath in pipeNames:
    _pipe = '+pipe={0}'.format(pipePath);
    params = (args.sPath,"+exec","server.cfg","+exec","levels.cfg","+exec","bots.cfg",_pipe)
    print(params);
    pOpens.append(subprocess.Popen(params))


# MAIN
if(args.d == 0):
    while True:
            # if not pausing:
                #Re-think the pausing
            pausing = TrainingRun(pipeNames,population, config)
            #else:
             #   pausing = q3n.RunNEAT(population,fitnessParams,config)

if __name__ == '__main__':
    pOpens[0].wait()






