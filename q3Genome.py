import os
import sys
import neat


class quakeGenome(neat.DefaultGenome):
    def __init__(self, key):
        super().__init__(key)
        self.discount = None


