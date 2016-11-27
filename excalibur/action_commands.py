# -*- coding: utf-8 -*-

import collections
import functools
from enum import Enum
import numpy.random
import sys
from character import Character
from character import generatePirate
from character import generatePirateShip
from character import generateTheSea
import tracery
import uuid
import weakref
import copy

# For debugging...
from IPython.utils import coloransi
from IPython.core import prompts

class Cmd(Enum):
    current_actor = 1 # character currently acting, set dynamically
    current_target = 2 # object of the character's action, set dynamically
    action = 3
    prereq = 4
    effects = 5
    command = 6
    transcript = 7
    last_time = 999

def is_decay_in_efx(efx):
    if not isinstance(efx, str):
        return False
    return ("decay" in efx)


def buildTranslationTable(actor, target):
    ttable = []
    ("<ACTOR>", actor.name)
    ttable.append(["<ANTAGONIST>", target.name])
    ttable.append(["<ACTOR_WEAPON>", actor.weapon_name])
    ttable.append(["<ANTAGONIST_WEAPON>", target.weapon_name])
    ttable.append(["<TARGET_WEAPON>", target.weapon_name])
    ttable.append(["<ANTAGONIST'S>", target.possessive])
    ttable.append(["<TARGET>", target.name])
    ttable.append(["<TARGET'S>", target.possessive])
    ttable.append(["<ACTOR'S>", actor.possessive])
    ttable.append(["<TARGET_HIM>", target.him])
    ttable.append(["<ACTOR_HIM>", actor.him])
    ttable.append(["<ANTAGONIST_HER>", target.him])
    ttable.append(["<ANTAGONIST_HIM>", target.him])
    ttable.append(["<TARGET_HER>", target.him])
    ttable.append(["<ACTOR_HER>", actor.him])
    ttable.append(["<TARGET_SELF>", target.herself])
    ttable.append(["<TARGET_SELF>", target.herself])
    ttable.append(["<ACTOR_SELF>", actor.herself])
    # TODO: replace the following with actual lookups
    ttable.append(["<ACTOR_ATTRIBUTE>", "skill"])
    ttable.append(["<TARGET_ATTRIBUTE>", "strength"])
    ttable.append(["<ACTOR_WEAPON_SOUND>", "clank"])
    ttable.append(["<ANTAGONIST_ARMOR>", "leather cap"])
        
    

def translateActionDescription(action, specific_item = None):
    #print(action)
    #print(action.get(Cmd.current_actor))
    #print(specific_item)
    actor = action.get(Cmd.current_actor)
    target = action.get(Cmd.current_target)
    action_string = action.get(Cmd.action)
    if not (specific_item is None):
        action_string = specific_item
    if hasattr(action_string, "get"):
        if action_string.get(Cmd.transcript) != None:
            return action_string # TODO: handle nested transcriptions
    if (not isinstance(action_string, str)) or (not (hasattr(action_string, "replace"))):
        if isinstance(action_string, collections.Iterable):
            for asi in action_string:
                return translateActionDescription(action, asi)
        else:
            return action_string
    ttable = buildTranslationTable(actor, target)
    if not ttable is None:
        for trans in ttable:
            if not trans[1] is None:
                action_string = action_string.replace(trans[0], trans[1])
    
    # TODO: add lookups for ships and crew
    return action_string

class ActionProcessor:
    def __init__(self):
        self.queue = collections.deque()
        self._uuid = uuid.uuid4()
        self._parent = None
        self._initial_state = []
        
    def setInitialState(self, state):
        self._initial_state = state # TODO: include actor/target/character states
        
    def addAction(self, act):
        self.queue.append(act)
        # Commands are effects that operate on something other than 
        # the effects bag. They are expected to have side effects.
        # They also take effect immidiately, rather than being put
        # in the effects queue.
        if Cmd.command in act:
            for cmd_efx in act[Cmd.command]:
                self.executeCommand(cmd_efx)
                
    @property
    def parent(self):
        return self._parent
        
    @parent.setter
    def parent(self, newparent):
        self._parent = weakref.ref(newparent) 
            
    def currentState(self):
        """
        Runs the effects in the queue, returning the current collection of tags
        """
        effect_bag = collections.Counter()
        if self._initial_state:
            effect_bag.update(self._initial_state)
        for act in self.queue:
            if not act is None:
                if Cmd.effects in act:
                    for efx in act[Cmd.effects]:
                        get_effect_bag = efx({"action": act, "tags": effect_bag})
                        if not get_effect_bag is None:
                            effect_bag = get_effect_bag
                effect_bag = +effect_bag # remove zero and negative counts
                for efx in list(effect_bag): # some signals decay over time...
                    if is_decay_in_efx(efx):
                        effect_bag.subtract([efx])
                effect_bag = +effect_bag # remove zero and negative counts
                
        return effect_bag
        
    def executeCommand(self, command):
        command(weakref.ref(self))
        return # TODO: test to make sure this works as intended
        
    def sendToParentConflict(self, act):
        """
        Attempts to send the message to whichever conflict is a parent to
        the current conflict.
        """
        upper_parent = self.parent()._parent_conflict
        if upper_parent:
            upper_parent().addResolution(act)
    
    def currentTranscript(self):
        transcript = []
        for act in self.queue:
            if not act is None:
                transcript.append(translateActionDescription(act))
        return transcript
        
    def emitTranscript(self):
        charone = self.parent().char_one
        chartwo = self.parent().char_two
        return {Cmd.current_actor: copy.deepcopy(charone), Cmd.current_target: copy.deepcopy(chartwo), Cmd.transcript: copy.deepcopy(self.currentTranscript())}
        
                

def expandTag(tag, actor, target):
    if(isinstance(actor, int)):
        print(actor)
    if(isinstance(target, int)):
        print(target)
    tag = tag.replace("<ACTOR>", actor.getId())
    tag = tag.replace("<TARGET>", target.getId())
    tag = tag.replace("<ACTOR SHIP>", actor.ship_id)
    tag = tag.replace("{TARGET SHIP}", target.ship_id)
    return tag
    
def expandTagFromState(tag, state):
    """
    Returns the text of the tag, with the proper variables 
    filled in.
    
    If you get a KeyError, make sure that you're calling this
    from a state-query, and NOT from an action. Action EFX
    functions should use expandTagFromAction.
    """
    return expandTag(tag, state["actor"], state["target"])
    
def expandTagFromAction(tag, state):
    if state is None:
        return tag
    return expandTag(tag, state["action"][Cmd.current_actor], state["action"][Cmd.current_target])    
               
class Conflict:
    def __init__(self, action_catalog, protagonist, antagonist, initial_state = None):
        self._sub_conflicts = []
        self._parent_conflict = None
        self.char_one = protagonist#Character("Robin Hood")
        self.char_two = antagonist#Character("Sir Galahad")
        self.action_processor = ActionProcessor()
        self.action_processor.parent = self
        self.action_processor.setInitialState(initial_state)
        self.deck_of_actions = action_catalog
        #self.current_state = []
        self.actions_last_time = []
        for act in self.deck_of_actions:
            act.update({Cmd.last_time: 0.0})
        self._resolved = False
        #self._resolution_action = None
            
    def setInitialState(self, state):
        self.action_processor.setInitialState(state)
        
    @property
    def resolved(self):
        return self._resolved
        
    @resolved.setter
    def resolved(self, val):
        self._resolved = val
        
    def performAction(self, actor, target, action):
        action.update({Cmd.current_actor: actor, Cmd.current_target: target})
        print(action)
        self.action_processor.addAction(action)
        
    def addResolution(self, action):
        print(action)
        self.action_processor.addAction(action)
        
    def currentParentState(self):
        if self._parent_conflict is None:
            return self.currentState()
        return self._parent_conflict().currentParentState()
        
        
    def currentState(self):
        return self.currentTotalState()
        
    def currentSelfState(self):
        return self.action_processor.currentState()
        
    def currentChildState(self):
        """
        Returns the conflict-state of all the children sub-conflicts.
        """
        conflict_sum = collections.Counter()
        for sc in self._sub_conflicts:
            conflict_sum.update(sc.currentTotalState())
        return conflict_sum
        
    def currentTotalState(self):
        conflict_sum = self.currentSelfState()
        conflict_sum.update(self.currentChildState())
        return conflict_sum
        
    
    def currentTranscript(self):
        return self.action_processor.currentTranscript()
        
    def outputTranscript(self):
        return self.action_processor.emitTranscript()
        
    def prereqCheck(self, action, actor, target):
        if Cmd.prereq in action:
            for pre in action[Cmd.prereq]:
                if not pre({"conflict":weakref.ref(self), "actor": actor, "target": target}):
                    return False
        return True
        
    def pickNextAction(self, actor_num):
        acting = self.char_one
        targeting = self.char_two
        if actor_num != 1:
            acting = self.char_two
            targeting = self.char_one
        # filter actions...
        #state = self.currentState() #used for cache side effect
        live_deck = [act for act in self.deck_of_actions if self.prereqCheck(act, acting, targeting)]
        if len(live_deck) > 0:
            prob = [max(0.5, len(act[Cmd.prereq])) * (1.0 - act[Cmd.last_time]) for act in live_deck]
            psum = sum(prob)
            
            next_act = numpy.random.choice(live_deck, 1, False, [p / psum for p in prob])
            return next_act[0]
        return None
        
    def hideAction(self, action):
        idx = self.deck_of_actions.index(action)
        action.update({Cmd.last_time: 1.0})
        self.deck_of_actions[idx] = action

    def unhideActions(self):
        for idx, act in enumerate(self.deck_of_actions):
            last_time = act.get(Cmd.last_time)
            if last_time is None:
                last_time = 0.0
            act[Cmd.last_time] = last_time * 0.999
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
        
    def performChildActions(self):
        if len(self._sub_conflicts) <= 0:
            return False
        for sc in self._sub_conflicts:
            if sc.resolved:
                self.resolveChild(sc)
            else:
                sc.performActions()
        self._sub_conflicts = [sc for sc in self._sub_conflicts if (not sc.resolved)]
        return True
        
    def resolveChild(self, child_conflict):
        for act in child_conflict.resolution_action:
            self.performAction(act.get(Cmd.current_actor), act.get(Cmd.current_target), act)
        
            
        
    def performActions(self):
        if self.performChildActions():
            return # Only update this conflict once the subconflict has been resolved...
        self.performNextAction(0)
        self.performNextAction(1)
            
        
    def spawnSubconflict(self, conf):
        """
        Given a Conflict, add it to this conflict as a subconflict
        """
        conf._parent_conflict = weakref.ref(self)
        self._sub_conflicts.append(conf)

def getCurState(state):
    return state["conflict"]().currentParentState()

        
#def efx_resolve_conflict(state):
#    """
#    When the conflict is finished, finalize the results by propagating the
#    important state changes up to the parent conflict.
#    """
#    effects = state["tags"]
#    # TODO: implement conflict resolution
#    return effects
    
def cmd_efx_resolve_conflict(actproc):
    """
    When the conflict is finished, finalize the results by propagating the
    important state changes up to the parent conflict.
    """
    #actproc().parent().addTags(tags)
    actproc().parent().resolved = True
    return        
        
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

def WeighAnchor(conflict):
    conflict.performActions()
    print(conflict.currentState())
    print("===")
    
def is_ship(state):
    return state["actor"].isShip()
    
def is_sea(state):
    return state["actor"].isSea()
        
def in_combat(state):
    cur_tags = getCurState(state)
    if (expandTagFromState("end combat <ACTOR>", state) in cur_tags):
        return False
    if (expandTagFromState("begin combat <ACTOR>", state) in cur_tags):
        return False
    return (expandTagFromState("in combat <ACTOR>", state) in cur_tags)
    
def not_in_combat(state):
    cur_tags = getCurState(state)
    return not (expandTagFromState("in combat <ACTOR>", state) in cur_tags)

def if_end_combat(state):
    cur_tags = getCurState(state)
    return (expandTagFromState("end combat <ACTOR>", state) in cur_tags)
    
def not_end_combat(state):
    cur_tags = state["conflict"]().currentState()
    return not (expandTagFromState("end combat <ACTOR>", state) in cur_tags)

def can_proact(state):
    """
    Can be proactive: Returns true as long as the character doesn't have 
    something that would block taking action...
    """
    if not_in_combat(state):
        return False
    if incoming_attack(state):
        return False
    if is_offbalance_actor(state):
        return False
    return True
    
def can_attack(state):
    if not is_tag_count_positive("has weapon <ACTOR>", state):
        return False
    return can_proact(state)

def incoming_attack(state): # AKA "should parry", a necessary but not complete componet of "can parry"
    cur_tags = getCurState(state)
    if not in_combat(state):
        return False
    return (expandTagFromState("attacking <ACTOR>", state) in cur_tags)
    
def can_parry(state):
    if not incoming_attack(state):
        return False
    if is_offbalance_actor(state):
        return False
    return True
    
def is_tag_count_positive(tag, state):
    cur_tags = getCurState(state)
    if (expandTagFromState(tag, state) in cur_tags):
        return cur_tags[expandTagFromState(tag, state)] > 0

def is_staggered_actor(state):
    return is_tag_count_positive("staggered <ACTOR>", state)
    
def is_staggered_target(state):
    return is_tag_count_positive("staggered <TARGET>", state)

def is_wounded_actor(state):
    return is_tag_count_positive("wounded <ACTOR>", state)
    
def is_wounded_target(state):
    return is_tag_count_positive("wounded <TARGET>", state)

def not_is_wounded_actor(state):
    return not is_tag_count_positive("wounded <ACTOR>", state)
    
def not_is_wounded_target(state):
    return not is_tag_count_positive("wounded <TARGET>", state)
        
def is_fallen_actor(state):
    return is_tag_count_positive("fallen <ACTOR>", state)
    
def is_fallen_target(state):
    return is_tag_count_positive("fallen <TARGET>", state)

def is_offbalance_actor(state):
    """
    Offbalance is the general term for a status that needs to be recovered from.
    """
    if is_staggered_actor(state):
        return True
    if is_fallen_actor(state):
        return True
    return False
    
def target_vulnerable(state):
    """
    Returns True if the target can receive a winning blow.
    """
    if is_staggered_target(state):
        return True
    if is_wounded_target(state):
        return True
    return False
   
def target_broken_weapon(state):
    cur_tags = getCurState(state)
    return (expandTagFromState("broken weapon <TARGET>", state) in cur_tags)
    return False

def actor_broken_weapon(state):
    cur_tags = getCurState(state)
    return (expandTagFromState("broken weapon <ACTOR>", state) in cur_tags)
    return False
   
def respond_actor_broken_weapon(state):
    """
    Respond actions happen as immidiate priority responses...
    """
    cur_tags = getCurState(state)
    for tag in cur_tags:
        if ("signal broken weapon" in tag):
            return actor_broken_weapon(state)
    return False
    
def respond_start_combat(state):
    """
    Respond actions happen as immidiate priority responses...
    """
    cur_tags = getCurState(state)
    for tag in cur_tags:
        if "signal start combat" in tag:
            return not_in_combat(state)
    return False

    
def react_with_anger_actor(state):
    """
    Can react...
    Anger is an appropreate response...
    Actor can become angry...
    """
    return False # TODO

def efx_signal_start_combat(state):
    effects = state["tags"]
    effects.update(["signal start combat decay", "signal start combat decay"])
    return effects
    
def efx_signal_broken_weapon(state):
    effects = state["tags"]
    effects.update(["signal broken weapon"])
    return effects

def efx_signal_dropped_weapon(state):
    effects = state["tags"]
    effects.update(["signal dropped weapon"])
    return effects
    
def efx_begin_combat(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("in combat <ACTOR>", state)])
    effects.update([expandTagFromAction("in combat <TARGET>", state)])
    effects.update([expandTagFromAction("has weapon <ACTOR>", state)])
    effects.update([expandTagFromAction("has weapon <TARGET>", state)])
    return effects
    
def efx_attack_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("attacking <TARGET>", state)])
    return effects

def efx_knockdown_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("fallen <TARGET>", state)])
    return effects
    
def efx_knockdown_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("fallen <ACTOR>", state)])
    return effects
    
def efx_wound_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("wounded <TARGET>", state)])
    return effects
    
def efx_wound_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("wounded <ACTOR>", state)])
    return effects
    
def efx_stagger_target(state):
    effects = state["tags"]
    effects[expandTagFromAction("staggered <TARGET>", state)] = 0
    return effects
    
def efx_stagger_actor(state):
    effects = state["tags"]
    effects[expandTagFromAction("staggered <ACTOR>", state)] = 0
    return effects

def efx_break_weapon_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("broken weapon <TARGET>", state)])
    effects.update(["signal broken weapon"])
    effects.subtract([expandTagFromAction("has weapon <TARGET>", state)])
    effects = efx_signal_broken_weapon(state)
    return effects
    
def efx_drop_weapon_target(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("has weapon <TARGET>", state)])
    effects = efx_signal_dropped_weapon(state)
    return effects
    
def efx_break_weapon_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("broken weapon <ACTOR>", state)])
    effects.update(["signal broken weapon"])
    effects.subtract([expandTagFromAction("has weapon <ACTOR>", state)])
    effects = efx_signal_broken_weapon(state)
    return effects
    
def efx_recover_balance_actor(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("staggered <ACTOR>", state)])
    return effects

def efx_end_attack(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("attacking <ACTOR>", state)])
    return effects

def efx_parry(state):
    effects = state["tags"]
    effects = efx_end_attack(state)
    return effects

def efx_end_combat(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("end combat <ACTOR>", state)])
    effects.update([expandTagFromAction("end combat <TARGET>", state)])
    del effects[expandTagFromAction("in combat <ACTOR>", state)]
    del effects[expandTagFromAction("in combat <TARGET>", state)]
    return effects
    
def efx_emotion_anger_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("emotion <ACTOR>: anger", state)])
    return effects
    
def efx_clear_signal(state, signal):
    effects = state["tags"]
    effects[signal] = 0
    return effects

def efx_decay_signal(state, signal):
    effects = state["tags"]
    effects.subtract([signal])
    return effects
    
def efx_clear_signal_broken_weapon(state):
    return efx_clear_signal(state, "signal broken weapon")
    


swordfight_actcat = [
{Cmd.prereq: [not_in_combat, not_end_combat], Cmd.effects: [efx_signal_start_combat], Cmd.action: "{BEGIN: MELEE COMBAT}"},
{Cmd.prereq: [not_in_combat, if_end_combat], Cmd.effects: [], Cmd.command: [cmd_efx_resolve_conflict], Cmd.action: "{END: MELEE COMBAT}"},
#Begin
{Cmd.prereq: [not_in_combat, respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "In a moment <ACTOR> stepped quickly <UPON THE PLACE> where <ANTAGONIST> stood."},
{Cmd.prereq: [not_in_combat, respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "At last <ACTOR> struck like a flash, and--\"rap!\"--<ANTAGONIST> met the blow and turned it aside, and then smote back at <ACTOR>, who also turned the blow; and so this mighty battle began."},
{Cmd.prereq: [not_in_combat, respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "Then <ACTOR> spat upon <ACTOR'S> hands and, grasping <ACTOR'S> <ACTOR_WEAPON>, came straight at the other."},
{Cmd.prereq: [not_in_combat, respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "<ACTOR> gripped <ACTOR'S> <ACTOR_WEAPON> and threw <ACTOR_SELF> upon <ACTOR'S> guard."},
{Cmd.prereq: [not_in_combat, respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "<ACTOR> said nothing at first but stood looking at <ANTAGONIST> with a grim face."},
{Cmd.prereq: [not_in_combat, respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "Whatever <ACTOR> thought, <ACTOR> stood <ACTOR'S> ground, and now <ACTOR> and <ANTAGONIST> stood face to face."},
# Start Attack
{Cmd.prereq: [can_attack], Cmd.effects: [efx_attack_target], Cmd.action: "<PAR><ACTOR> made a feint, and then delivered a blow at <ANTAGONIST> that, had it met its mark, would have tumbled <ANTAGONIST> speedily."},
{Cmd.prereq: [can_attack], Cmd.effects: [efx_attack_target], Cmd.action: "<PAR>At last <ACTOR> saw <ACTOR'S> chance, and, throwing all the strength <ACTOR> felt going from <ACTOR_HIM> into one blow that might have felled an ox, <ACTOR> struck at <ANTAGONIST> with might and main."},
# Response, leading to knockdown of original attacker
{Cmd.prereq: [incoming_attack, is_offbalance_actor], Cmd.effects: [efx_knockdown_target, efx_recover_balance_actor, efx_drop_weapon_target], Cmd.action: "But <ACTOR> regained <ACTOR_SELF> quickly and, at arm's length, struck back a blow at <ANTAGONIST>, and this time the stroke reached its mark, and down went <ANTAGONIST> at full length, <ANTAGONIST'S> <ANTAGONIST_WEAPON> flying from <ANTAGONIST'S> hand as <ANTAGONIST> fell."},
# Back-and-forth stalemate
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "<ACTOR> struck like a flash, and--\"rap!\"--<ANTAGONIST> met the blow and turned it aside, and then smote back at <ACTOR>, who also turned the blow."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "But <ACTOR> turned the blow right deftly and in return gave one as stout, which <ANTAGONIST> also turned as <ACTOR> had done."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "Thrice <ACTOR> struck <ANTAGONIST>; once upon the arm and twice upon the ribs, and yet <ACTOR> warded all the other's blows, only one of which, had it met its mark, would have laid <ACTOR> lower in the dust than <ACTOR> had ever gone before."},
#Response, counterattack wounds original attacker
{Cmd.prereq: [can_parry], Cmd.effects: [efx_wound_target, efx_end_attack], Cmd.action: "<ANTAGONIST> soon found that <ANTAGONIST> had met <ANTAGONIST'S> match, for <ACTOR> warded and parried all of the attacks, and, before <ANTAGONIST> thought, <ACTOR> gave <ANTAGONIST> a rap upon the ribs in return."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_wound_target, efx_end_attack], Cmd.action: "So shrewd was the stroke that <ACTOR> came within a hair's-breadth of falling, but <ACTOR> regained <ACTOR_SELF> right quickly and, by a dexterous blow, gave <ANTAGONIST> a crack on the crown that caused the blood to flow."},
#Response, counterattack knocks down original attacker
{Cmd.prereq: [can_parry, target_vulnerable], Cmd.effects: [efx_knockdown_target, efx_end_attack], Cmd.action: "But <ACTOR> warded the blow and thwacked <ANTAGONIST>, and this time so fairly that <ANTAGONIST> fell heels over head, as the queen pin falls in a game of bowls."},
{Cmd.prereq: [can_parry, target_vulnerable], Cmd.effects: [efx_knockdown_target, efx_end_attack], Cmd.action: "In response, <ACTOR> struck <ANTAGONIST'S> <ANTAGONIST_WEAPON> so fairly in the middle that <ANTAGONIST> could hardly hold <ANTAGONIST'S> <ANTAGONIST_WEAPON> in <ANTAGONIST'S> hand; again <ACTOR> struck, and <ANTAGONIST> bent beneath the blow; a third time <ACTOR> struck, and now not only fairly beat down <ANTAGONIST'S> guard, but gave <ANTAGONIST> such a rap, also, that down <ANTAGONIST> tumbled."},
# Response: failed, weapon breaks
{Cmd.prereq: [can_parry, target_vulnerable], Cmd.effects: [efx_break_weapon_target], Cmd.action: "<ANTAGONIST> warded two of the strokes, but at the third, <ANTAGONIST'S> <ANTAGONIST_WEAPON> broke beneath the mighty blows of <ACTOR>."},
#React to broken weapon
{Cmd.prereq: [respond_actor_broken_weapon], Cmd.effects: [efx_end_combat, efx_clear_signal_broken_weapon], Cmd.action: "\"Now, ill betide thee, traitor <ACTOR_WEAPON>,\" cried <ACTOR>, as it fell from <ACTOR'S> hands; \"a foul <ACTOR_WEAPON> art thou to serve me thus in my hour of need.\""},
#Land a hit
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "At last <ACTOR> gave <ANTAGONIST> a blow upon the ribs that made <ANTAGONIST'S> jacket smoke like a damp straw thatch in the sun."},
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "And now did <ANTAGONIST'S> <ANTAGONIST_ARMOR> stand <ANTAGONIST> in good stead, and but for it <ANTAGONIST> might never have held <ANTAGONIST_WEAPON> in hand again."},
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "As it was, the blow <ANTAGONIST> caught beside the head was so shrewd that it sent <ANTAGONIST> staggering, so that, if <ACTOR> had had the strength to follow up <ACTOR'S> vantage, it would have been ill for <ANTAGONIST>."},
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "Then, raising <ACTOR'S> <ACTOR_WEAPON>, <ACTOR> dealt <ANTAGONIST> a blow upon the ribs."},
#Reaction: Emotion, leading to renewed attack
{Cmd.prereq: [react_with_anger_actor], Cmd.effects: [efx_emotion_anger_actor], Cmd.action: "Then <ACTOR> grew mad with anger and smote with all <ACTOR'S> might at the other."},
{Cmd.prereq: [react_with_anger_actor], Cmd.effects: [efx_emotion_anger_actor], Cmd.action: "At this <ANTAGONIST> laughed aloud, and <ACTOR> grew more angry than ever, and smote again with all <ACTOR'S> might and main."},
# General back and forth
{Cmd.prereq: [can_attack], Cmd.action: "Well did <ACTOR> hold <ACTOR'S> own that day."},
{Cmd.prereq: [can_attack], Cmd.action: "This way and that they fought, and back and forth, <ACTOR'S> <ACTOR_ATTRIBUTE> against the <ANTAGONIST'S> <TARGET_ATTRIBUTE>."},
{Cmd.prereq: [can_attack], Cmd.action: "Then up and down and back and forth they trod, the blows falling so thick and fast that, at a distance, one would have thought that half a score were fighting."},
{Cmd.prereq: [can_attack], Cmd.action: "Thus they fought for nigh a half an hour, until the ground was all plowed up with the digging of their heels, and their breathing grew labored like the ox in the furrow."},
{Cmd.prereq: [can_attack], Cmd.action: "The dust of the highway rose up around them like a cloud, so that at times the onlookers could see nothing, but only hear the <ACTOR_WEAPON_SOUND> of <ACTOR_WEAPON> against <ANTAGONIST_WEAPON>."},
{Cmd.prereq: [can_attack], Cmd.action: "So they stood, each in their place, neither moving a finger's-breadth back, for one good hour, and many blows were given and received by each in that time, till here and there were sore bones and bumps, yet neither thought of crying \"Enough,\" nor seemed likely to fall."},
{Cmd.prereq: [can_attack], Cmd.action: "Now and then they stopped to rest, and each thought that they never had seen in all their life before such a hand at <ACTOR_WEAPON> or <ANTAGONIST_WEAPON>."},
{Cmd.prereq: [is_fallen_actor, not_end_combat], Cmd.effects: [efx_end_combat], Cmd.action: "And so <ACTOR> was defeated by <ANTAGONIST'S> <ANTAGONIST_WEAPON>"},
# Friar Tuck
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "So, without more ado, they came together, and thereupon began a fierce and mighty battle."},
{Cmd.prereq: [can_attack], Cmd.action: "Right and left, and up and down and back and forth they fought."},
{Cmd.prereq: [can_attack], Cmd.action: "The <ACTOR_WEAPON> <ACTOR_WEAPON_VERB> and then met with a <ACTOR_WEAPON_SOUND> that sounded far and near."},
{Cmd.prereq: [can_attack], Cmd.action: "This was no playful bout, but a grim and serious fight of real earnest."},
{Cmd.prereq: [can_attack], Cmd.action: "Thus they strove for an hour or more, pausing every now and then to rest, at which times each looked at the other with wonder, and thought that never had they seen so stout a foe; then once again they would go at it more fiercely than ever."},
{Cmd.prereq: [can_attack, not_is_wounded_actor, not_is_wounded_target], Cmd.action: "Yet in all this time neither had harmed the other nor caused his blood to flow."},
# Beggar Riccon
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "Then <ACTOR> swung his <ACTOR_WEAPON> also, and struck a mighty blow at <TARGET>, which <TARGET> turned."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action:  "Three blows <TARGET> struck, yet never one touched so much as a hair of <ACTOR'S> head. "},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_knockdown_target, efx_drop_weapon_target], Cmd.action: "Then <ACTOR> saw <ACTOR'S> chance, and, ere you could count three, <TARGET'S> <TARGET_WEAPON> was flying away, and <TARGET> <TARGET_SELF> lay upon the <GROUND_DESCRIPTION> with no more motion than you could find in an empty pudding bag."}
]

def respond_start_weigh_anchor(state):
    cur_tags = getCurState(state)
    search_tag = expandTagFromState("signal start weigh anchor <ACTOR SHIP>", state)
    for tag in cur_tags:
        if search_tag in tag:
            return True
    return False

def respond_prepare_capstan(state):
    cur_tags = getCurState(state)
    search_tag = expandTagFromState("signal prepare capstan <ACTOR SHIP>", state)
    for tag in cur_tags:
        if search_tag in tag:
            return True
    return False

def if_anchor_aweigh(state):
    return is_tag_count_positive("anchor aweigh <ACTOR SHIP>", state)
    
def not_anchor_aweigh(state):
    return not is_tag_count_positive("anchor aweigh <ACTOR SHIP>", state)
    
def if_turning_capstan(state):
    return is_tag_count_positive("turning capstan <ACTOR SHIP>", state)

def if_weighing_anchor(state):
    return is_tag_count_positive("weighing anchor <ACTOR SHIP>", state)

def if_weighing_anchor_end(state):
    return is_tag_count_positive("weighing anchor end <ACTOR SHIP>", state)

def if_begin_weighing_anchor(state):
    return is_tag_count_positive("begin weighing anchor <ACTOR SHIP>", state)

#def begin_weighing_anchor(state):
#    return is_tag_count_positive("begin weighing anchor <ACTOR SHIP>", state)

def if_anchor_struggle(state):
    return is_tag_count_positive("anchor struggle <ACTOR SHIP>", state)

def not_turning_capstan(state):
    return not is_tag_count_positive("turning capstan <ACTOR SHIP>", state)

def not_weighing_anchor(state):
    return not is_tag_count_positive("weighing anchor <ACTOR SHIP>", state)

def not_weighing_anchor_end(state):
    return not is_tag_count_positive("weighing anchor end <ACTOR SHIP>", state)
    
def not_begin_weighing_anchor(state):
    return not is_tag_count_positive("begin weighing anchor <ACTOR SHIP>", state)
    
def not_anchor_struggle(state):
    return not is_tag_count_positive("anchor struggle <ACTOR SHIP>", state)
    
def is_tag_count_greater_than(tag, than, state):
    cur_tags = getCurState(state)
    if (expandTagFromState(tag, state) in cur_tags):
        return cur_tags[expandTagFromState(tag, state)] > than

def is_tag_count_less_than(tag, than, state):
    cur_tags = getCurState(state)
    #if (expandTagFromState(tag, state) in cur_tags):
    return cur_tags[expandTagFromState(tag, state)] < than
                        
def if_anchor_at_long_stay(state):
    if not is_tag_count_less_than("turning capstan <ACTOR SHIP>", 10, state):
        return False
    return is_tag_count_greater_than("turning capstan <ACTOR SHIP>", 8, state)

def if_anchor_at_short_stay(state):
    if not is_tag_count_less_than("turning capstan <ACTOR SHIP>", 7, state):
        return False
    return is_tag_count_greater_than("turning capstan <ACTOR SHIP>", 5, state)

def if_anchor_at_up_and_down(state):
    if not is_tag_count_less_than("turning capstan <ACTOR SHIP>", 4, state):
        return False
    return is_tag_count_greater_than("turning capstan <ACTOR SHIP>", 2, state)

def if_anchor_at_anchor_aweigh(state):
    return is_tag_count_less_than("turning capstan <ACTOR SHIP>", 2, state)
    
    

def efx_signal_start_weigh_anchor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("signal start weigh anchor <ACTOR SHIP>", state)])
    effects.update([expandTagFromAction("weighing anchor <ACTOR SHIP>", state)])
    effects.update([expandTagFromAction("begin weighing anchor <ACTOR SHIP>", state)])
    return effects
    
def efx_signal_prepare_capstan(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("signal prepare capstan <ACTOR SHIP>", state)])
    effects = efx_clear_signal(state, expandTagFromAction("signal start weigh anchor <ACTOR SHIP>", state))
    return effects
    
def efx_begin_turning_capstan(state):
    effects = state["tags"]
    effects[expandTagFromAction("turning capstan <ACTOR SHIP>", state)] = 12
    effects[expandTagFromAction("begin weighing anchor <ACTOR SHIP>", state)] = 0
    effects = efx_clear_signal(state, expandTagFromAction("signal prepare capstan <ACTOR SHIP>", state))
    return effects
    
def efx_turn_capstan(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("turning capstan <ACTOR SHIP>", state)])
    return effects
    
def efx_finish_turn_capstan(state):
    effects = state["tags"]
    effects[expandTagFromAction("turning capstan <ACTOR SHIP>", state)] = 0
    return effects
    
def efx_end_weigh_anchor(state):
    effects = state["tags"]
    effects[expandTagFromAction("turning capstan <ACTOR SHIP>", state)] = 0
    effects[expandTagFromAction("weighing anchor <ACTOR SHIP>", state)] = 0
    effects[expandTagFromAction("begin weighing anchor <ACTOR SHIP>", state)] = 0
    effects[expandTagFromAction("anchor aweigh <ACTOR SHIP>", state)] = 1
    effects[expandTagFromAction("weighing anchor end <ACTOR SHIP>", state)] = 1
    effects = efx_clear_signal(state, expandTagFromAction("weighing anchor <ACTOR SHIP>", state))
    return effects

def cmd_efx_anchor_aweigh(actproc):
    charone = actproc().parent().char_one
    chartwo = actproc().parent().char_two
    transcript = actproc().emitTranscript()
    act = {Cmd.effects: [lambda state: state["tags"] + collections.Counter([expandTag("anchor aweigh <ACTOR SHIP>", charone, chartwo)])],
           Cmd.action: transcript }
    actproc().sendToParentConflict(act)

    
# Crew vs Anchor
weigh_anchor_actcat = [
#Temp: an order to jumpstart the conflict
{Cmd.prereq: [is_ship, not_turning_capstan, not_weighing_anchor_end, not_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_signal_start_weigh_anchor], Cmd.action: "<BEGIN: WEIGH ANCHOR>"},
{Cmd.prereq: [is_ship, not_turning_capstan, not_weighing_anchor_end, if_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_signal_start_weigh_anchor], Cmd.action: "<BEGIN: WEIGH ANCHOR>"},
{Cmd.prereq: [is_ship, if_weighing_anchor_end, not_weighing_anchor, if_anchor_aweigh], Cmd.effects: [], Cmd.command: [cmd_efx_anchor_aweigh, cmd_efx_resolve_conflict], Cmd.action: "<END: WEIGH ANCHOR>"},
# clear the deck, make ready
{Cmd.prereq: [is_ship, not_turning_capstan, respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>The crew #adjectively# cleared the capstan and made ready to weigh anchor."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>The order was given, and soon the messenger was run out and the capstan manned."},
# capstan bars fitted to capstan
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "<Crewmember> fitted the bars, and the #sailors# took their positions around the capstan."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "<Crewmember> took the bars from where they were stowed, and the #sailors# fitted them to the capstan."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "\"Take your positions, you #sailors#,\" said <THE BOATSWAIN>."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "There came soon the familiar racket of making sail and trimming yards and the clank of the capstan pawls. "},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "The capstan bars were now fully manned."},
#pulling at the capstan
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The #sailors# pressed their broad chests against the powerful levers, planted their feet firmly upon the deck, straightened out their backs, and slowly pawl after pawl was gained."},
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "<PAR>\"That's your sort, my hearties,\" exclaimed <THE BOATSWAIN> encouragingly, as <THE BOATSWAIN> applied <THE BOATSWAIN'S> tremendous strength to the outer extremity of one of the bars, \"heave with a will! heave, and she _must_ come! _heave_, all of us!! now--one--_two_--three!!!\""},
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The #sailors# strained at the bars, the pawl clicking as they drove the capstan round."},
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The chorus of the shanty kept time with the clicks of the pawl."},
#sing a shanty
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: ["As the #sailors# turned the capstan, <THE BOATSWAIN> took up the verse and the crew repeated the chorus: <SHANTY>", "The crew sang in time with their work: <SHANTY>", "As was their practice, they sang to maintain the rhythm. <SHANTY>"]},
# straining, it goes slowly...
{Cmd.prereq: [is_ship, if_turning_capstan, if_anchor_struggle], Cmd.effects: [], Cmd.action: ["The anchor held fast, drawing line tighter and pulling the ship closer.", "The #sailors# strained against the wheel of the capstan, each rachet of the pawl a hard won fight."]},
# call out: at long stay / at short stay, up and down, anchors aweigh
{Cmd.prereq: [is_ship, if_turning_capstan, if_weighing_anchor, if_anchor_at_long_stay], Cmd.effects: [efx_turn_capstan], Cmd.action: "<PAR>#weigh_anchor_long_stay#"},
{Cmd.prereq: [is_ship, if_turning_capstan, if_weighing_anchor, if_anchor_at_short_stay], Cmd.effects: [efx_turn_capstan], Cmd.action: "<PAR>#weigh_anchor_short_stay#"},
{Cmd.prereq: [is_ship, if_turning_capstan, if_weighing_anchor, if_anchor_at_up_and_down], Cmd.effects: [efx_turn_capstan], Cmd.action: "<PAR>#weigh_anchor_up_and_down#"},
{Cmd.prereq: [is_ship, if_turning_capstan, if_weighing_anchor, if_anchor_at_anchor_aweigh], Cmd.effects: [efx_finish_turn_capstan], Cmd.action: "<PAR>#weigh_anchor_anchors_aweigh#"},
# catting the anchor
{Cmd.prereq: [is_ship, if_weighing_anchor, if_anchor_at_anchor_aweigh, not_begin_weighing_anchor, not_weighing_anchor_end], Cmd.effects: [efx_end_weigh_anchor], Cmd.action: "<PAR>#catting_1# #catting_2# #catting_3# #catting_4#"}
]

def cmd_efx_weigh_anchor(actproc):
    actor = actproc().parent().char_one
    target = actproc().parent().char_two
    subconflict = Conflict(weigh_anchor_actcat, actor, target, [expandTag("weighing anchor <ACTOR SHIP>", actor, target), expandTag("begin weighing anchor <ACTOR SHIP>", actor, target)])
    actproc().parent().spawnSubconflict(subconflict)
    return # TODO

def if_no_destination(state):
    cur_tags = getCurState(state)
    #print(cur_tags)
    finddest = expandTagFromState("destination <ACTOR>", state)
    curdest = None
    for tag in cur_tags:
        if finddest in tag:
            curdest = tag
    #print (curdest)
    #print((None == curdest))
    return (None == curdest)
    
def if_at_destination(state):
    cur_tags = getCurState(state)
    findloc = expandTagFromState("location <ACTOR>", state)
    finddest = expandTagFromState("destination <ACTOR>", state)
    curloc = None
    curdest = None
    for tag in cur_tags:
        if findloc in tag:
            curloc = tag
        if finddest in tag:
            curdest = tag
    if (None == curdest) or (None == curloc):
        return False    
    return (curdest.split(":",maxsplit=1)[1] == curloc.split(":",maxsplit=1)[1])
    
def not_at_destination(state):
    return not (if_at_destination(state))
    
def if_destination_overseas(state):
    return True # TODO: sometimes destinations can be on this island
    
def if_voyaging(state):
    return is_tag_count_positive("voyaging <ACTOR SHIP>", state)
    
def if_in_harbor(state):
    return is_tag_count_positive("in harbor <ACTOR SHIP>", state)

def not_in_harbor(state):
    return not is_tag_count_positive("in harbor <ACTOR SHIP>", state)
    
def efx_voyage_begins(state):
    effects = state["tags"]
    # TODO: change these temporary tag injections to reflect the actual current state of the ship
    effects = effects + collections.Counter([expandTagFromAction("destination <ACTOR SHIP>: NOMANISAN ISLAND", state)])
    effects = effects + collections.Counter([expandTagFromAction("in harbor <ACTOR SHIP>", state)])
    effects = effects + collections.Counter([expandTagFromAction("voyaging <ACTOR SHIP>", state)])
    return effects         

def efx_leave_harbor(state):
    effects = state["tags"]
    effects[expandTagFromAction("in harbor <ACTOR SHIP>", state)] = 0
    return effects
    
def efx_voyage_ends(state):
    effects = state["tags"]
    effects[expandTagFromAction("voyaging <ACTOR SHIP>", state)] = 0
    return effects
    
def efx_drop_anchor(state):
    effects = state["tags"]
    effects[expandTagFromAction("anchor aweigh <ACTOR SHIP>", state)] = 0
    return effects
    
def efx_enter_harbor(state):
    return state["tags"] + collections.Counter([expandTagFromAction("in harbor <ACTOR SHIP>", state)])
    
def efx_move_location_destination(state):
    """
    Destinations are specified by tags formatted as 
    "destination <ACTOR>: place_id". Locations use a similar
    format. This swaps them out.
    """
    effects = state["tags"]
    findloc = expandTagFromAction("location <ACTOR>", state)
    finddest = expandTagFromAction("destination <ACTOR>", state)
    curdest = None
    curloc = None
    for tag in effects:
        if findloc in tag:
            curloc = tag
        if finddest in tag:
            curdest = tag
    if not curdest is None:
        if not curloc is None:
            effects[curloc] = 0
        newloc = curdest.split(":",maxsplit=1)[1]
        effects.update(["{0}:{1}".format(expandTagFromAction("location <ACTOR>", state), newloc)])
    return effects
    
# Voyage: Ship vs. the Sea
actcat_ship_voyage = [
{Cmd.prereq: [is_ship, if_no_destination], Cmd.effects: [efx_voyage_begins], Cmd.action: "<TEMP: RANDOM DESTINATION>"},
# Start the voyage
{Cmd.prereq: [is_ship, not_at_destination, if_destination_overseas], Cmd.effects: [efx_voyage_begins], Cmd.action: "<VOYAGE: BEGIN_VOYAGE>"},
# Weigh Anchor
{Cmd.prereq: [is_ship, if_voyaging, not_weighing_anchor_end, not_at_destination, not_begin_weighing_anchor, not_weighing_anchor, not_anchor_aweigh], Cmd.effects: [], Cmd.command: [cmd_efx_weigh_anchor], Cmd.action: "<VOYAGE: WEIGH ANCHOR>"},
# Leave the harbor
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, if_in_harbor, not_at_destination], Cmd.effects: [efx_leave_harbor], Cmd.action: "<VOYAGE: LEAVE HARBOR>"},
# Sailing
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [efx_move_location_destination], Cmd.action: "<VOYAGE: SAILING>"},
# Perilous Journey
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: "<VOYAGE: PERILS AT SEA>"},
# Arrive at destination, enter harbor
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, if_at_destination], Cmd.effects: [efx_enter_harbor], Cmd.action: "<VOYAGE: ENTER HARBOR>"},
# Drop anchor
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, if_in_harbor, if_at_destination], Cmd.effects: [efx_drop_anchor], Cmd.action: "<VOYAGE: DROP ANCHOR>"},
 # Voyage over
{Cmd.prereq: [is_ship, if_voyaging, not_anchor_aweigh, if_in_harbor, if_at_destination], Cmd.effects: [efx_voyage_ends], Cmd.action: "<VOYAGE: END>"}
 ]

actcat_ship_leave_port = []

actcat_ship_grounded = [
#{Cmd.prereq: [respond_start_pull_off], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>With the anchor secured, the messenger was run out and the capstan manned."},                 
]


actcat_pirate_book = [
{Cmd.prereq: [], Cmd.command: [], Cmd.action: "The Voyages of <THE_CAPTAIN>, aboard #ship_name#"}
]

test_char_one = Character("Robin Hood")
test_char_two = Character("Little John")

def parseActionForResearch(action):
    action.update({Cmd.current_actor: test_char_one, Cmd.current_target: test_char_two})
    desc = translateActionDescription(action)
    desc.replace("<PAR>", "")
    desc.replace("<DIALOG>", "")
    return desc

def parseActionCatalog(action_catalog):
    return [parseActionForResearch(act) for act in action_catalog]
    
