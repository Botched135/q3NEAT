from __future__ import print_function
import os
import sys
import subprocess
import argparse
import neat
import atexit
import time
from q3Genome import quakeGenome

def CreatePipe(pipe_name):
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)
        print("Pipe has been created")

def Initialize(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
			 neat.DefaultSpeciesSet, neat.DefaultStagnation,
		         config_file)

    p = neat.Population(config)

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
pipeName = args.pipePath
CreatePipe(pipeName)
Initialize(args.configPath)
popen = subprocess.Popen(params);


#WRITING
while True:
    #READING
    pipe = open(pipeName,'r')
    data = pipe.read()
    print("In Python: %s" % data)
    pipe.close()
    #WRITING
    pipe = open(pipeName,'w')
    pipe.write("From Python")
    pipe.close()
    
#pipe.close()

def exit_handler():
    print('Killing off subprocesses')
    pipe.close();
    popen.kill()



atexit.register(exit_handler)
if __name__ == '__main__':
    popen.wait()






