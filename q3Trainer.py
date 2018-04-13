from __future__ import print_function
import os,sys, subprocess,argparse,time
import neat
import atexit
import numpy as np
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u

pOpens = []
def exit_handler():
    print('Killing off subprocesses')
    for p in pOpens:
        p.kill()

atexit.register(exit_handler)

# RUNNING

def TrainingRun(_pipeName,_population,_config):
    pausing = False
    #READING
    pipeOut = open(pipeName,'r')
    data = pipeOut.read()
    if len(data) >0:
        q3Data = q3u.ConvertPipeDataToFloatList(data)
    #Decide when to break
    #if something:
    #    pausing = True
    #    break
    #
    pipeOut.close()
    neatString = ""
    if len(data) >0:
        NNOutputs = q3n.Activate_Genomes(_population,q3Data, _config)
        neatString = q3u.ConvertNEATDataToString(NNOutputs)
    
    #WRITE TO Q3
    pipeIn = open(pipeName,'w',1)
    pipeIn.write(neatString)
    pipeIn.close()
    return pausing


parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='/home/rbons/pipes/pipe', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--init',action='store_true',help="Initiliaze training(remove previous NNs)")
parser.add_argument('--sPath',type=str,default="../ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-s','--servers',type=int, default=1,help="Numbers of server instances")
parser.add_argument('-t','--speed',type=float, default=10.0,help="Speed/timescale of each server")
parser.add_argument('-g','--gLength',type=int, default=180,help="Length of each generation in seconds")

args = parser.parse_args()
params = (args.sPath,"+exec","server.cfg","+exec","levels.cfg","+exec","bots.cfg")


#INITIALIZATION
pausing = False
pipeName = args.pipePath
q3u.CreatePipe(pipeName)
population, config = q3n.Initialize(args.configPath)


#Open servers
for i in range(args.servers):
    pOpens.append(subprocess.Popen(params))

# MAIN
while True:
    if not pausing:
        pausing = TrainingRun(pipeName,population, config)
    else:
        pausing = q3n.RunNEAT(population,fitnessParams,config)

if __name__ == '__main__':
    popen.wait()






