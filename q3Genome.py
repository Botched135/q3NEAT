import os
import sys
import neat
import random


class QuakeGenome(neat.DefaultGenome):
    def __init__(self, key):
        super().__init__(key)
        self.ANN = None
        self.clientNum= -1
        self.serverNum= -1
        #NN

    def configure_new(self, config):
        super().configure_new(config)
    
    def configure_crossover(self, genome1, genome2, config):
        super().configure_crossover(genome1, genome2, config)

    def mutate(self, config):
        super().mutate(config)

    def distance(self, other, config):
        dist = super().distance(other, config)
        return dist

    def activate(self,_input,config):
        if self.ANN == None:
            self.ANN = neat.nn.FeedForwardNetwork.create(self, config)
            self.clientNum = _input[0]
        _ANNInput =_input[1:]
        ANNOutput = self.ANN.activate(_ANNInput)
        ANNOutput.insert(0,self.clientNum)
        return ANNOutput

    def evaluateGenome(self,_input):
        #SOME GODDAM FORMULAR
        self.fitness = random.random()*3.5





