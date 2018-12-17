import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy import stats


AffectiveLoadedData = genfromtxt('TestData/Affect.csv',delimiter=',')
NonAffectiveLoadedData = genfromtxt('TestData/NonAffect.csv',delimiter=',')
#List of lists.. Each list containing the data about one variable for 
# Needs to be numpy arrays
Categories = [		'Competence', 	  'Flow', 	  'Tension/Annoyance',   'Challenge',   'Negative Affect','Positive Affect']
CategoriesValue =[(4,11,15,17,19),(6,13,23,25,27),    (20,22,26),     (12,21,24,28,29),   (8,9,10,16),     (3,5,7,14,18)]
CategoryParametric = [ True, 		   True, 			 True, 			    True,             False, 			True]


#Each tuple contains info about one category


UserData =[]
for userData in AffectiveLoadedData[9:]:
	userMeanList = []
	for cat in CategoriesValue:
		catVal = 0
		for index in cat:
			catVal+=userData[index]
		catVal /= len(cat)
		userMeanList.append(catVal)
	UserData.append(userMeanList)


NonUserData = []
for userData in NonAffectiveLoadedData[9:]:
	userMeanList = []
	for cat in CategoriesValue:
		catVal = 0
		for index in cat:
			catVal+=userData[index]
		catVal /= len(cat)
		userMeanList.append(catVal)
	NonUserData.append(userMeanList)

print(Categories)
iterations = 9
for Affect, Non in zip(UserData,NonUserData):
	print("participant {0}:Affective Data for ".format(iterations))
	print(Affect)
	print("participant {0}: Non-Affective Data for participant {0}".format(iterations))
	print(Non)
	iterations += 1

#for userData in AffectiveLoadedData[1:]
'''


AffectiveData = []
for userData in AffectiveLoadedData[1:]:
	userMeanList = []
	for cat in CategoriesValue:
		catVal = 0
		for index in cat:
			catVal+=userData[index]
		catVal /= len(cat)
		userMeanList.append(catVal)
	userMeanList = np.array(userMeanList,dtype=float)
	AffectiveData.append(userMeanList)


NonAffectiveData = []
for userData in NonAffectiveLoadedData[1:]:
	userMeanList = []
	for cat in CategoriesValue:
		catVal = 0
		for index in cat:
			catVal+=userData[index]
		catVal /= len(cat)
		userMeanList.append(catVal)
	userMeanList = np.array(userMeanList,dtype=float)
	NonAffectiveData.append(userMeanList)


IsParametricData = True
IsNormalDistributed = True
p_value = 0.05
# Descriptive statistics

AffectiveMean = [] #One list per category
AffectiveMedian = []
AffectiveSTD = []
NonAffectiveMedian = []
NonAffectiveMean = []
NonAffectiveSTD = []


for index in range(len(Categories)):
	AffectiveValues = []
	NonAffectiveValues = []	
	for AffectiveUserData, NonAffectiveUserData in zip(AffectiveData, NonAffectiveData):	
		AffectiveValues.append(AffectiveUserData[index])
		NonAffectiveValues.append(NonAffectiveUserData[index])

	AffectiveValues = np.array(AffectiveValues,dtype=float)
	NonAffectiveValues = np.array(NonAffectiveValues, dtype=float)

	AffectiveMean.append(np.mean(AffectiveValues))
	AffectiveMedian.append(np.median(AffectiveValues))
	AffectiveSTD.append(np.std(AffectiveValues))

	NonAffectiveMean.append(np.mean(NonAffectiveValues))
	NonAffectiveMedian.append(np.median(NonAffectiveValues))
	NonAffectiveSTD.append(np.std(NonAffectiveValues))


# Show graphic



for x in range(len(Categories)):
	print("Descriptive statistics for Affective {0}:\nMean: {1}\tMedian: {2}\tSTD: {3}".format(Categories[x],AffectiveMean[x],AffectiveMedian[x],AffectiveSTD[2]))
	print("")
	print("Descriptive statistics for Non-Affective {0}:\nMean: {1}\tMedian: {2}\tSTD: {3}".format(Categories[x],NonAffectiveMean[x],NonAffectiveMedian[x],NonAffectiveSTD[2]))
	print("\n")


#For each variable --> that is flow, challenge etc.
AffectiveAD  = [] 
NonAffectiveAD = []
for AffectiveList, NonAffectiveList in zip(AffectiveData, NonAffectiveData):
	AffADstats = stats.anderson(AffectiveList)
	AffectiveAD.append(AffADstats)
	NonADStats = stats.anderson(NonAffectiveList)
	NonAffectiveAD.append(NonADStats)

for AffAD, NonAffAD, Category in zip(AffectiveAD, NonAffectiveAD,Categories):
	print("Affective Anderson Darling Statistic for {0}: {1:.5f}".format(Category,AffAD.statistic))
	for i in range(len(AffAD.critical_values)):
	    sl, cv = AffAD.significance_level[i], AffAD.critical_values[i]
	    if AffAD.statistic < AffAD.critical_values[i]:
		    print('%.3f: %.3f, data looks normal (fail to reject H0)' % (sl, cv))
	    else:
		    print('%.3f: %.3f, data does not look normal (reject H0)' % (sl, cv))

	print("")
	print("Non Affective Anderson Darling Statistic for {0}: {1:.5f}".format(Category,NonAffAD.statistic))
	for i in range(len(NonAffAD.critical_values)):
	    sl, cv = NonAffAD.significance_level[i], NonAffAD.critical_values[i]
	    if NonAffAD.statistic < NonAffAD.critical_values[i]:
		    print('%.3f: %.3f, data looks normal (fail to reject H0)' % (sl, cv))
	    else:
		    print('%.3f: %.3f, data does not look normal (reject H0)' % (sl, cv))
	print("\n")


if IsNormalDistributed is False:
	LeveneData = []
	for AffectiveList, NonAffectiveList in zip(AffectiveData, NonAffectiveData):
	    LeveneStats = stats.levene(AffectiveList,NonAffectiveList)
	    LeveneData.append(LeveneStats)
	for cat, lv, para in zip(Categories, LeveneData, CategoryParametric):
	    if lv.pvalue > p_value:
		    print("Levene: Homogeneity of variance has NOT been violated for {0} at alpha level {1} (p-value: {2:.5f}\tstats: {3:.5f})".format(cat,p_value,lv.pvalue,lv.statistic))
	    else:
		    print("Levene: Homogeneity of variance has been violated for {0} at alpha level {1} (p-value: {2:.5f}\tstats:{3:.5f})".format(cat,p_value,lv.pvalue,lv.statistic))
		    para = False
else:
	BartlettData = []
	for AffectiveList, NonAffectiveList in zip(AffectiveData, NonAffectiveData):
	    BartlettStats = stats.bartlett(AffectiveList,NonAffectiveList)
	    BartlettData.append(BartlettStats)

	for cat, lv, para in zip(Categories, BartlettData, CategoryParametric):
		if lv.pvalue > p_value:
			print("Bartlett: Homogeneity of variance has NOT been violated for {0} at alpha level {1} (p-value: {2:.5f}\tstats:{3:.5f})".format(cat,p_value,lv.pvalue,lv.statistic))
		else:
			print("Bartlett: Homogeneity of variance has been violated for {0} at alpha level {1} (p-value: {2:.5f}\tstats:{3:.5f})".format(cat,p_value,lv.pvalue,lv.statistic))
			para = False

#for AD, NonAD, Levene in AffectiveAD, NonAffectiveAD, LeveneData:
print("\n")

T_testData = []

#if IsParametricData is True:
for AffectiveList, NonAffectiveList, para in zip(AffectiveData, NonAffectiveData, CategoryParametric):
    T_testStats = None
    if para is True:
    	T_testStats = stats.ttest_rel(AffectiveList,NonAffectiveList)
    else:
    	T_testStats = stats.wilcoxon(AffectiveList,NonAffectiveList)
    T_testData.append(T_testStats)

for ttest,cat, para in zip(T_testData,Categories, CategoryParametric):
    if para is True:
        if ttest.pvalue < p_value:
	        print("There is a signficant difference at alpha level {0} for t-test comparing {1}, stats: {2:.5f} \t p-value {3:.5f}".format(p_value, cat, ttest.statistic , ttest.pvalue))
        else:
	        print("There is a NO signficant difference at alpha level {0} for t-test comparing {1}, stats: {2:.5f} \t p-value {3:.5f}".format(p_value, cat, ttest.statistic , ttest.pvalue))
    else:
        if ttest.pvalue < p_value:
            print("There is a signficant difference at alpha level {0} for wilcoxon test comparing {1}, stats: {2:.5f} \t p-value {3:.5f}".format(p_value, cat,ttest.statistic , ttest.pvalue))
        else:
        	print("There is NO signficant difference at alpha level {0} for wilcoxon test comparing {1}, stats: {2:.5f} \t p-value {3:.5f}".format(p_value, cat,ttest.statistic , ttest.pvalue))
#

#else:
    #for AffectiveList, NonAffectiveList in zip(AffectiveData, NonAffectiveData):
   # 	T_testStats = stats.wilcoxon(AffectiveList,NonAffectiveList)
  #  	T_testData.append(T_testStats)

 #   for wilcoxon, cat in zip(T_testData,Categories):
#	    if wilcoxon.pvalue < p_value:
#		    print("There is a signficant difference at alpha level {0} for wilcoxon test comparing {1}, stats: {2:.5f} \t p-value {3:.5f}".format(p_value, cat,wilcoxon.statistic , wilcoxon.pvalue))
#	    else:
#		    print("There is NO signficant difference at alpha level {0} for wilcoxon test comparing {1}, stats: {2:.5f} \t p-value {3:.5f}".format(p_value, cat,wilcoxon.statistic , wilcoxon.pvalue))
#

# width of the bars
barWidth = 0.3
# One for each category, two in each
# The x position of bars
r1 = np.arange(len(AffectiveMean))
r2 = [x + barWidth for x in r1]
 
# Create blue bars
plt.bar(r1, AffectiveMean, width = barWidth, color = 'orange', edgecolor = 'black', capsize=7, label='Affective')
 
# Create cyan bars
plt.bar(r2, NonAffectiveMean, width = barWidth, color = '#468499', edgecolor = 'black',  capsize=7, label='Non-Affective')
 
# general layout
plt.xticks([r + barWidth/2 for r in range(len(AffectiveMean))], Categories)
plt.ylabel('Mean')
plt.title('Comparison of Affective and Non-Affective version')
plt.legend()

plt.show()

# Create blue bars
plt.bar(r1, AffectiveMedian, width = barWidth, color = 'orange', edgecolor = 'black', capsize=6, label='Affective')
 
# Create cyan bars
plt.bar(r2, NonAffectiveMedian, width = barWidth, color = '#468499', edgecolor = 'black',  capsize=6, label='Non-Affective')
 
# general layout
plt.xticks([r + barWidth/2 for r in range(len(AffectiveMedian))], Categories)
plt.ylabel('Median')
plt.title('Comparison of Affective and Non-Affective version')
plt.legend()

plt.show()

plt.bar(r1, AffectiveSTD, width = barWidth, color = 'orange', edgecolor = 'black', capsize=7, label='Affective')
 
# Create cyan bars
plt.bar(r2, NonAffectiveSTD, width = barWidth, color = '#468499', edgecolor = 'black',  capsize=7, label='Non-Affective')
 
# general layout
plt.xticks([r + barWidth/2 for r in range(len(AffectiveSTD))], Categories)
plt.ylabel('Standard Deviation')
plt.title('Comparison of Affective and Non-Affective version')
plt.legend()

plt.show()
'''