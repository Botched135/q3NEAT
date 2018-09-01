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
import time

parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('-sPath',type=str,default="../debug/ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-gF','--genomeFolder', type=str, help='path to the folder containing genomes to adapt between')
parser.add_argument('-ag','--activeGenomePath', type=str,help='path to genome that will control the agent initially')
parser.add_argument('--HRBase', type=float, help='Heart Rate (BPM) baseline of the participant')
parser.add_argument('--EDABase', type=float, help='Electrodermal Activity baseline of the participant')
parser.add_argument('--HRVBase', type=float, help='Heart Rate Variability baseline of the participant')
parser.add_argument('-s','--socket',type=str, help='Path to UNIX socket for physiological signals')

args = parser.parse_args()

def TransformAffectiveData(data):
    PhysList = []
    for x in range(4):
        PhysList.append([])
    data = data.replace(',','.')
    dataList = data.split(':')
    dataList = list(filter(None,dataList))
    for dataSet in dataList:
        splitList = dataSet.split(';')
        splitList = list(filter(None,splitList))
        numpyArray = np.array(splitList,dtype=float)
        counter = 0;
        for value in numpyArray:
            if value != -1:
                PhysList[counter].append(value)
            counter+=1

def EvaluateBiostate(PhysList, genomeList, currentGenomeID):
    return 0

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
        TransformAffectiveData(affectiveData)
    return res


pipeName = q3u.SetupPipes(1,args.pipePath)
pipeName = pipeName[0]
combat = 0 #Three stages: 0: No change, 1: engaged in combat, 2: Combat ended, 3: Evaluation

#UNIX socket client
socketPath = args.socket
client= socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
client.connect(socketPath)
client.send(b'Q3Runner connected')



with open(args.activeGenomePath,'rb') as file:
	genome = pickle.load(file)

config = neat.Config(	QuakeGenome, neat.DefaultReproduction, 
					neat.DefaultSpeciesSet, neat.DefaultStagnation, 
					args.configPath)

_pipe = '+pipe={0}'.format(pipeName)
params = ("xterm","-hold","-e",args.sPath,"+exec","runnerServer.cfg","+exec","levels.cfg","+exec","runnerBots.cfg",_pipe)

pOpen = subprocess.Popen(params)

def exit_handler():
    print('Killing off subprocesses')
    pOpen.kill()
    print('Deleting pipes')
    os.remove(pipeName)
    client.disconnect()
    
#Evaluate combat based
while True:
    state = q3n.ActivationRun(pipeName,genome,config)
    combat = ResolveCombatCommands(client,combat,state)

if __name__ == '__main__':
    pOpen.wait()
