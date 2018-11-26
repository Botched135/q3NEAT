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



parser = argparse.ArgumentParser()

parser.add_argument("-ID","--participantID", type=str, help="ParticipantID used to load .csv files")

args = parser.parse_args()
if args.participantID is None:
	print("ERROR! No participantID defined. Exitting")
	raise SystemExit


Timestamps, BVP_numpy = genfromtxt('NodeJS/CSV/Participant{0}BVPBaseline.csv'.format(args.participantID),delimiter=';',skip_header = 1, unpack = True)
EDA_df = pd.read_csv('NodeJS/CSV/Participant{0}EDABaseline.csv'.format(args.participantID),delimiter=';')



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
