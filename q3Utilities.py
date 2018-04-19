import sys, os, string
import numpy as np

def CreatePipe(pipe_name):
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)
        print("Pipe has been created")

def ConvertPipeDataToFloatList(datastring):
    if len(datastring) <= 0:
        return None
    print(datastring)
    strList = datastring.split(':')
    strList = list(filter(None,strList))
    floatArrayList = []
    for _str in strList:
        split = _str.split(',')
        split = list(filter(None,split))
        npArray = np.array(split,dtype=float)
        floatArrayList.append(npArray)
    return floatArrayList

def ConvertNEATDataToString(neatArray):
    if len(neatArray) <= 0:
        return None
    finalString = ""
    for floatArray in neatArray:
        for values in floatArray:
            finalString += "{:.2f},".format(values)
        finalString+='-1,'

    return finalString

def ConvertArrayToTuple(array):
    return tuple(array)