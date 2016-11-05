# -*- coding: utf-8 -*-

## A conflict is a struggle between two opposing characters: a fight, a debate,
## a chase, a riddle duel, etc.
##
## In a conflict, the opposing sides deploy actions against each other



import character

class Manuver:
    def __init__(self, m_name):
        self.name = m_name


attack = ["Describe an attack!" "ATTACK-EFFECT: causes damage"]
defense_success = ["Replace attack effect with defense description"]
defense_failure = ["Describe failed attack, inserted before ATTACK-EFFECT"]
        
effect_stack = []


        