# -*- coding: utf-8 -*-

## A conflict is a struggle between two opposing characters: a fight, a debate,
## a chase, a riddle duel, etc.
##
## In a conflict, the opposing sides deploy actions against each other

import collections

import character
from enum import Enum

        
    


#class ConflictCard (Enum):
#    open = 0,
#    locked = 1,
#    description = 2,
#    attack_effect = 3
#    
#    
#conflict_rules = {
#"open": ["#ATTACK@#"],
#"ATTACK": []
#}
#
#

#class ActionStack:
#    def __init__(self):
#        self.stack = []
#
#    def Push(self, manuver):
#        self.stack.append(manuver)
#    
#    def List(self):
#        return self.stack
#        
#    def Print(self):
#        for i in self.stack:
#            print(i.Describe())
#            
#
#astack = ActionStack()
## First character adds a manuver to the stack
#astack.Push(Manuver("Attack"))
#astack.Print()
## Second character responds to the manuver...


## OK, so here's how I think Conflicts get implemented:
## The conflict consists of a stack of current actions and a transcript
## of resolved actions
## Each character takes turns putting actions on the action stack.
## Which actions are valid to put there depends on the prerequisites
## of the actions and the tags of what is already played on the stack and/or
## the transcript.
## When a character is no longer able to respond to the state of the stack,
## the stack is capped by the resolution of the most recent unresolved 
## consequence, and that chunk of the stack is popped off and recorded in the
## transcript. 
## With the stack now unwound to the most recently unresolved consequence,
## the characters resume placing actions on the stack in an attempt to resolve 
## it.
##
## As an example:
## - start with an empty conflict: [] []
## - first character, A, tries to attack B: ["A swings his sword at B"]
## - the unresolved consequence: "B is wounded"
## - B, not wanting this, responds to A: "She dodges back"
## - The stack now looks like this: ["A attacks B" "B dodges A's attack"]
## - A responds: "B is backed against a wall"
## - B: "B throws a knife at A, distracting him at a crucial point"
## - A: "A ducks away from B's thrown knife"
## - B plays an action that caps the backed-against-the-wall consequence:
##   "Taking advantage of the distraction, B rolls to the side, out of the 
##   reach of A's sword."
## - A has no response. This resolves the state back to that point:
##   ["A attacks B", "B dodges back, "B is against the wall", 
##    "B throws a knife", "A ducks] <= resolved, removed from the stack.
##
## - Since the action is resolved, look at the consequence. Since A failed,
##   (which we know because B played the final action) then we get the failure
##   consequence. In this case, let's call it: "A is off balance after that 
##   attack failed."
## - We start the next climb up the stack from that starting point.
##
## - Meanwhile, the transcipt has already recorded all of the actions played.
## - When a cap is hit, starting at the root action of the conflict, walk 
##   forward in the stack, transcribing the actions into the transcript.
## - When an action is transcribed, mark it as already being transcribed.
## - Next time, start the transcribing from the first un-transcribed action.
##
## - As each action is added, it also has a pointer to the action it is 
##   responding to. 
## - When a cap happens, we start winding up these actions by tracing this
##   parenting tree to find the node that stops the resolution.
##
## - Consequences are how the actions branch. The action is an attempt to make
##   something happen. If it succeeds, the something happens, if it fails, the
##   failure effect/action happens instead
## - Consequences can, of course, be implemented as actions themselves
## - Not all actions have consequences
## - For example, parrying a sword thrust could be implemented as an action
## - without a consequence. The de facto effect is that it keeps the stack 
##   alive. But if the failed parry doesn't have any interesting effects 
##   (beyond that it delayed the effect of the sword thrust) then it doesn't
##   need to have any branching.
##
## - When one of the characters cannot find a valid action to put on the stack:
##      1. Transcribe the stack into the transcript, starting from the most
##         recent un-transcribed action.
##      2. Starting from the top of the stack, walk down the stack until
##         you find an action with a consequence, branch, or multiple possible
##         resolutions. (An unresolved one. If you find a resolved one, keep
##         going down the stack.)
##      3. Everything above that point gets removed from the stack. (Remember,
##         it's been transcribed already.)
##      4. Add the consequence action of that action node as the next action
##         at the top of the stack to start building on.
##
## - However, we also need to check to see if the state that a prior action
##   requires is still valid. I think the best place to do that check is
##   just prior to asking a character for their next action...i.e. do the check
##   after one character's turn is resolved and before the next one starts.
## - Invalid, unresolved actions don't have any of their consequences fire.
##   Instead, the stack is rolled up to the action above it.
## - Actions can also be resolved by having their goal conditions be met.
##
## As an example, suppose the characters are swordfighting in a room. The 
## actions played build on the tags from the setting: leaping on tables and
## swinging from chandeliers and so on. And at some point, one of the 
## characters jumps out a window. 
## Assuming that the sword fight still continues, any action that requires the
## character to still be in the room is now invalidated. I think that if this 
## is reflected in the tags that the actions will naturally be resolved: if
## an attack requires a certain distance and other other character just moved
## zones, that'll naturally invalidate most responses, and we won't need a
## special check for it.
## This may require a very nuanced set of tags, though.
## 
## I also need to work out how to handle it when goals are either fulfilled or
## invalidated...
##
## Emotional reactions to the events are handled by a separate system, executed
## on the finished transcript...

def assignList(a_list, contents):
    if isinstance(a_list, collections.MutableSequence):
            a_list = contents
    else:
        if not contents is None:
            a_list.append(contents)
        else:
            a_list = []
    

class Manuver:
    def __init__(self, m_name, prereqs=None, conseq=None):
        self.name = m_name
        self.prerequisites = []
        self.consequences = []
        assignList(self.prerequisites, prereqs)
        assignList(self.consequences, conseq)       

        
    def Describe(self):
        return self.name # TODO: Full description parameters for transcription
        
    def Print(self):
        print(self.Describe())
        
    
        
    


    
class Conflict:
    def __init__(self):
        self.stack = []
        self.transcript = []
        
    def getStateTags(self):
        """
        Returns the complete set of calculated tags for the conflict at this 
        point in the action stack and transcript.
        """
        return [] #TODO
        
    def addAction(self, action):
        # insert action onto stack
        self.stack.append(action)
    
    def resolveStack(self, action):
        # TODO
        print("resolving...")


    
