import numpy as np
import heartbeat as hb
import neurokit as nk
import pandas as pd
import seaborn as sns
from numpy import genfromtxt
import argparse
import matplotlib.pyplot as plt 


parser = argparse.ArgumentParser()

parser.add_argument("-ID","--participantID", type=str, help="ParticipantID used to load .csv files")

args = parser.parse_args()
if args.participantID is None:
	print("ERROR! No participantID defined. Exitting")
	raise SystemExit


Timestamps, BVP_numpy = genfromtxt('NodeJS/CSV/Participant{0}BVPBaseline.csv'.format(args.participantID),delimiter=';',skip_header = 1, unpack = True)
EDA_df = pd.read_csv('NodeJS/CSV/Participant{0}EDABaseline.csv'.format(args.participantID),delimiter=';')



measures = hb.process(BVP_numpy,64.0,report_time = True)
processed_eda = nk.eda_process(EDA_df["EDA"],freq = 1.9, sampling_rate = 4);

print("Average heartrate(BPM): {0}".format(measures['bpm']))
print("Average HRV(RMSSD): {0} ".format(measures['rmssd']))
print(processed_eda)