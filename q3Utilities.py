import sys, os, string

def CreatePipe(pipe_name):
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)
        print("Pipe has been created")

def ConvertPipeDataToFloatList(datastring):
    strList = datastring.split(':')
    strList = list(filter(None,strList))
    floatArrayList = []
    for _str in strList:
        split = _str.split(',')
        npArray = np.array(split,dtype=float)
        floatArrayList.append(npArray)
    return floatArrayList

def ConvertNEATDataToString(neatArray):
    finalString = ""
    for floatArray in neatArray:
        for values in floatArray:
            finalString += '{:.2f},'.format
        finalString+=':'
    return finalString
