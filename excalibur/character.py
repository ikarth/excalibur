# -*- coding: utf-8 -*-

class Character:
    def __init__(self, char_name):
        self.name = char_name
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
