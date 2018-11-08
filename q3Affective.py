import heartbeat as hb
import neurokit as nk
import numpy as np
import pandas as pd
import seaborn as sns

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

# BVP needs to be numpy, while EDA needs to be standard array or list
def EvaluateNEATBiostate(BVP_array, EDA_array, genomeList, currentGenomeID, baselineDict):

	hb_measure = hb.process(BVP_array,64.0,report_time = True)
	processed_eda = nk.eda_process(EDA_array, freq= 1.9,sampling_rate=4)
	

	#Do the evaluation stuff
	return 0

def EvaluateAdaptiveBiostate(BVP_array, EDA_array, baselineDict):
	hb_measure = hb.process(BVP_array,64.0,report_time = True)
	processed_eda = nk.eda_process(EDA_array, freq= 1.9,sampling_rate=4)

	#Do the evaluation stuff 
	return 0;
	


# Debugging
if __name__ == '__main__':
	leData = "1,0998348;45,0348;-200,21345;:23,0012;2144,12;"

	x, y = TransformAffectiveData(leData);
	print(x)
	for q in x:
		print(q/2)

	print(y)

	for derp in y:
		print(derp%10)
	