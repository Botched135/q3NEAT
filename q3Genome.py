import os
import sys
import neat
import random
import math


class QuakeGenome(neat.DefaultGenome):
    def __init__(self, key):
        super().__init__(key)
        self.ANN = None
        self.clientNum= -1
        self.serverNum= -1
        self.totalFit = 0
        self.fitness = -1
        self.age = 0
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
        ANNOutput = self.ANN.activate(_input)
        return ANNOutput

    def evaluateGenome(self,_input):
        #SOME GODDAM FORMULAR
        accuracy = _input[0]
        #movementFails = _input[1]
        #deaths = _input[2]
        #self.age+=1
        #self.totalFit += accuracy-movementFails-deaths
        #self.fitness = self.totalFit/self.age;
        self.fitness = accuracy
        if math.isinf(self.fitness) and self.fitness < 0:
            self.fitness = 0.0 
