from __future__ import print_function
import os,sys, subprocess,argparse,time
import neat
import atexit
import pickle
import socket
from q3Genome import QuakeGenome
import q3NEAT as q3n
import q3Utilities as q3u
import time

import heartpy as hb
import neurokit as nk
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.stats import mannwhitneyu as mw



parser = argparse.ArgumentParser()

parser.add_argument("--path", type=str,default='./q3NN', help="path to experiment")
parser.add_argument("--pipePath",'-pp', type=str, default='~/q3Pipes/', help="path to pipe")
parser.add_argument('--configPath','-cp', type=str,default='./configs/config-q3Trainer',help="Config-file path for neat-python algorithms")
parser.add_argument('-sPath',type=str,default="../debug/ioq3/build/release-linux-x86_64/ioq3ded.x86_64",help="path to the server file")
parser.add_argument('-gF','--genomeFolder', type=str, help='path to the folder containing genomes to adapt between')
parser.add_argument('-ag','--activeGenomePath', type=str,help='path to genome that will control the agent initially')
parser.add_argument('--affective',action='store_true', help='Whether or not the affective version should run')
parser.add_argument('--NEAT', action='store_true',help='Whehter to use the NEAT-AI or the built-in bots')
parser.add_argument('-s','--socket',type=str, default='/tmp/AffectSocket', help='Path to UNIX socket for physiological signals')
parser.add_argument('-ID','--participantID',type=str, help='ID of the player. Used to load baseline')

args = parser.parse_args()
baselineDict = {}

hb_measures = None


EDA_measures = None

levelStatesList = []
progressionStateList =[]


#AFFECTIVE (so much easier than making individual module)
m_previousHR = None
m_previousHRV = None

m_previousTonic = None
m_previousPhasic = None

m_baseHR = None
m_baseHRV = None

m_baseTonic = None 
m_basePhasic = None

m_prevLevel = None
m_curLevel = None
m_prevLevel = None
m_lastAction = None

m_REVERT = -1
m_STAY = 0
m_INCREASE = 1
m_DECREASE = 2
m_Iteration = 0


p_value = 0.05
percentage_change = 1.15
# Get the entire session as a string
# ; seperates each sample
# : seperates BVP and EDA
def TransformAffectiveData(stringData):
    tempData = stringData.replace(',','.')
    BVP_EDA_List = tempData.split(':')
    BVP_EDA_List = list(filter(None,BVP_EDA_List))

    BVP_List = BVP_EDA_List[0].split(';')
    BVP_List = list(filter(None,BVP_List))

    EDA_List = BVP_EDA_List[1].split(';')
    EDA_List = list(filter(None,EDA_List))

    BVP_array = np.array(BVP_List,dtype=float)
    EDA_List = [float(item) for item in EDA_List]

    return BVP_array, EDA_List

def SetupBaseline(baselineDict):
    global hb_measures 
    global m_baseHR
    global m_baseHRV
    global EDA_measures
    global m_baseTonic
    global m_basePhasic
    global m_prevLevel
    global m_curLevel
    global levelStatesList
    global progressionStateList

    for x in range(5):
        levelDic = {'HR_mean': None, 'HRV' : None, 'Tonic_mean' : None, 'Phasic_mean' : None}
        levelStatesList.append(levelDic)
        progDic = {'Level': None,'HR_mean': None, 'HRV' : None, 'Tonic_mean' : None, 'Phasic_mean' : None}
        progressionStateList.append(progDic)

    
    hb_measures= baselineDict['HR']['measures']

    m_baseHR = hb_measures['bpm']
    m_baseHRV = hb_measures['rmssd']

    EDA_measures = baselineDict['EDA']

    m_baseTonic = EDA_measures['df']['EDA_Tonic']
    m_basePhasic = EDA_measures['df']['EDA_Phasic']

    m_prevLevel = 3
    m_curLevel = 3

# BVP needs to be numpy, while EDA needs to be standard array or list
def EvaluateNEATBiostate(BVP_array, EDA_array, genomeList, currentGenomeID):

    working_data, hb_measure = hb.process(BVP_array,64.0,report_time = True)

    processed_eda = nk.eda_process(EDA_array, freq= 1.9,sampling_rate=4)
    

    #Do the evaluation stuff
    return 0

def EvaluateAdaptiveBiostate(BVP_array = None, EDA_array = None):
    global hb_measures 
    global m_baseHR
    global m_baseHRV
    global m_previousHR
    global m_previousHRV

    global EDA_measures
    global m_baseTonic
    global m_basePhasic
    global m_previousTonic
    global m_previousPhasic

    global m_prevLevel
    global m_curLevel
    global m_lastAction

    global levelStatesList
    global progressionStateList
    global m_Iteration
    #1: higher arousal
    #0: no notificable change 
    #-1: lower arousal

    hr_rate = 0
    hrv_rate = 0
    tonic_rate = 0
    phasic_rate = 0


    if BVP_array is not None:
        working_data, hb_measure = hb.process(BVP_array,64.0,report_time = True)
    #TODO: Test the difference between resting and playing against the easiest possible character
    # High heart rate and high HRV = decrease level 

    if EDA_array is not None:
        current_EDA = nk.eda_process(EDA_array, freq= 1.9,sampling_rate=4)


    current_HR = hb_measure['bpm']
    current_HRV = hb_measure['rmssd']

    current_Tonic = current_EDA['df']['EDA_Tonic']
    current_Phasic = current_EDA['df']['EDA_Phasic']

    current_Tonic_mean =  np.mean(current_Tonic)
    current_Phasic_mean = np.mean(current_Phasic)
    # Firstly, is he excited compared to baseline this is for HR and EDA
    # Secondly, is he exicted compared to previous
    # 1:0 : Might need to switch back
    # 0:1 : switch up
    # 0:0 : switch up
    # 1:1 : stay
    #Do the evaluation stuff 

    #If there is NO difference significantly between HR & EDA and the arousal was higher before, switch back




    #HR
    hr_state = m_baseHR*percentage_change < current_HR
    if m_previousHR == None:
        hr_rate = 1 if hr_state else 0
    elif hr_state == 1:
        prev_hr_state = m_previousHR*percentage_change
        if prev_hr_state < current_HR:
            hr_rate = 1
        elif current_HR*percentage_change < m_previousHR:
            hr_rate = -1
        else:
            hr_rate = 0
    else:
        hr_rate = 0
        
        
    #HRV, use HRV in the end.
    hrv_state = m_baseHRV > current_HRV*percentage_change
    if m_previousHRV == None:
        hrv_rate = 1 if hrv_state else 0 #Compare with previous set
    elif hrv_state == 1:
        prev_hrv_state = m_previousHRV
        if prev_hrv_state > current_HRV*percentage_change:
            hrv_rate = 1
        elif current_HRV > m_previousHRV*percentage_change:
            hrv_rate = -1
        else:
            hrv_rate = 0
    else:
        if current_HRV > m_previousHRV*percentage_change:
            hrv_rate = -1
        elif current_HRV*percentage_change < m_previousHRV:
            hrv_rate = 1
        else:
            hrv_rate = -1 if current_HRV > m_baseHRV*percentage_change else 0

    #EDA Tonic

    tonic_stats = mw(current_Tonic, m_baseTonic,alternative = 'greater')

    if m_previousTonic is None:
        if tonic_stats.pvalue <= p_value:
            tonic_rate = 1 #Increase or stay
        else:
            tonic_rate = 0 #Increase!
    else:
        if tonic_stats.pvalue > p_value:
            tonic_rate = 1 #must upgrade
        else:
            tonic_greater_stats = mw(current_Tonic,m_previousTonic,alternative = 'greater')
            tonic_less_stats = mw(current_Tonic,m_previousTonic,alternative = 'less')
            if tonic_greater_stats.pvalue <= p_value:
                # This is good. Stay or increase 
                tonic_rate = 1
            elif tonic_less_stats.pvalue <= p_value:
                tonic_rate = -1 #Revert back to the previous!
            else:
                tonic_rate = 0

    #EDA Phasic
    phasic_stats = mw(current_Phasic,m_basePhasic, alternative = 'greater') 

    if m_previousPhasic is None:
        if phasic_stats.pvalue <= p_value:
            phasic_rate = 1
        else:
            phasic_rate = 0
    else:
        if phasic_stats.pvalue > p_value:
            phasic_rate = 1
        else:
            phasic_greater_stats = mw(current_Phasic,m_previousPhasic,alternative = 'greater')
            phasic_less_stats = mw(current_Phasic,m_previousPhasic,alternative = 'less')
            if phasic_greater_stats.pvalue <= p_value:
                #stay! Or increae
                phasic_rate = 1
            elif phasic_less_stats.pvalue <= p_value:
                #Revert back
                phasic_rate = -1 
            else:
                #increase! depending on the previous action
                phasic_rate = 0

    #Phasic component is the main,as 
    result = 0

    #Higher arousal 
    if ((phasic_rate+tonic_rate+hr_rate)/3.0) > 0.5: 
        #Check last action
        if m_lastAction == m_DECREASE:
            if m_curLevel ==1:
                result = 0
                m_lastAction = m_STAY
            elif levelStatesList[m_curLevel-2]['HR_mean'] is None:
                result = -1
                m_lastAction = m_DECREASE
            else: 
                lowerAffectiveState = ((1 if levelStatesList[m_curLevel-2]['HR_mean'] < current_HR else 0) + (1 if levelStatesList[m_curLevel-2]['HRV'] > current_HRV else 0) + (1 if levelStatesList[m_curLevel-2]['Tonic_mean'] < current_Tonic_mean else 0) + (1 if levelStatesList[m_curLevel-2]['Phasic_mean'] < current_Phasic_mean else 0))/4
                if levelStatesList[m_curLevel-2]['HR_mean'] is None:
                    result = -1
                    m_lastAction =  m_DECREASE
                elif lowerAffectiveState > 0.5:
                    result = -1
                    m_lastAction = m_DECREASE
                else:
                    result = 0
                    m_lastAction = m_STAY
        elif m_lastAction == m_INCREASE:
            if m_curLevel == 5:
                result =0
                m_lastAction = m_STAY
            elif levelStatesList[m_curLevel]['HR_mean'] is None:
                result = 1
                m_lastAction = m_INCREASE
            else: 
                upperAffectiveState = ((1 if levelStatesList[m_curLevel]['HR_mean'] < current_HR else 0) + (1 if levelStatesList[m_curLevel]['HRV'] > current_HRV else 0) + (1 if levelStatesList[m_curLevel]['Tonic_mean'] < current_Tonic_mean else 0) + (1 if levelStatesList[m_curLevel]['Phasic_mean'] < current_Phasic_mean else 0))/4
                if upperAffectiveState > 0.5:
                    if hrv_rate == -1:
                        result = -1
                        m_lastAction = m_DECREASE
                    else:
                        result = 1
                        m_lastAction = m_INCREASE
                else:
                    result = 0
                    m_lastAction = m_STAY
        else: 
            if hrv_rate == -1:
                result = -1
                m_lastAction = m_DECREASE
            elif hrv_rate == 0:
                result = 0
                m_lastAction = m_STAY
            else:
                result = 1
                m_lastAction = m_INCREASE
    # significant lower arousal -- SHOULD NOT STAY
    elif ((phasic_rate+tonic_rate+hr_rate)/3.0) <0.0:
        #REVERT!
        if m_curLevel == 1:
            result = 1
            m_lastAction = m_INCREASE
        elif m_curLevel == 5:
            result = -1
            m_lastAction = m_DECREASE
        elif m_lastAction == m_DECREASE:
            result = 1
            m_lastAction = m_INCREASE
        elif m_lastAction == m_INCREASE:
            result = -1
            m_lastAction = m_DECREASE
        else:
            upperAffectiveState = ((1 if levelStatesList[m_curLevel]['HR_mean'] < current_HR else 0) + (1 if levelStatesList[m_curLevel]['HRV'] > current_HRV else 0) + (1 if levelStatesList[m_curLevel]['Tonic_mean'] < current_Tonic_mean else 0) + (1 if levelStatesList[m_curLevel]['Phasic_mean'] < current_Phasic_mean else 0))/4
            lowerAffectiveState = ((1 if levelStatesList[m_curLevel-2]['HR_mean'] < current_HR else 0) + (1 if levelStatesList[m_curLevel-2]['HRV'] > current_HRV else 0) + (1 if levelStatesList[m_curLevel-2]['Tonic_mean'] < current_Tonic_mean else 0) + (1 if levelStatesList[m_curLevel-2]['Phasic_mean'] < current_Phasic_mean else 0))/4
            if upperAffectiveState > 0.5:
                m_lastAction = m_DECREASE
                result = -1
            elif lowerAffectiveState > 0.5:
                m_lastAction = m_INCREASE
                result = 1
            else:
                m_lastAction = m_DECREASE
                result = -1


    #No real change between this and the previous, do the same action again
    else:
        if m_previousPhasic is None:
            result = 1
            m_lastAction = m_INCREASE
        elif m_curLevel == 1:
            result = 1
            m_lastAction = m_INCREASE
        elif m_curLevel == 5:
            result = -1
            m_lastAction = m_DECREASE
        elif m_lastAction == m_DECREASE:
            result = -1
        elif m_lastAction == m_INCREASE:
            result = 1
        else:
            result = 0
            m_lastAction = m_STAY

    #Finish off

    m_prevLevel = m_curLevel
    m_curLevel += result
    if m_curLevel > 5:
        m_curLevel = 5
    elif m_curLevel < 1:
        m_curLevel = 1


    m_previousHR = current_HR
    m_previousHRV = current_HRV

    levelStatesList[m_prevLevel-1]['HR_mean'] = m_previousHR
    levelStatesList[m_prevLevel-1]['HRV'] = m_previousHRV

    progressionStateList[m_Iteration]['HR_mean'] = m_previousHR
    progressionStateList[m_Iteration]['HRV'] = m_previousHRV

    m_previousTonic = current_Tonic
    m_previousPhasic = current_Phasic

    levelStatesList[m_prevLevel-1]['Tonic_mean'] = current_Tonic_mean
    levelStatesList[m_prevLevel-1]['Phasic_mean'] = current_Phasic_mean

    progressionStateList[m_Iteration]['Tonic_mean'] = current_Tonic_mean
    progressionStateList[m_Iteration]['Phasic_mean'] = current_Phasic_mean

    progressionStateList[m_Iteration]['Level'] = m_prevLevel

    m_Iteration+=1
    print("Baseline HR: {0}    HRV: {1}".format(m_baseHR,m_baseHRV)) 
    print ("Phasic:{0}, tonic: {1}, hr: {2}(BPM){3:.3f}, hrv: {4}(RMSSD){5:.3f}".format(phasic_rate,tonic_rate,hr_rate,current_HR,  hrv_rate,current_HRV))
    print("Done with result: {0}".format(result))
    return result;


def UpdateNEAT(evaluationResult,genomeList, newGenomeID):
    return 0;

def NonAdamAffectiveRun(pipeName, update_val):
    pipeIn = open(pipeName,'r')
    pipeIn.read()
    pipeIn.close()

    # WRITE IF THERE SHOULD BE UPDATE
    updateString = str(update_val)
    pipeOut = open(pipeName,'w')
    pipeOut.write(updateString)
    pipeOut.close()

def EvaluateBiodata(client):
    client.send(b'eval')
    affectiveData = client.recv(66600).decode('utf-8')
    BVP, EDA = TransformAffectiveData(affectiveData)
    return EvaluateAdaptiveBiostate(BVP,EDA)

def EvaluateNEATBiodata(client, genomeList, currentGenomeID):
    client.send(b'eval')
    affectiveData = client.recv(66600).decode('utf-8')
    BVP, EDA = TransformAffectiveData(affectiveData)
    evaluationResult = EvaluateAdaptiveBiostate(BVP, EDA, genomeList, currentGenomeID, baselineDict)
    newGenomeID = 0;
    return newGenomeID #Needs to return what next genome id 

def EndSession():
    for x in range(5):
        print("For level {0}:".format(x+1))
        print(levelStatesList[x])
    for x in range(5):
        print("For session part {0}:".format(x+1))
        print(progressionStateList[x])

botCfgPrefix = 'nonAdam'

pipeName = q3u.SetupPipes(1,args.pipePath)
pipeName = pipeName[0]
baselineDict = {}

m_prevLevel = 3

if args.affective is True or args.participantID is not None:
    combat = 0 #Three stages: 0: No change, 1: engaged in combat, 2: Combat ended, 3: Evaluation

    # Baseline dict for parsing onto the affective evaluator
    # Load pickled files
    base_path = "BaselineData/Participant{0}/".format(args.participantID)

    HR_file = open('{0}HRBase'.format(base_path),'rb')
    EDA_file=  open('{0}EDABase'.format(base_path),'rb')

    baselineDict['HR'] = pickle.load(HR_file)
    baselineDict['EDA'] = pickle.load(EDA_file)

    HR_file.close()
    EDA_file.close()

    SetupBaseline(baselineDict)
    
    #UNIX socket client
    socketPath = args.socket
    client= socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    client.connect(socketPath)
    client.send(b'Q3Connected')

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
params = ("xterm","-hold","-e",args.sPath,"+exec","runnerServer.cfg","+exec","runnerLevels.cfg","+exec","{0}RunnerBots.cfg".format(botCfgPrefix),_pipe)

pOpen = subprocess.Popen(params)

def exit_handler():
    print('Killing off subprocesses')
    pOpen.kill()
    print('Deleting pipes')
    os.remove(pipeName)
    client.send(b'nonAffect')
    client.close()

iterations = 0
updates = 0;
#Evaluate combat based
_time = ""
prev_time = time.time() 
time_counter = prev_time;
if args.affective is True:
    print("Entering affective")
    while True:
        if args.NEAT is True:
            if iterations > 1200:
                iterations = 0
                evalResult = EvaluateNEATBiodata(client)
                genome = UpdateNEAT(evalResult)
                updates += 1 

            q3n.ActivationRun(pipeName,genome,config)
        else:
            update_val = 0
            if time_counter > prev_time+59.0:
                iterations = 0
                _time = time.time()
                print("\n\nRun evaluation ({0:.3f} seconds since last)".format(_time-prev_time))
                prev_time = _time
                update_val = EvaluateBiodata(client)
                updates+= 1
            if updates >4:
                    updates = 0;
                    EndSession()
                    client.send(b'end')

            NonAdamAffectiveRun(pipeName, update_val)

        time_counter=time.time()
        iterations+=1
elif args.NEAT is True:
    while True: 
        q3n.ActivationRun(pipeName,genome,config)

if args.affective is not True:
    while time_counter-prev_time < 300:
        time_counter = time.time()
    client.send(b'nonAffect')
    pOpen.wait()
