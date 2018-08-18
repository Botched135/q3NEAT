from __future__ import print_function
import os,sys, subprocess,argparse,time
import neat
import atexit
import pickle
import numpy as np
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u

parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--sPath',type=str,default="../debug/ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-g','--genomePath', type=str,help='path to genome that will control the agent')

args = parser.parse_args()

pipeName = q3u.SetupPipes(1,args.pipePath)
pipeName = pipeName[0]

with open(args.genomePath,'rb') as file:
	genome = pickle.load(file)

config = neat.Config(	QuakeGenome, neat.DefaultReproduction, 
					neat.DefaultSpeciesSet, neat.DefaultStagnation, 
					args.configPath)

_pipe = '+pipe={0}'.format(pipeName)
params = ("xterm","-hold","-e",args.sPath,"+exec","runnerServer.cfg","+exec","levels.cfg","+exec","runnerBots.cfg",_pipe)

pOpen = subprocess.Popen(params)

while True:
	q3n.ActivationRun(pipeName,genome,config)

if __name__ == '__main__':
    pOpen.wait()

