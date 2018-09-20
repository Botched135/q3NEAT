import numpy as np
from numpy import genfromtxt
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-ID","--participantID", type=str, help="ParticipantID used to load .csv files")

args = parser.parse_args()
if args.participantID is None:
	print("ERROR! No participantID defined. Exitting")
	raise SystemExit


EDACsv = genfromtxt('NodeJS/CSV/Participant{0}EDA.csv'.format(args.participantID),delimiter=';')
CardioCsv = genfromtxt('NodeJS/CSV/Participant{0}HR.csv'.format(args.participantID),delimiter=';')

EDA_array, HR_array, IBI_array, HRV_array = [],[],[],[]

for EDATuple in EDACsv[1:]:
	EDA_array.append(EDATuple[1])

EDA_array = np.array(EDA_array,dtype=float)

for CardioTuple in CardioCsv[1:]:
	HR_array.append(CardioTuple[1])
	IBI_array.append(CardioTuple[2])
	HRV_array.append(CardioTuple[3])


HR_array = np.array(HR_array, dtype=float)
IBI_array = np.array(IBI_array,dtype=float)
HRV_array = np.array(HRV_array,dtype=float)

EDAMedian = np.median(EDA_array)
HRMedian = np.median(HR_array)
IBIMedian = np.median(IBI_array)
HRVMedian = np.median(HRV_array)

print("EDA Median: "+EDAMedian)
print("HR Median: "+HRMedian)
print("IBI Median: "+IBIMedian)
print("HRV Median: "+HRVMedian)