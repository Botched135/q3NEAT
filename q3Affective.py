import heartpy as hb
import neurokit as nk
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pickle 
import matplotlib.mlab as mlab
from scipy.stats import mannwhitneyu as mw


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
m_lastAction = None

m_REVERT = -1
m_STAY = 0
m_INCREASE = 1
m_DECREASE = 2

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
	hb_measures = baselineDict['HR']['measures']

	m_baseHR = hb_measures['bpm']
	m_baseHRV = hb_measures['rmssd']

	EDA_measures = baselineDict['EDA']

	m_baseTonic = EDA_measures['df']['EDA_Tonic']
	m_basePhasic = EDA_measures['df']['EDA_Phasic']

	m_prevLevel = 3

# BVP needs to be numpy, while EDA needs to be standard array or list
def EvaluateNEATBiostate(BVP_array, EDA_array, genomeList, currentGenomeID):

	working_data, hb_measure = hb.process(BVP_array,64.0,report_time = True)

	processed_eda = nk.eda_process(EDA_array, freq= 1.9,sampling_rate=4)
	

	#Do the evaluation stuff
	return 0

def EvaluateAdaptiveBiostate(BVP_array = None, EDA_array = None):
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
	# Firstly, is he excited compared to baseline this is for HR and EDA
	# Secondly, is he exicted compared to previous
	# 1:0 : Might need to switch back
	# 0:1 : switch up
	# 0:0 : switch up
	# 1:1 : stay
	#Do the evaluation stuff 

	#If there is NO difference significantly between HR & EDA and the arousal was higher before, switch back

	#HR
	print(m_baseHR)
	print(percentage_change)
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
		if prev_hr_state > current_HRV*percentage_change:
			hr_rate = 1
		elif current_HRV < m_previousHRV*percentage_change:
			hrv_rate = -1
		else:
			hrv_rate = 0
	else:
		hrv_rate = -1 if current_HRV > m_baseHRV*percentage_change else 0

	#EDA Tonic
	current_Tonic = current_EDA['df']['EDA_Tonic']
	tonic_stats = mw(current_Tonic, m_baseTonic,alternative = 'greater')
	
	if m_previousTonic == None:
		if tonic_stats.p_value > p_value:
		    tonic_rate = 1 #must upgrade
		else:
		    tonic_greater_stats = mw(current_Tonic,m_previousTonic,alternative = 'greater')
		    tonic_less_stats = mw(current_Tonic,m_previousTonic,alternative = 'less')
		    if tonic_greater_stats.p_value <= p_value:
		    	# This is good. Stay or increase 
			    tonic_rate = 1
		    elif tonic_less_stats.p_value <= p_value:
		        tonic_rate = -1 #Revert back to the previous!
		    else:
			    tonic_rate = 0
	else:
		if tonic_stats.p_value <= p_value:
		    tonic_rate = 1 #Increase or stay
		else:
		    tonic_rate = 0 #Increase!

	#EDA Phasic
	current_Phasic = current_EDA['df']['EDA_Phasic']
	phasic_stats = mw(current_Phasic,m_basePhasic, alternative = 'greater')	

	if m_previousPhasic == None:
		if phasic_stats.p_value > p_value:
			phasic_rate = 1
		else:
			phasic_greater_stats = mw(current_Phasic,m_previousPhasic,alternative = 'greater')
			phasic_less_stats = mw(current_Phasic,m_previousPhasic,alternative = 'less')
			if phasic_greater_stats.p_value <= p_value:
				#stay! Or increae
				phasic_rate = 1
			elif phasic_less_stats.p_value <= p_value:
				#Revert back
				phasic_rate = -1 
			else:
				#increase! depending on the previous action
				phasic_rate = 0

	else:
		if phasic_stats.p_value <= p_value:
			phasic_rate = 1
		else: 
			phasic_rate = 0
	
	#Phasic component is the main,as 
	result = 0

    #Higher arousal 
	if ((current_Phasic+current_Tonic+current_HR)/3.0) > 0.5: 
		if hrv_rate == -1:
			result = -1
			m_lastAction = m_DECREASE
		else:
			result = 1
			m_lastAction = m_INCREASE
			#
	# significant lower arousal --
	elif ((current_Phasic+current_Tonic+current_HR)/3.0) <0.0:
		#REVERT!
		result = m_prevLevel-m_curLevel 
		m_lastAction = m_REVERT
	#No real change between this and the previous, do the same action again
	else:
		if m_lastAction == m_DECREASE:
			result = -1
		elif m_lastAction == m_INCREASE:
			result = 1

	#Finish off
	m_prevLevel = m_curLevel
	m_curLevel += result

	m_previousHR = hb_measure['bpm']
	m_previousHRV = hb_measure['rmssd']
	m_previousTonic = current_Tonic
	m_previousPhasic = current_Phasic 
	return result;
	


# Debugging
if __name__ == '__main__':
	EDA_filename = "BaselineData/ParticipantAlexWrite2/EDABase"
	EDA_Actfile = open(EDA_filename,'rb')
	EDA_Actdict = pickle.load(EDA_Actfile)
	EDA_Actfile.close()

	EDA_filename = "BaselineData/ParticipantAlexWrite1/EDABase"
	EDA_basfile = open(EDA_filename,'rb')
	EDA_basdict = pickle.load(EDA_basfile)
	EDA_basfile.close()
	EDA_basdict['df'].plot()
	EDA_Actdict['df'].plot()
	plt.show()
	EvaluateAdaptiveBiostate(baselineDict = EDA_basdict,EDA_array=EDA_Actdict)

	#Mann-whitney test test if first parameter is significantly <alternative> that second parameter