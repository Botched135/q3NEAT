import os
import sys
import neat


class quakeGenome(neat.DefaultGenome):
    def __init__(self, key):
        super().__init__(key)
        self.ANN = None
        self.clientNum= 0
        self.serverNum= 0
        #NN

    def activate(self,_input,config):
        if self.ANN = None:
            self.ANN = neat.nn.FeedForwardNetwork.create(self, config)
            self.clientNum = _input[0]
            #self.serverNum = 0
        ANNOutput = self.ANN.activate(_input)
        ANNOutput.insert(0,self.clientNum)
        return 

    def evaluateGenome(_input):
        #SOME GODDAM FORMULAR
        self.fitness = 0
