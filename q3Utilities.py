import sys, os, string
import numpy as np

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


def SetupPipes(servers,pipe_path):
    resList = []
    path = os.path.expanduser(pipe_path)
    if not os.path.exists(path):
        os.mkdir(path)
        print('Created pipe folder')

    for x in range(0,servers):
            serverPath = '{0}pipeServer{1}/'.format(path,x)
            if not os.path.exists(serverPath):
                os.mkdir(serverPath)
                print('Created pipe {0} folder'.format(x))
            resList.append('{0}pipeServer{1}'.format(serverPath,(x)))

    for name in resList:
        if not os.path.exists(name):
            os.mkfifo(name)
            print('Pipe has been created at {0}'.format(name))

    return resList


