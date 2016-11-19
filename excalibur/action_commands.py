# -*- coding: utf-8 -*-

import collections
import functools
from enum import Enum
import numpy.random
import sys

#class CommandQueue:
#    def __init__(self):
#        self.queue = []
#
#    def add(self, cmd):
#        if isinstance(cmd, collections.MutableSequence):
#            self.queue.extend(cmd)
#        else:
#            self.queue.append(cmd)
#    
#    def remove(self, cmd):
#        while True:
#            try:
#                self.queue.remove(cmd)
#            except ValueError:
#                return
#        
#    def remove_one(self, cmd):
#        try:
#            self.queue.remove(cmd)
#        except ValueError:
#            return
#            
#    def contains(self, tag):
#        if self.queue.count(tag) > 0:
#            return True
#        return False
#    
#    def contains_not(self, tag):
#        if self.queue.count(tag) > 0:
#            return False
#        return True
#        
#
#    
#    def currentState(self):
#        state = []
#        for cmd in self.queue:
#            state = cmd(state)
#        return state
#        
#    def parse(self, cmd):
#        """
#        Takes a command string list and translates it into the effect...
#        """
#        translate_table = {"remove": lambda x: self.remove(x),
#                       "remove_one": lambda x: self.remove_one(x),
#                       "add": lambda x: self.add(x)}
#        parsing = cmd["cmd"]
#        index = 0
#        while index < len(parsing):
#            if callable(translate_table[parsing[index]]):
#                translate_table[parsing[index]](parsing[index+1])
#                index += 1            
#            index += 1
#    

class Cmd(Enum):
    current_actor = 1 # character currently acting, set dynamically
    current_target = 2 # object of the character's action, set dynamically
    action = 3
    require = 4
    forbid = 5
    effects = 6
    add = 7
    remove = 8
    remove_one = 9
    last_time = 999
    
def translateActionDescription(action):
    actor = action[Cmd.current_actor]
    target = action[Cmd.current_target] 
    # TODO: translate the variables into their description forms
    action_string = action[Cmd.action]
    action_string = action_string.replace("{ACTOR}", actor)
    action_string = action_string.replace("{ANTAGONIST}", target)
    action_string = action_string.replace("{ANTAGONIST'S}", target + "'s")
    action_string = action_string.replace("{ACTOR'S}", actor+"'s")
    return action_string

class ActionProcessor:
    def __init__(self):
        self.queue = collections.deque()
        
    def addAction(self, act):
        #if isinstance(act, collections.MutableSequence):
        #    self.queue.extend(act)
        #else:
        self.queue.append(act)
            
    def currentState(self):
        """
        Runs the effects in the queue, returning the current collection of tags
        """
        effect_bag = collections.Counter()
        for act in self.queue:
            if not act is None:
                if Cmd.add in act:
                    act_ef = act[Cmd.add]
                    #print(act_ef)
                    act_ef = [tag.replace("{ACTOR}", act[Cmd.current_actor]) for tag in act_ef]
                    act_ef = [tag.replace("{TARGET}", act[Cmd.current_target]) for tag in act_ef]
                    #print(act_ef)
                    effect_bag.update(act_ef)
                if Cmd.remove in act:
                    for i in act[Cmd.remove]:
                        i = i.replace("{ACTOR}", act[Cmd.current_actor])
                        i = i.replace("{TARGET}", act[Cmd.current_target])
                        effect_bag[i] = 0
                if Cmd.remove_one in act:
                    act_ef = act[Cmd.remove_one]
                    act_ef = [tag.replace("{ACTOR}", act[Cmd.current_actor]) for tag in act_ef]
                    act_ef = [tag.replace("{TARGET}", act[Cmd.current_target]) for tag in act_ef]
                    effect_bag.subtract(act_ef)
                effect_bag = +effect_bag # remove zero and negative counts
            
        return effect_bag
    
    def currentTranscript(self):
        transcript = []
        for act in self.queue:
            if not act is None:
                transcript.append(translateActionDescription(act))
        return transcript
                

def expandTag(tag, actor, target):
    tag = tag.replace("{ACTOR}", actor)
    tag = tag.replace("{TARGET}", target)
    return tag
    
                
class Conflict:
    def __init__(self, action_catalog):
        self.char_one = "ROBIN_HOOD"
        self.char_two = "SIR_GALAHAD"
        self.action_processor = ActionProcessor()
        self.deck_of_actions = action_catalog
        self.current_state = []
        self.actions_last_time = []
        for act in self.deck_of_actions:
            act.update({Cmd.last_time: 0.0})
        
        
    def performAction(self, actor, target, action):
        action.update({Cmd.current_actor: actor, Cmd.current_target: target})
        tag_list_list = [Cmd.require, Cmd.forbid, Cmd.add, Cmd.remove, Cmd.remove_one]
        for tag_list in tag_list_list:
            try:
                tl = action[tag_list]
                tl = [expandTag(i, action[Cmd.current_actor], action[Cmd.current_target]) for i in tl]
                action.update({tag_list: tl})
            except KeyError:
                pass
        print(action)
        self.action_processor.addAction(action)
        
    def currentState(self):
        self.current_state = self.action_processor.currentState()
        return self.current_state
    
    def currentTranscript(self):
        return self.action_processor.currentTranscript()
        
    def prereqCheck(self, action, actor, target):
        if Cmd.require in action:
            for pre in action[Cmd.require]:
                pre_str = expandTag(pre, actor, target)
                if not (self.current_state[pre_str] > 0):
                    return False
        if Cmd.forbid in action:
            for pre in action[Cmd.forbid]:
                pre_str = expandTag(pre, actor, target)
                if (self.current_state[pre_str] > 0):
                    return False
        return True
        
    def pickNextAction(self, actor_num):
        acting = self.char_one
        targeting = self.char_two
        if actor_num != 1:
            acting = self.char_two
            targeting = self.char_one
        # filter actions...
        state = self.currentState() #used for cache side effect
        live_deck = [act for act in self.deck_of_actions if self.prereqCheck(act, acting, targeting)]
        if len(live_deck) > 0:
            prob = [1.0 - act[Cmd.last_time] for act in live_deck]
            psum = sum(prob)
            next_act = numpy.random.choice(live_deck, 1, False, [p / psum for p in prob])
            return next_act[0]
        return None
        
    def hideAction(self, action):
        #self.deck_of_actions.remove(action)
        #idx = self.deck_of_actions.index(action)
        #self.actions_last_time[idx] = 1.0
        idx = self.deck_of_actions.index(action)
        action.update({Cmd.last_time: 1.0})
        self.deck_of_actions[idx] = action

    def unhideActions(self):
        for idx, act in enumerate(self.deck_of_actions):
            act[Cmd.last_time] = act[Cmd.last_time] * 0.95
            self.deck_of_actions[idx] = act
        
        
    def performNextAction(self, actor_num):
        self.unhideActions()
        acting = self.char_one
        targeting = self.char_two
        if actor_num != 1:
            acting = self.char_two
            targeting = self.char_one
        next_action = self.pickNextAction(actor_num)
        if next_action is None:
            print("No Action")
            return # todo: unwind to last branch
        self.performAction(acting, targeting, next_action)
        self.hideAction(next_action) # this action has been spent. 
        # Remove it from consideration until later...
        
        
def Fight(conflict):
    conflict.performNextAction(0)
    print("---")
    print(conflict.currentState())
    print("===")
    conflict.performNextAction(1)
    #conflict.currentTranscript()
    print("---")
    print(conflict.currentState())
    print("===")
    return
        

        


    
    
actcat = [
{Cmd.require: [], Cmd.forbid: ["end combat", "in combat", "begin combat"], Cmd.add: ["begin combat"], Cmd.action: "BEGIN"},
{Cmd.require: ["begin combat"], Cmd.remove: ["begin combat"], Cmd.add: ["in combat"], Cmd.action: "In a moment {ACTOR} stepped quickly {UPON THE PLACE} where {ANTAGONIST} stood."},
{Cmd.require: ["begin combat"], Cmd.remove: ["begin combat"], Cmd.add: ["in combat"], Cmd.action: "At last {ACTOR} struck like a flash, and--\"rap!\"--{ANTAGONIST} met the blow and turned it aside, and then smote back at {ACTOR}, who also turned the blow; and so this mighty battle began."},
{Cmd.require: ["begin combat"], Cmd.remove: ["begin combat"], Cmd.add: ["in combat"], Cmd.action: "Then {ACTOR} spat upon {ACTOR'S} hands and, grasping {ACTOR'S} {ACTOR_WEAPON}, came straight at the other."},
{Cmd.require: ["begin combat"], Cmd.remove: ["begin combat"], Cmd.add: ["in combat"], Cmd.action: "{ACTOR} gripped {ACTOR'S} {ACTOR_WEAPON} and threw {ACTOR_SELF} upon {ACTOR'S} guard."},
{Cmd.require: ["begin combat"], Cmd.remove: ["begin combat"], Cmd.add: ["in combat"], Cmd.action: "{ACTOR} said nothing at first but stood looking at {ANTAGONIST} with a grim face."},
{Cmd.require: ["begin combat"], Cmd.remove: ["begin combat"], Cmd.add: ["in combat"], Cmd.action: "Whatever {ACTOR} thought, {ACTOR} stood {ACTOR'S} ground, and now {ACTOR} and {ANTAGONIST} stood face to face."},
{Cmd.require: ["in combat"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}", "staggered {ACTOR}"], Cmd.add: ["attacking {TARGET}", "immediate {TARGET}"], Cmd.action: "{ACTOR} made a feint, and then delivered a blow at {ANTAGONIST} that, had it met its mark, would have tumbled {ANTAGONIST} speedily."},
{Cmd.require: ["in combat"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}", "staggered {ACTOR}"], Cmd.add: ["attacking {TARGET}", "immediate {TARGET}"], Cmd.action: "At last {ACTOR} saw {ACTOR'S} chance, and, throwing all the strength {ACTOR} felt going from {ACTOR_HIM} into one blow that might have felled an ox, {ACTOR} struck at {ANTAGONIST} with might and main."},
{Cmd.require: ["in combat", "attacking {ACTOR}", "stunned {ACTOR}"], Cmd.forbid: ["staggered {ACTOR}"], Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}", "in combat"], Cmd.add: ["fallen {TARGET}", "drop weapon {TARGET}", "end combat"], Cmd.action: "But {ACTOR} regained {ACTOR_SELF} quickly and, at arm's length, struck back a blow at {ANTAGONIST}, and this time the stroke reached its mark, and down went {ANTAGONIST} at full length, {ANTAGONIST'S} {ANTAGONIST_WEAPON} flying from {ANTAGONIST'S} hand as {ANTAGONIST} fell."},
{Cmd.require: ["in combat", "attacking {ACTOR}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.action: "{ACTOR} struck like a flash, and--\"rap!\"--{ANTAGONIST} met the blow and turned it aside, and then smote back at {ACTOR}, who also turned the blow."},
{Cmd.require: ["in combat", "attacking {ACTOR}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.action: "But {ACTOR} turned the blow right deftly and in return gave one as stout, which {ANTAGONIST} also turned as {ACTOR} had done."},
{Cmd.require: ["in combat", "attacking {ACTOR}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.action: "Thrice {ACTOR} struck {ANTAGONIST}; once upon the arm and twice upon the ribs, and yet {ACTOR} warded all the other's blows, only one of which, had it met its mark, would have laid {ACTOR} lower in the dust than {ACTOR} had ever gone before."},
{Cmd.require: ["in combat", "attacking {ACTOR}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["wound {TARGET}"], Cmd.action: "{ANTAGONIST} soon found that {ANTAGONIST} had met {ANTAGONIST'S} match, for {ACTOR} warded and parried all of the attacks, and, before {ANTAGONIST} thought, {ACTOR} gave {ANTAGONIST} a rap upon the ribs in return."},
{Cmd.require: ["in combat", "attacking {ACTOR}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["wound {TARGET}"], Cmd.action: "So shrewd was the stroke that {ACTOR} came within a hair's-breadth of falling, but {ACTOR} regained {ACTOR_SELF} right quickly and, by a dexterous blow, gave {ANTAGONIST} a crack on the crown that caused the blood to flow."},
{Cmd.require: ["in combat", "attacking {ACTOR}", "wound {TARGET}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}", "in combat"], Cmd.add: ["fallen {TARGET}", "end combat"], Cmd.action: "But {ACTOR} warded the blow and thwacked {ANTAGONIST}, and this time so fairly that {ANTAGONIST} fell heels over head, as the queen pin falls in a game of bowls."},
{Cmd.require: ["in combat", "attacking {ACTOR}", "wound {TARGET}"], Cmd.forbid: ["staggered {ACTOR}"],  Cmd.remove: ["attacking {ACTOR}", "immediate {ACTOR}", "in combat"], Cmd.add: ["fallen {TARGET}", "end combat"], Cmd.action: "In response, {ACTOR} struck {ANTAGONIST'S} {ANTAGONIST_WEAPON} so fairly in the middle that {ANTAGONIST} could hardly hold {ANTAGONIST'S} {ANTAGONIST_WEAPON} in {ANTAGONIST'S} hand; again {ACTOR} struck, and {ANTAGONIST} bent beneath the blow; a third time {ACTOR} struck, and now not only fairly beat down {ANTAGONIST'S} guard, but gave {ANTAGONIST} such a rap, also, that down {ANTAGONIST} tumbled."},
{Cmd.require: ["in combat", "attacking {TARGET}"], Cmd.remove: ["attacking {TARGET}", "immediate {TARGET}", "in combat"], Cmd.add: ["broken weapon {TARGET}", "end combat"], Cmd.action: "{ANTAGONIST} warded two of the strokes, but at the third, {ANTAGONIST'S} {ANTAGONIST_WEAPON} broke beneath the mighty blows of {ACTOR}."},
{Cmd.require: ["broken weapon {ACTOR}"], Cmd.forbid: ["end combat"], Cmd.remove: ["in combat"], Cmd.add: ["end combat"], Cmd.action: "\"Now, ill betide thee, traitor {ACTOR_WEAPON},\" cried {ACTOR}, as it fell from {ACTOR'S} hands; \"a foul {ACTOR_WEAPON} art thou to serve me thus in my hour of need.\""},
{Cmd.require: ["in combat", "attacking {TARGET}"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["staggered {TARGET}", "wound {TARGET}"], Cmd.action: "At last {ACTOR} gave {ANTAGONIST} a blow upon the ribs that made {ANTAGONIST'S} jacket smoke like a damp straw thatch in the sun."},
{Cmd.require: ["in combat", "attacking {TARGET}"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["staggered {TARGET}", "wound {TARGET}"], Cmd.action: "And now did {ANTAGONIST'S} {ANTAGONIST_ARMOR} stand {ANTAGONIST} in good stead, and but for it {ANTAGONIST} might never have held {ANTAGONIST_WEAPON} in hand again."},
{Cmd.require: ["in combat", "attacking {TARGET}"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["staggered {TARGET}", "wound {TARGET}"], Cmd.action: "As it was, the blow {ANTAGONIST} caught beside the head was so shrewd that it sent {ANTAGONIST} staggering, so that, if {ACTOR} had had the strength to follow up {ACTOR'S} vantage, it would have been ill for {ANTAGONIST}."},
{Cmd.require: ["in combat", "attacking {TARGET}"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["staggered {TARGET}", "wound {TARGET}"], Cmd.action: "Then, raising {ACTOR'S} {ACTOR_WEAPON}, {ACTOR} dealt {ANTAGONIST} a blow upon the ribs."},
# Emotion...
{Cmd.require: ["in combat", "wound {ACTOR}"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["anger {ACTOR}", "attacking {TARGET}", "immediate {TARGET}"], Cmd.action: "Then {ACTOR} grew mad with anger and smote with all {ACTOR'S} might at the other."},
{Cmd.require: ["in combat", "wound {ACTOR}"], Cmd.forbid: ["attacking {ACTOR}", "immediate {ACTOR}"], Cmd.add: ["anger {ACTOR}", "attacking {TARGET}", "immediate {TARGET}"], Cmd.action: "At this {ANTAGONIST} laughed aloud, and {ACTOR} grew more angry than ever, and smote again with all {ACTOR'S} might and main."},

# General back and forth
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: [], Cmd.action: "Well did {ACTOR} hold {ACTOR'S} own that day."},
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: [], Cmd.action: "This way and that they fought, and back and forth, {ACTOR'S} {ACTOR_ATTRIBUTE} against the {ANTAGONIST'S} {ANTAGONIST_ATTRIBUTE}."},
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: [], Cmd.action: "Then up and down and back and forth they trod, the blows falling so thick and fast that, at a distance, one would have thought that half a score were fighting."},
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: ["spent time"], Cmd.action: "Thus they fought for nigh a half an hour, until the ground was all plowed up with the digging of their heels, and their breathing grew labored like the ox in the furrow."},
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: [], Cmd.action: "The dust of the highway rose up around them like a cloud, so that at times the onlookers could see nothing, but only hear the {ACTOR_WEAPON_SOUND} of {ACTOR_WEAPON} against {ANTAGONIST_WEAPON}."},
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: ["spent time"], Cmd.action: "So they stood, each in their place, neither moving a finger's-breadth back, for one good hour, and many blows were given and received by each in that time, till here and there were sore bones and bumps, yet neither thought of crying \"Enough,\" nor seemed likely to fall."},
{Cmd.require: ["in combat"], Cmd.forbid: ["immediate {ACTOR}", "immediate {TARGET}", "staggered {ACTOR}"], Cmd.add: ["fatigue {TARGET}", "fatigue {ACTOR}"], Cmd.action: "Now and then they stopped to rest, and each thought that they never had seen in all their life before such a hand at {ACTOR_WEAPON} or {ANTAGONIST_WEAPON}."}

]

    
    
   

    