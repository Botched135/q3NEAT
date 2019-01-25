import numpy as np
import heartpy as hb
import neurokit as nk
import pandas as pd
import seaborn as sns
import pickle
from numpy import genfromtxt
import argparse
import os
import matplotlib.pyplot as plt 
from scipy.stats import mannwhitneyu as mw



parser = argparse.ArgumentParser()

parser.add_argument("-ID","--participantID", type=str, help="ParticipantID used to load .csv files")
parser.add_argument("--baseline", action='store_true', help ="Should the analyser analyse baseline or test data")

args = parser.parse_args()
if args.participantID is None:
	print("ERROR! No participantID defined. Exitting")
	raise SystemExit

dataType = 'Baseline' if args.baseline is True else 'Test'
if args.baseline is True:
	testType = ''
	Timestamps, BVP_numpy = genfromtxt('NodeJS/CSV/Participant{0}BVP{1}{2}.csv'.format(args.participantID,testType, dataType),delimiter=';',skip_header = 1, unpack = True)
	EDA_df = pd.read_csv('NodeJS/CSV/Participant{0}EDA{1}{2}.csv'.format(args.participantID,testType,dataType),delimiter=';')


	working_data, measures = hb.process(BVP_numpy,64.0,report_time = True, calc_freq = True)
	processed_eda = nk.eda_process(EDA_df["EDA"],freq = 1.9, sampling_rate = 4);

	path = "BaselineData/Participant{0}/".format(args.participantID)
	if not os.path.exists(path):
		os.makedirs(path)

	hb.plotter(working_data,measures)
	print("Average heartrate(BPM): {0}".format(measures['bpm']))
	print("Average HRV(RMSSD): {0} ".format(measures['rmssd']))
	print("Average HRV(LF): {0}".format(measures['lf']))
	processed_eda["df"].plot()

	hr_dict = {}
	hr_dict['working_data'] = working_data
	hr_dict['measures'] = measures

	# Store the baseline dicts to be transported
	pickle.dump(hr_dict, open('{0}HRBase'.format(path),'wb'))
	pickle.dump(processed_eda, open('{0}EDABase'.format(path),'wb'))

	plt.show()

else:
	AffectTimestamps, BVP_Affect = genfromtxt('NodeJS/CSV/Participant{0}BVPAffect{1}.csv'.format(args.participantID, dataType),delimiter=';',skip_header = 1, unpack = True)
	
    
	EDA_df_Affect = pd.read_csv('NodeJS/CSV/Participant{0}EDAAffect{1}.csv'.format(args.participantID,dataType),delimiter=';')
	processed_eda_Affect =nk.eda_process(EDA_df_Affect["EDA"],freq = 1.9, sampling_rate = 4);
	EDA_df_Affect["EDA"].plot()
	NonTimeStamps, BVP_Non = genfromtxt('NodeJS/CSV/Participant{0}BVPReg{1}.csv'.format(args.participantID, dataType),delimiter=';',skip_header = 1, unpack = True)
	working_non, non_m = hb.process(BVP_Non,64.0,calc_freq = True)

	EDA_df_Non = pd.read_csv('NodeJS/CSV/Participant{0}EDAReg{1}.csv'.format(args.participantID,dataType),delimiter=';')
	processed_eda_Non = nk.eda_process(EDA_df_Non["EDA"],freq = 1.9, sampling_rate = 4);

	MWTonic_stats_greater = mw( processed_eda_Affect['df']['EDA_Tonic'],processed_eda_Non['df']['EDA_Tonic'], alternative = 'greater')
	MWTonic_stats_less = mw( processed_eda_Affect['df']['EDA_Tonic'],processed_eda_Non['df']['EDA_Tonic'], alternative = 'less')
	MWPhasic_stats_greater = mw(processed_eda_Affect['df']['EDA_Phasic'], processed_eda_Non['df']['EDA_Phasic'], alternative = 'greater')
	MWPhasic_stats_less = mw(processed_eda_Affect['df']['EDA_Phasic'], processed_eda_Non['df']['EDA_Phasic'], alternative = 'less')

	print("Baseline HR analysis")
	times, baseline = genfromtxt('NodeJS/CSV/Participant{0}BVPBaseline5.csv'.format(args.participantID, dataType),delimiter=';',skip_header = 1, unpack = True) 
	wdata, m_baseline = hb.process(baseline,64.0,calc_freq = True)
	hb.plotter(wdata,m_baseline)
	print("Average heartrate(BPM): {0}".format(m_baseline['bpm']))
	print("Average HRV(RMSSD): {0} ".format(m_baseline['rmssd']))
	print("Average HRV(LF): {0}".format(m_baseline['lf']))
	working_affect, affect_m = hb.process(BVP_Affect,64.0,calc_freq = True)
	
	print("Affective HR analysis:")
	print("Average heartrate(BPM): {0}".format(affect_m['bpm']))
	print("Average HRV(RMSSD): {0} ".format(affect_m['rmssd']))
	print("Average HRV(LF): {0}".format(affect_m['lf']))
	working_non, non_m = hb.process(BVP_Non,64.0,calc_freq = True)
	print("Non-Affect HR analysis:")
	print("Average heartrate(BPM): {0}".format(non_m['bpm']))
	print("Average HRV(RMSSD): {0} ".format(non_m['rmssd']))
	print("Average HRV(LF): {0}".format(non_m['lf']))
	processed_eda_Affect['df'].plot(title = 'Affective')
	processed_eda_Non["df"].plot(title = 'Non-Affective')
	print("Tonic stats(greater):")
	print(MWTonic_stats_greater)
	print("Tonic stats(less):")
	print(MWTonic_stats_less)
	print("Phasic Stats(greater):")
	print(MWPhasic_stats_greater)
	print("Phasic stats(less):")
	print(MWPhasic_stats_less)

	plt.show()


