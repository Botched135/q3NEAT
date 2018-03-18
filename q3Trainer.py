from __future__ import print_function
import os
import sys
import subprocess
import argparse
import neat
from q3Genome import quakeGenome

parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument('--configPath', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('--init',action='store_true',help="Initiliaze training(remove previous NNs)")
parser.add_argument('--sPath',type=str,default="../ioq3/build/release-linux-x86_64",help="path to the server file")
parser.add_argument('-s','--servers',type=int, default=1,help="Numbers of server instances")
parser.add_argument('-t','--speed',type=float, default=10.0,help="Speed/timescale of each server")
parser.add_argument('-g','--gLength',type=int, default=180,help="Length of each generation in seconds")

args = parser.parse_args()


def initialize(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
			 neat.DefaultSpeciesSet, neat.DefaultStagnation,
		         config_file)

    p = neat.Population(config)




if __name__ == '__main__':
    initialize(args.configPath)
