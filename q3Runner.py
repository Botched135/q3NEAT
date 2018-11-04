from __future__ import print_function
import os,sys, subprocess,argparse,time
import neat
import atexit
import pickle
import socket
import numpy as np
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u
import q3Affective as q3a
import time


parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('-sPath',type=str,default="../debug/ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-gF','--genomeFolder', type=str, help='path to the folder containing genomes to adapt between')
parser.add_argument('-ag','--activeGenomePath', type=str,help='path to genome that will control the agent initially')
parser.add_argument('--affective',action='store_true', help='Whether or not the affective version should run')
parser.add_argument('--NEAT', action='store_true',help='Whehter to use the NEAT-AI or the built-in bots')
parser.add_argument('--HRBase', type=float, help='Heart Rate (BPM) baseline of the participant')
parser.add_argument('--EDABase', type=float, help='Electrodermal Activity baseline of the participant')
parser.add_argument('--HRVBase', type=float, help='Heart Rate Variability baseline of the participant')
parser.add_argument('-s','--socket',type=str, help='Path to UNIX socket for physiological signals')

args = parser.parse_args()
baselineDict = {}

def NonAffectiveRun(pipeName):
    pipeIn = open(pipeName,'r')
    pipeIn.read()
    pipeIn.close()

    # WRITE IF THERE SHOULD BE UPDATE
    pipeOut = open(pipeName,'w')
    pipeOut.write('1')
    pipeOut.close()


def ResolveCombatCommands(client, previousCombatState,botState):
    res = botState;
    if res == previousCombatState:
        return res;
    if res == 1:
    	client.send(b'combat')
    elif res == 2:
    	client.send(b'end')
    elif res == 3:
        client.send(b'eval')
        affectiveData = client.recv(66600).decode('utf-8')
        q3a.TransformAffectiveData(affectiveData)
    return res


botCfgPrefix = 'nonAdam'
pipeName = q3u.SetupPipes(1,args.pipePath)
pipeName = pipeName[0]

if args.affective is True:
    combat = 0 #Three stages: 0: No change, 1: engaged in combat, 2: Combat ended, 3: Evaluation

    # Baseline dict for parsing onto the affective evaluator
    baselineDict = {'HR' : args.HRBase,'HRV' : args.HRVBase,'EDA' : args.EDABase}

    #UNIX socket client
    socketPath = args.socket
    client= socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    client.connect(socketPath)
    client.send(b'Q3Runner connected')

if args.NEAT is True:
    botCfgPrefix = 'adam'
    with open(args.activeGenomePath,'rb') as file:
        print(file.seek(0))
        genome = pickle.load(file)
        file.close()

    config = neat.Config(QuakeGenome, neat.DefaultReproduction, 
					neat.DefaultSpeciesSet, neat.DefaultStagnation, 
					args.configPath)

_pipe = '+pipe={0}'.format(pipeName)
params = ("xterm","-hold","-e",args.sPath,"+exec","runnerServer.cfg","+exec","levels.cfg","+exec","{0}RunnerBots.cfg".format(botCfgPrefix),_pipe)

pOpen = subprocess.Popen(params)

def exit_handler():
    print('Killing off subprocesses')
    pOpen.kill()
    print('Deleting pipes')
    os.remove(pipeName)
    client.disconnect()
    
#Evaluate combat based
while True:
    if args.NEAT is True:
        state = q3n.ActivationRun(pipeName,genome,config)
        if args.affective is True:
            combat = ResolveCombatCommands(client,combat,state)
    else:
        NonAffectiveRun(pipeName)

if __name__ == '__main__':
    pOpen.wait()
