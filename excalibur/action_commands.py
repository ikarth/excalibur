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
import traceback
import places

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
    injected = 900
    last_time = 999

def is_decay_in_efx(efx):
    if not isinstance(efx, str):
        return False
    return ("decay" in efx)

def findIdTagInState(tag, state):
    id_tag_list = []
    for i in state:
        if tag in i:
            #print(i.split(": ",1)[1])
            id_tag_list.append(i.split(": ",1)[1])
    if len(id_tag_list) > 0:
        return id_tag_list.pop()
    return None
    
    
def buildTranslationTable(actor, target, state=None):
    ttable = []
    if None != actor:
        ttable.append(["<ACTOR>", "<v_act_pronoun {0}>{1}|{2}</>".format(actor.uuid, actor.kenning, actor.she)])
        ttable.append(["<ACTOR_WEAPON>", "<v_actor_weapon {0}>{1}</>".format(actor.uuid, actor.weapon_name)])
        ttable.append(["<ACTOR'S>", "<v_actor_possessive {0}>{1}|{2}</>".format(actor.uuid, actor.possessive, actor.her)])
        ttable.append(["<ACTOR_HIM>", "<v_actor_pronoun {0}>{1}</>".format(actor.uuid, actor.him)])
        ttable.append(["<ACTOR_HER>", "<v_actor_pronoun {0}>{1}</>".format(actor.uuid, actor.him)])
        ttable.append(["<ACTOR_SELF>", "<v_actor_reflexive {0}>{1}</>".format(actor.uuid, actor.herself)])
        ttable.append(["<ACTOR_ATTRIBUTE>", actor.attribute])
        ttable.append(["<ACTOR_WEAPON_SOUND>", actor.weapon_sound])
    if None != target:
        #TODO: move these to Transcript, expand handling
        ttable.append(["<ANTAGONIST>", "<v_target_pronoun {0}>{1}|{2}</>".format(target.uuid, target.name, target.kennings)])
        ttable.append(["<ANTAGONIST_WEAPON>", "<v_target_weapon {0}>{1}</>".format(target.uuid, target.weapon_name)])
        ttable.append(["<TARGET_WEAPON>", "<v_target_weapon {0}>{1}</>".format(target.uuid, target.weapon_name)])
        ttable.append(["<ANTAGONIST'S>", "<v_target_possessive {0}>{1}|{2}</>".format(target.uuid, target.possessive,target.her)])
        ttable.append(["<TARGET>", "<v_target_pronoun {0}>{1}|{2}</>".format(target.uuid, target.name, target.she)])
        ttable.append(["<TARGET'S>", "<v_target_possessive {0}>{1}</>".format(target.uuid, target.possessive,target.her)])
        ttable.append(["<TARGET_HIM>", "<v_target_pronoun {0}>{1}</>".format(target.uuid, target.him)])
        ttable.append(["<ANTAGONIST_HER>", "<v_target_pronoun {0}>{1}</>".format(target.uuid, target.him)])
        ttable.append(["<ANTAGONIST_HIM>", "<v_target_pronoun {0}>{1}</>".format(target.uuid, target.him)])
        ttable.append(["<TARGET_HER>", "<v_target_pronoun {0}>{1}</>".format(target.uuid, target.him)])
        ttable.append(["<ANTAGONIST_SELF>", "<v_target_reflexive {0}>{1}</>".format(target.uuid, target.herself)])
        ttable.append(["<TARGET_SELF>", "<v_target_reflexive {0}>{1}</>".format(target.uuid, target.herself)])
        ttable.append(["<ANTAGONIST_ARMOR>", target.armor])
        ttable.append(["<TARGET_ARMOR>", target.armor])
        ttable.append(["<TARGET_ATTRIBUTE>", target.attribute])


    if None != state:
        ttable.append(["<DESCRIBE: LOCATION NAME>", 
                       places.getPlaceName(places.findPlaceById(findIdTagInState(expandTag("location <ACTOR SHIP>: ", actor, target), state)))])
        ttable.append(["<DESCRIBE: LOCATION DESCRIPTION>", 
                       places.getPlaceDescription(places.findPlaceById(findIdTagInState(expandTag("location <ACTOR SHIP>: ", actor, target), state)))])
        ttable.append(["<DESCRIBE: DESTINATION NAME>", 
                       places.getPlaceName(places.findPlaceById(findIdTagInState(expandTag("destination <ACTOR SHIP>: ", actor, target), state)))])
        ttable.append(["<DESCRIBE: DESTINATION DESCRIPTION>", 
                       places.getPlaceDescription(places.findPlaceById(findIdTagInState(expandTag("destination <ACTOR SHIP>: ", actor, target), state)))])
    return ttable
        
    

def translateActionDescription(action, specific_item=None, state=None):
    #print(action)
    #print(action.get(Cmd.current_actor))
    #print(specific_item)
    actor = action.get(Cmd.current_actor)
    target = action.get(Cmd.current_target)
    action_string = action.get(Cmd.action)
    if (specific_item != None):
        action_string = specific_item
    if hasattr(action_string, "get"):
        if action_string.get(Cmd.transcript) != None:
            return action_string # TODO: handle nested transcriptions
    if (not isinstance(action_string, str)) or (not (hasattr(action_string, "replace"))):
        if isinstance(action_string, collections.Iterable):
            asi = numpy.random.choice(action_string) # TODO: make determanistic
            #for asi in action_string:
            return translateActionDescription(action, asi)
        else:
            return action_string
    ttable = buildTranslationTable(actor, target, state)
    if not ttable == None:
        for trans in ttable:
            if not None == trans:
                if not trans[1] == None:
                    action_string = action_string.replace(trans[0], trans[1])
    
    # TODO: add lookups for ships and crew
    return action_string

class ActionProcessor:
    def __init__(self):
        self.queue = collections.deque()
        self._uuid = uuid.uuid4()
        self._parent = None
        self._initial_state = []
        self.__debugging_counter = 0
        self.__internal_action_counter = 0
        
    def setInitialState(self, state):
        self._initial_state = state # TODO: include actor/target/character states
        
    def addAction(self, act):
        newact = copy.deepcopy(act)
        self.__internal_action_counter += 1
        newact["internal_id"] = str(uuid.uuid4()) + "_" + str(self.__internal_action_counter)
        self.queue.append(newact)
        # Commands are effects that operate on something other than 
        # the effects bag. They are expected to have side effects.
        # They also take effect immidiately, rather than being put
        # in the effects queue.
        if Cmd.command in newact:
            for cmd_efx in newact[Cmd.command]:
                self.executeCommand(cmd_efx)
                
    @property
    def parent(self):
        return self._parent
        
    @parent.setter
    def parent(self, newparent):
        self._parent = weakref.ref(newparent) 
            
    def currentState(self, stop=None):
        """
        Runs the effects in the queue, returning the current collection of tags
        """
        self.__debugging_counter += 1
        stop_next = 0 # skip ahead one more action, because we injected one...
        effect_bag = collections.Counter()
        if self._initial_state:
            effect_bag.update(self._initial_state)
        for act in self.queue:
            if act != None:
                if Cmd.effects in act:
                    for efx in act[Cmd.effects]:
                        get_effect_bag = efx({"action": act, "tags": effect_bag})
                        if get_effect_bag != None:
                            effect_bag = get_effect_bag
                effect_bag = +effect_bag # remove zero and negative counts
                for efx in list(effect_bag): # some signals decay over time...
                    if is_decay_in_efx(efx):
                        effect_bag.subtract([efx])
                effect_bag = +effect_bag # remove zero and negative counts
                if None != stop:
                    if stop_next > 0:
                        if not(Cmd.injected in act):
                            #print(effect_bag)
                            return effect_bag # return early with a partial result
                    #print(act.get("internal_id"))
                    #print(stop.get("internal_id"))
                    if act.get("internal_id") == stop.get("internal_id"):
                        #print("----compare IDs: {0} ----".format(self.__debugging_counter))
                        #print(act)
                        #print(effect_bag)
                        stop_next += 1

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
            if act != None:
                transcript.append(translateActionDescription(act, state=self.currentState(act)))
        return transcript
        
    def emitTranscript(self):
        charone = self.parent().char_one
        chartwo = self.parent().char_two
        return {Cmd.current_actor: copy.deepcopy(charone), Cmd.current_target: copy.deepcopy(chartwo), Cmd.transcript: copy.deepcopy(self.currentTranscript())}
        
                

def expandTag(tag, actor, target):
    #if(isinstance(actor, int)):
    #    print(actor)
    #if(isinstance(target, int)):
    #    print(target)
    if None != actor:
        tag = tag.replace("<ACTOR>", actor.getId())
        tag = tag.replace("<ACTOR SHIP>", actor.ship_id)
    if None != target:
        tag = tag.replace("<TARGET>", target.getId())
        tag = tag.replace("<TARGET SHIP>", target.ship_id)
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
    if state == None:
        return tag
    return expandTag(tag, state["action"][Cmd.current_actor], state["action"][Cmd.current_target])    

explain_conflict = False
               
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
        if explain_conflict:
            print(action)
        self.action_processor.addAction(action)
        
    def addResolution(self, action):
        if explain_conflict:
            print(action)
        self.action_processor.addAction(action)
        
    def currentParentState(self):
        if self._parent_conflict == None:
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
        
    def prereqCheck(self, action, actor, target, explain=False):
        if self.resolved:
            return False
        if Cmd.prereq in action:
            for pre in action[Cmd.prereq]:
                pre_state = pre({"conflict":weakref.ref(self), "actor": actor, "target": target})
                if explain:
                    print("{0}: {2}\t{1}".format(pre_state, str(pre), str(pre.__name__)))
                if not pre_state:
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
            if explain_conflict:
                print("No Action")
            return # todo: unwind to last branch
        self.performAction(acting, targeting, next_action)
        self.hideAction(next_action) # this action has been spent. 
        # Remove it from consideration until later...
        
    def debugNextAction(self, actor_num):
        print(self.currentState())
        acting = self.char_one
        targeting = self.char_two
        if actor_num != 1:
            acting = self.char_two
            targeting = self.char_one
        for act in self.deck_of_actions:
            self.prereqCheck(act, acting, targeting, explain=True)
        
        
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
    #print("---")
    #print(conflict.currentState())
    #print("===")
    conflict.performNextAction(1)
    #conflict.currentTranscript()
    #print("---")
    #print(conflict.currentState())
    #print("===")
    return

def WeighAnchor(conflict):
    conflict.performActions()
    #print(conflict.currentState())
    #print("===")
    
def is_ship(state):
    return state["actor"].isShip()
    
def is_sea(state):
    return state["actor"].isSea()

def if_crew_busy(state):
    return False # TODO: properly detect if the crew is already engaged in doing something else (such as firing the canons)
    
def not_crew_busy(state):
    return not if_crew_busy(state)

    
def if_rushed_for_time(state):
    return False # TODO: properly detect if we're rushed for time, i.e. under fire, in a storm, etc.
    
def not_rushed_for_time(state):
    return not if_rushed_for_time(state)
        
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
        if cur_tags[expandTagFromState(tag, state)] > 0:
            return True
    return False
        
def compare_tag_count(tag1, tag2, state):
    cur_tags = getCurState(state)
    if (expandTagFromState(tag1, state) in cur_tags):
        if (expandTagFromState(tag2, state) in cur_tags):
            one = cur_tags[expandTagFromState(tag1, state)]
            two = cur_tags[expandTagFromState(tag2, state)]
            if None == one:
                one = 0
            if None == two:
                two = 0
            return one - two

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
    tag_change = collections.Counter([expandTag("anchor aweigh <ACTOR SHIP>", charone, chartwo)])
    tag_change[expandTag("anchors moored <ACTOR SHIP>", charone, chartwo)] = -9 # TODO: Updated weighing anchor to take into account multiple mooring anchors
    #print(anchor_count)
    act = {Cmd.effects: [lambda state: state["tags"] + tag_change],
           Cmd.action: transcript }
    actproc().sendToParentConflict(act)

    
# Crew vs Anchor
weigh_anchor_actcat = [
#Temp: an order to jumpstart the conflict
{Cmd.prereq: [is_ship, not_turning_capstan, not_weighing_anchor_end, not_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_signal_start_weigh_anchor], Cmd.action: "<BEGIN: WEIGH ANCHOR>"},
{Cmd.prereq: [is_ship, not_turning_capstan, not_weighing_anchor_end, if_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_signal_start_weigh_anchor], Cmd.action: "<BEGIN: WEIGH ANCHOR>"},
{Cmd.prereq: [is_ship, if_weighing_anchor_end, not_weighing_anchor, if_anchor_aweigh], Cmd.effects: [], Cmd.command: [cmd_efx_anchor_aweigh, cmd_efx_resolve_conflict], Cmd.action: "<END: WEIGH ANCHOR>"},
# clear the deck, make ready
{Cmd.prereq: [is_ship, not_turning_capstan, respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>The crew dutifully cleared the capstan and made ready to weigh anchor."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>The order was given, and soon the messenger was run out and the capstan manned."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>The capstan was made ready. The bars unstowed, the #sailors# took up the preparation of unmooring the #ship#."},
# capstan bars fitted to capstan
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "<Crewmember.capitalize> fitted the bars, and the #sailors# took their positions around the capstan."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "<Crewmember.capitalize> took the bars from where they were stowed, and the #sailors# fitted them to the capstan."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "\"Take your positions, you #sailors#,\" said <THE BOATSWAIN>."},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "There came soon the familiar racket of making sail and trimming yards and the clank of the capstan pawls. "},
{Cmd.prereq: [is_ship, not_turning_capstan, respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "The capstan bars were now fully manned."},
#pulling at the capstan
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The #sailors# pressed their broad chests against the powerful levers, planted their feet firmly upon the deck, straightened out their backs, and slowly pawl after pawl was gained."},
{Cmd.prereq: [is_ship, if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "<PAR>\"That's your sort, my hearties,\" exclaimed <THE BOATSWAIN> encouragingly, as <THE BOATSWAIN SHE> applied <THE BOATSWAIN'S> tremendous strength to the outer extremity of one of the bars, \"heave with a will! heave, and she _must_ come! _heave_, all of us!! now--one--_two_--three!!!\""},
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
    
def cmd_efx_drop_anchor(actproc):
    actor = actproc().parent().char_one
    target = actproc().parent().char_two
    # TODO: check harbor conditions to see how many mooring anchors should be dropped
    subconflict = Conflict(actcat_ship_drop_anchor, actor, target, [expandTag("mooring ship <ACTOR SHIP>", actor, target), expandTag("mooring anchors needed <ACTOR SHIP>", actor, target), expandTag("mooring anchors needed <ACTOR SHIP>", actor, target)])
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
    #print("x=y?")
    #print(curdest.split(":",maxsplit=1)[1])
    #print(curloc.split(":",maxsplit=1)[1])
    return (curdest.split(":",maxsplit=1)[1] == curloc.split(":",maxsplit=1)[1])
    
def not_at_destination(state):
    return not (if_at_destination(state))
    
def if_destination_overseas(state):
    return True # TODO: sometimes destinations can be on this island
    
def if_voyaging(state):
    return is_tag_count_positive("voyaging <ACTOR SHIP>", state)
    
def not_voyaging(state):
    return not if_voyaging(state)

def if_voyaging_canceled(state):
    return is_tag_count_positive("voyaging canceled <ACTOR SHIP>", state)
    
def if_in_harbor(state):
    return is_tag_count_positive("in harbor <ACTOR SHIP>", state)

def not_in_harbor(state):
    return not is_tag_count_positive("in harbor <ACTOR SHIP>", state)
    
def efx_voyage_begins(state):
    effects = state["tags"]
    # TODO: change these temporary tag injections to reflect the actual current state of the ship
    #effects = effects + collections.Counter([expandTagFromAction("in harbor <ACTOR SHIP>", state)])
    effects = effects + collections.Counter([expandTagFromAction("voyaging <ACTOR SHIP>", state)])
    return effects         
    
def efx_temp_voyage_start(state):
    effects = state["tags"]
    # TODO: change these temporary tag injections to reflect the actual current state of the ship
    effects = effects + collections.Counter([expandTagFromAction("in harbor <ACTOR SHIP>", state)])
    #effects = effects + collections.Counter([expandTagFromAction("voyaging <ACTOR SHIP>", state)])
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
    findloc = expandTagFromAction("location <ACTOR SHIP>", state)
    finddest = expandTagFromAction("destination <ACTOR SHIP>", state)
    curdest = None
    curloc = None
    for tag in effects:
        if findloc in tag:
            curloc = tag
        if finddest in tag:
            curdest = tag
    if curdest != None:
        #print("DEST " + str(curdest))
        #print("LOC  " + str(curloc))
        if curloc != None:
            effects[curloc] = 0
        newloc = curdest.split(":",maxsplit=1)[1]
        effects.update(["{0}:{1}".format(expandTagFromAction("location <ACTOR SHIP>", state), newloc)])
        #print(["{0}:{1}".format(expandTagFromAction("location <ACTOR>", state), newloc)])
    
    return effects

def cmd_efx_end_mooring_ship(actproc):
    charone = actproc().parent().char_one
    chartwo = actproc().parent().char_two
    transcript = actproc().emitTranscript()
    tag_change = collections.Counter()
    tag_change[expandTag("anchor aweigh <ACTOR SHIP>", charone, chartwo)] = -1
    anchor_count = actproc().currentState().get(expandTag("anchors moored <ACTOR SHIP>", charone, chartwo))
    #print(anchor_count)
    tag_change[expandTag("anchors moored <ACTOR SHIP>", charone, chartwo)] = anchor_count
    act = {Cmd.effects: [lambda state: state["tags"] + tag_change],
           Cmd.action: transcript }
    actproc().sendToParentConflict(act)    
   
def cmd_efx_set_random_destination(actproc):
    actor = actproc().parent().char_one
    target = actproc().parent().char_two
    effects = actproc().currentState()
    tag_change_plus = collections.Counter()
    tag_change_minus = collections.Counter()
    # clear destination...
    finddest = expandTag("destination <ACTOR SHIP>", actor, target)
    #print("finddest")
    #print(finddest)
    
    for tag in effects:
        if finddest in tag:
            #print("change tag")
            #print(tag)
            tag_change_minus[tag] = 99
    dest = places.getRandomDestination()
    destination_id = "destination <ACTOR SHIP>: {0}".format(places.getPlaceId(dest))
    tag_change_plus = tag_change_plus + collections.Counter([expandTag(destination_id, actor, target)])
    tag_change_cp = copy.deepcopy(tag_change_plus)
    act = {Cmd.effects: [lambda state: (state["tags"] - tag_change_minus) + tag_change_cp],
           Cmd.action: "",
           Cmd.injected: True}
    #print("---act---")
    #print(act)
    actproc().addAction(act)
    
def cmd_efx_set_random_location(actproc):
    actor = actproc().parent().char_one
    target = actproc().parent().char_two
    effects = actproc().currentState()
    tag_change_plus = collections.Counter()
    tag_change_minus = collections.Counter()
    # clear destination...
    finddest = expandTag("location <ACTOR SHIP>", actor, target)
    #print("find_loc")
    #print(finddest)
    
    for tag in effects:
        if finddest in tag:
            #print("change tag")
            #print(tag)
            tag_change_minus[tag] = 99
    dest = places.getRandomDestination()
    destination_id = "location <ACTOR SHIP>: {0}".format(places.getPlaceId(dest))
    tag_change_plus = tag_change_plus + collections.Counter([expandTag(destination_id, actor, target)])
    tag_change_cp = copy.deepcopy(tag_change_plus)
    act = {Cmd.effects: [lambda state: (state["tags"] - tag_change_minus) + tag_change_cp],
           Cmd.action: "",
           Cmd.injected: True}
    #print("---act---")
    #print(act)
    actproc().addAction(act)
    
def if_enough_anchors(state):
    compare = compare_tag_count("mooring anchors needed <ACTOR SHIP>", "anchors moored <ACTOR SHIP>", state)
    if None == compare:
        return not is_tag_count_positive("mooring anchors needed <ACTOR SHIP>", state)
    return (compare <= 0)

def efx_temp_skip_weigh_anchor(state):
    effects = state["tags"]
    effects[expandTagFromAction("anchor aweigh <ACTOR SHIP>", state)] = 1
    effects[expandTagFromAction("anchors moored <ACTOR SHIP>", state)] = 0
    return effects
 
    
# efx_set_random_destination, efx_clear_location, efx_set_random_location        
# Voyage: Ship vs. the Sea
actcat_ship_voyage = [
{Cmd.prereq: [is_ship, not_voyaging, if_no_destination], Cmd.effects: [efx_temp_voyage_start], Cmd.command: [cmd_efx_set_random_location, cmd_efx_set_random_destination], Cmd.action: ""},
# Start the voyage
{Cmd.prereq: [is_ship, not_voyaging, if_in_harbor, not_at_destination, if_destination_overseas], Cmd.effects: [efx_voyage_begins], Cmd.action: "<VOYAGE: BEGIN_VOYAGE>"},
# Weigh Anchor
{Cmd.prereq: [is_ship, if_voyaging, not_weighing_anchor_end, not_at_destination, not_begin_weighing_anchor, not_weighing_anchor, not_anchor_aweigh], Cmd.effects: [], Cmd.command: [cmd_efx_weigh_anchor], Cmd.action: "<PAR>They made ready to leave <DESCRIBE: LOCATION NAME> and sail to <DESCRIBE: DESTINATION NAME>.<VOYAGE: WEIGH ANCHOR><PAR>"},
#{Cmd.prereq: [is_ship, if_voyaging, not_weighing_anchor_end, not_at_destination, not_begin_weighing_anchor, not_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_temp_skip_weigh_anchor], Cmd.command: [], Cmd.action: "<PAR>They made ready to leave <DESCRIBE: LOCATION NAME> and sail to <DESCRIBE: DESTINATION NAME>.<PAR> <VOYAGE: WEIGH ANCHOR><PAR>"},
# Leave the harbor
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, if_in_harbor, not_at_destination], Cmd.effects: [efx_leave_harbor], Cmd.action: "<VOYAGE: LEAVE HARBOR><PAR>"},
# Sailing
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [efx_move_location_destination], Cmd.action: "<VOYAGE: SAILING>"},
# Perilous Journey
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: "<VOYAGE: PERILS AT SEA><PAR>"},
# Perilous Journey
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: "<VOYAGE: PERILS AT SEA><PAR>"},
# Arrive at destination, enter harbor
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, if_at_destination], Cmd.effects: [efx_enter_harbor], Cmd.action: "<VOYAGE: ENTER HARBOR><PAR>They had arrived at <DESCRIBE: LOCATION NAME>.<PAR><DESCRIBE: LOCATION DESCRIPTION>"},
# Drop anchor
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, if_in_harbor, if_at_destination], Cmd.effects: [], Cmd.command: [cmd_efx_drop_anchor], Cmd.action: "<VOYAGE: DROP ANCHOR><PAR>"},
#{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, if_in_harbor, if_at_destination], Cmd.effects: [efx_drop_anchor], Cmd.command: [], Cmd.action: "<VOYAGE: DROP ANCHOR><PAR>"},
 # Voyage over
{Cmd.prereq: [is_ship, if_voyaging, not_anchor_aweigh, if_in_harbor, if_at_destination], Cmd.effects: [efx_voyage_ends], Cmd.action: "<VOYAGE: END>"},
{Cmd.prereq: [is_ship, not_voyaging, if_enough_anchors, not_anchor_aweigh, if_in_harbor, if_at_destination], Cmd.effects: [efx_voyage_begins], Cmd.command: [cmd_efx_set_random_destination], Cmd.action: "<VOYAGE: RESTART>"},
{Cmd.prereq: [is_ship, if_voyaging, if_voyaging_canceled], Cmd.effects: [efx_voyage_ends], Cmd.action: "<VOYAGE: CANCELED>"},

#sunrise    
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: [
"<PAR>Much has been said of the sunrise at sea; but it will not compare with the sunrise on shore. It lacks the accompaniments of the songs of birds, the awakening hum of humanity, and the glancing of the first beams upon trees, hills, spires, and house-tops, to give it life and spirit. There is no scenery. But, although the actual rise of the sun at sea is not so beautiful, yet nothing will compare for melancholy and dreariness with the early breaking of day upon \"Old Ocean's gray and melancholy waste.\"<PAR>",
"<PAR>There is something in the first gray streaks stretching along the eastern horizon and throwing an indistinct light upon the face of the deep, which combines with the boundlessness and unknown depth of the sea around, and gives one a feeling of loneliness, of dread, and of melancholy foreboding, which nothing else in nature can. This gradually passes away as the light grows brighter, and when the sun comes up, the ordinary monotonous sea day begins.<PAR>"
]},
#sailing 
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: [
"With a favorable wind, they proceeded eastward for three days, and then they encountered a great wind. ",
"On the sea hereabouts there are many pirates, to meet with whom is speedy death. ",
"The great ocean spreads out, a boundless expanse. ",
"There is no knowing east or west; only by observing the sun, moon, and stars was it possible to go forward. ",
"The sea was deep and bottomless, and there was no place where they could drop anchor and stop. "]},
# overcast, no navigation...
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: [
"If the weather were dark and rainy, the ship went as she was carried by the wind, without any definite course. ",
"In the darkness of the night, only the great waves were to be seen, breaking on one another, and emitting a brightness like that of fire, with huge turtles and other monsters of the deep all about. ",
"But when the sky became clear, they could tell east and west, and the ship again went forward in the right direction. ",
"If she had come on any hidden rock, there would have been no way of escape.",
"At this time the sky continued very dark and gloomy, and the sailing-masters looked at one another and made mistakes. "]},
# clear skies
{Cmd.prereq: [is_ship, if_voyaging, if_anchor_aweigh, not_in_harbor, not_at_destination], Cmd.effects: [], Cmd.action: [
"The sky presented a clear expanse of the most delicate blue, except along the skirts of the horizon, where you might see a thin drapery of pale clouds which never varied their form or colour. ",
"The long, measured, dirge-like well of the #ocean_sea_name# came rolling along, with its surface broken by little tiny waves, sparkling in the sunshine. ",
"Every now and then a shoal of flying fish, scared from the water under the bows, would leap into the air, and fall the next moment like a shower of silver into the sea. ",
"Then you would see the superb albicore, with his glittering sides, sailing aloft, and often describing an arc in his descent, disappear on the surface of the water. ",
"Far off, the lofty jet of the whale might be seen, and nearer at hand the prowling shark, that villainous footpad of the seas, would come skulking along, and, at a wary distance, regard us with his evil eye. ",
"At times, some shapeless monster of the deep, floating on the surface, would, as we approached, sink slowly into the blue waters, and fade away from the sight. ",
"But the most impressive feature of the scene was the almost unbroken silence that reigned over sky and water. ",
"Scarcely a sound could be heard but the occasional breathing of the grampus, and the rippling at the cut-water. "]},

 ]

actcat_ship_leave_port = []
#The anchor catted, and the mainsail unfurled, they stood out for the open before a gentle breeze, without interference from the fort.

actcat_ship_arrive_port = []

def if_mooring_ship(state):
    return is_tag_count_positive("mooring ship <ACTOR SHIP>", state)

def if_begin_mooring(state):
    return is_tag_count_positive("begin mooring <ACTOR SHIP>", state)
    
def not_begin_mooring(state):
    return not is_tag_count_positive("begin mooring <ACTOR SHIP>", state)

def if_dropping_anchor(state):
    return is_tag_count_positive("dropping anchor <ACTOR SHIP>", state)
    
def not_dropping_anchor(state):
    return not if_dropping_anchor(state)
    
def if_dropping_anchor_middle(state):
    return is_tag_count_greater_than("dropping anchor <ACTOR SHIP>", 2, state)

def if_dropping_anchor_end(state):
    if is_tag_count_positive("dropping anchor <ACTOR SHIP>", state):
        return is_tag_count_less_than("dropping anchor <ACTOR SHIP>", 3, state)
    
def not_enough_anchors(state):
    return not if_enough_anchors(state)
    
def if_can_drop_anchor(state):
    if is_tag_count_positive("anchor close <ACTOR SHIP>", state):
        return False
    return True # TODO: get harbor conditions

def not_can_drop_anchor(state):
    return not if_can_drop_anchor(state)
    
def efx_begin_mooring(state):
    effects = state["tags"]
    effects[expandTagFromAction("begin mooring <ACTOR SHIP>", state)] = 1
    effects[expandTagFromAction("mooring anchors needed <ACTOR SHIP>", state)] = 2 # TODO: set in conflict above, based on conditions...
    effects[expandTagFromAction("anchors moored <ACTOR SHIP>", state)] = 0
    effects[expandTagFromAction("dropping anchor <ACTOR SHIP>", state)] = 0
    return effects
    
def efx_end_mooring(state):
    effects = state["tags"]
    effects[expandTagFromAction("begin mooring <ACTOR SHIP>", state)] = 0
    effects[expandTagFromAction("mooring anchors needed <ACTOR SHIP>", state)] = 0
    effects[expandTagFromAction("dropping anchor <ACTOR SHIP>", state)] = 0
    return effects


#def efx_begin_dropping_anchor(state):
#    effects = state["tags"]
#    effects[expandTagFromAction("dropping anchor <ACTOR SHIP>", state)] = 3
#    return effects
    
def efx_dropping_anchor(state):
    effects = state["tags"]
    anchor_drop_state = effects.get(expandTagFromAction("dropping anchor <ACTOR SHIP>", state))
    #print("")
    #traceback.print_stack(file=sys.stdout)
    #print(state)
    #print("anchor_drop_state: {0}".format(anchor_drop_state))
    if None == anchor_drop_state or anchor_drop_state <= 0:
        effects[expandTagFromAction("dropping anchor <ACTOR SHIP>", state)] = 3 # Can be increased for more description of readying the anchor...
        return effects
    else:
        effects.subtract([expandTagFromAction("dropping anchor <ACTOR SHIP>", state)])
    anchor_drop_state = effects.get(expandTagFromAction("dropping anchor <ACTOR SHIP>", state))
    if anchor_drop_state == 1:
        effects.update([expandTagFromAction("anchors moored <ACTOR SHIP>", state)])
        effects[expandTagFromAction("anchor aweigh <ACTOR SHIP>", state)] = 0
        effects[expandTagFromAction("anchor close <ACTOR SHIP>", state)] = 3
        effects[expandTagFromAction("dropping anchor <ACTOR SHIP>", state)] = 0
    return effects
    
def efx_drift_ship(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("anchor close <ACTOR SHIP>", state)])
    # TODO: perform ship drifting...probably as its own action catalog
    return effects
    
def efx_pull_ship(state):
    effects = state["tags"]
    # TODO: use the capstan to move the ship
    return effects

def efx_test_mooring(state):
    effects = state["tags"]
    effects[expandTagFromAction("anchor aweigh <ACTOR SHIP>", state)] = 1
    effects[expandTagFromAction("mooring ship <ACTOR SHIP>", state)] = 1
    return effects
    
def cmd_efx_end_mooring_ship(actproc):
    charone = actproc().parent().char_one
    chartwo = actproc().parent().char_two
    transcript = actproc().emitTranscript()
    tag_change = collections.Counter()
    tag_change[expandTag("anchor aweigh <ACTOR SHIP>", charone, chartwo)] = -1
    anchor_count = actproc().currentState().get(expandTag("anchors moored <ACTOR SHIP>", charone, chartwo))
    #print(anchor_count)
    tag_change[expandTag("anchors moored <ACTOR SHIP>", charone, chartwo)] = anchor_count
    act = {Cmd.effects: [lambda state: state["tags"] + tag_change],
           Cmd.action: transcript }
    actproc().sendToParentConflict(act)

def cmd_efx_start_drift(actproc):
    actor = actproc().parent().char_one
    target = actproc().parent().char_two
    subconflict = Conflict(actcat_ship_drift, actor, target, [expandTag("ship drifting <ACTOR SHIP>", actor, target)])
    actproc().parent().spawnSubconflict(subconflict)
    return # TODO    

#Conrad


     
actcat_ship_drop_anchor = [
#{Cmd.prereq: [is_ship, not_anchor_aweigh, not_begin_mooring], Cmd.effects: [efx_test_mooring], Cmd.action: "TEST"},                           
{Cmd.prereq: [is_ship, if_anchor_aweigh, if_mooring_ship, not_begin_mooring], Cmd.effects: [efx_begin_mooring], Cmd.action: ["<crewmember> was sent below to fetch the hawser.", "<crewmember> and <crewmember2> were sent below to fetch the hawser.","The #sailors# prepared to moor the #ship#.","The #ship# was made ready for the mooring.","<THE CAPTAIN> gave the order to moor the ship."]},
{Cmd.prereq: [is_ship, if_mooring_ship, if_begin_mooring, if_enough_anchors], Cmd.effects: [], Cmd.command: [cmd_efx_end_mooring_ship, cmd_efx_resolve_conflict], Cmd.action: "<PAR><MOORING SHIP: END>"},
{Cmd.prereq: [is_ship, if_mooring_ship, not_dropping_anchor, if_can_drop_anchor, if_begin_mooring, not_enough_anchors], Cmd.effects: [efx_dropping_anchor], Cmd.action: ["#hawsehole.capitalize#, #hawser_laid_out#.", "#hawser_laid_out.capitalize#, #hawsehole#.","#hawsehole.capitalize#, #hawser_laid_out#.", "#hawser_laid_out.capitalize#, #hawsehole#.","#hawsehole.capitalize#, #hawser_laid_out#.", "#hawser_laid_out.capitalize#, #hawsehole#.","<PAR>Before an anchor can ever be raised, it must be let go; and this perfectly obvious truism brings me at once to the subject of the degradation of the sea language in the daily press of this country.<PAR>Your journalist, whether he takes charge of a ship or a fleet, almost invariably \"casts\" his anchor.  Now, an anchor is never cast, and to take a liberty with technical language is a crime against the clearness, precision, and beauty of perfected speech.An anchor is a forged piece of iron, admirably adapted to its end, and technical language is an instrument wrought into perfection by ages of experience, a flawless thing for its purpose.  An anchor of yesterday (because nowadays there are contrivances like mushrooms and things like claws, of no particular expression or shape—just hooks)—an anchor of yesterday is in its way a most efficient instrument.  To its perfection its size bears witness, for there is no other appliance so small for the great work it has to do.  Look at the anchors hanging from the cat-heads of a big ship!  How tiny they are in proportion to the great size of the hull!  Were they made of gold they would look like trinkets, like ornamental toys, no bigger in proportion than a jewelled drop in a woman’s ear.  And yet upon them will depend, more than once, the very life of the ship.<PAR>An anchor is forged and fashioned for faithfulness; give it ground that it can bite, and it will hold till the cable parts, and then, whatever may afterwards befall its ship, that anchor is \"lost.\"  The honest, rough piece of iron, so simple in appearance, has more parts than the human body has limbs: the ring, the stock, the crown, the flukes, the palms, the shank.  All this, according to the journalist, is \"cast\" when a ship arriving at an anchorage is brought up.<PAR>This insistence in using the odious word arises from the fact that a particularly benighted landsman must imagine the act of anchoring as a process of throwing something overboard, whereas the anchor ready for its work is already overboard, and is not thrown over, but simply allowed to fall.  It hangs from the ship’s side at the end of a heavy, projecting timber called the cat-head, in the bight of a short, thick chain whose end link is suddenly released by a blow from a top-maul or the pull of a lever when the order is given.  And the order is not \"Heave over!\" as the paragraphist seems to imagine, but \"Let go!\"<PAR>"]},
{Cmd.prereq: [is_ship, if_mooring_ship, not_dropping_anchor, if_can_drop_anchor, if_begin_mooring, not_enough_anchors], Cmd.effects: [efx_dropping_anchor], Cmd.action: ["#hawsehole.capitalize#, #hawser_laid_out#.", "#hawser_laid_out.capitalize#, #hawsehole#."]},
{Cmd.prereq: [is_ship, if_mooring_ship, not_dropping_anchor, if_can_drop_anchor, if_begin_mooring, not_enough_anchors], Cmd.effects: [efx_dropping_anchor], Cmd.action: ["#hawsehole.capitalize#, #hawser_laid_out#.", "#hawser_laid_out.capitalize#, #hawsehole#."]},
{Cmd.prereq: [is_ship, if_mooring_ship, if_dropping_anchor_middle, if_begin_mooring, not_enough_anchors], Cmd.effects: [efx_dropping_anchor], Cmd.action: ["<crewmember> attached the anchor bouy.","The #sailors# took care to stand free of the cable.",""]},
{Cmd.prereq: [is_ship, if_mooring_ship, if_dropping_anchor_end, if_begin_mooring, not_enough_anchors], Cmd.effects: [efx_dropping_anchor], Cmd.action: ["Then they let fall the anchor, and it entered the water with a spash.", "The anchor was dropped with a splash.","The anchor was dropped, the cable playing out behind it.","\"Let go!\" and down it went.", "Down went the anchor, up spashed the spray.", "The stopper rope released, the anchor dropped."]},
{Cmd.prereq: [is_ship, if_mooring_ship, not_dropping_anchor, not_can_drop_anchor, if_begin_mooring, not_enough_anchors, not_rushed_for_time], Cmd.effects: [], Cmd.command: [cmd_efx_start_drift], Cmd.action: ["<PAR>The first anchor secure, the crew made ready to release the second, once the winds and tides had done their work.","<PAR>With one anchor in place, <THE CAPTAIN> judged it sufficent to wait for the ship to drift into position."]},
{Cmd.prereq: [is_ship, if_mooring_ship, not_dropping_anchor, not_can_drop_anchor, if_begin_mooring, not_enough_anchors, if_rushed_for_time, not_crew_busy], Cmd.effects: [efx_pull_ship], Cmd.action: "<NEED TO MOVE SHIP TO BE ABLE TO DROP THE NEXT ANCHOR: USE THE CAPSTAN>"},
{Cmd.prereq: [is_ship, if_mooring_ship, not_dropping_anchor, not_can_drop_anchor, if_begin_mooring, not_enough_anchors, if_rushed_for_time, not_crew_busy], Cmd.effects: [efx_pull_ship], Cmd.action: "<NEED TO MOVE SHIP TO BE ABLE TO DROP THE NEXT ANCHOR: USE THE CAPSTAN>"}, 
]


def cmd_efx_end_drift(actproc):
    charone = actproc().parent().char_one
    chartwo = actproc().parent().char_two
    transcript = actproc().emitTranscript()
    tag_change = collections.Counter()
    tag_change[expandTag("anchor close <ACTOR SHIP>", charone, chartwo)] = -9
    act = {Cmd.effects: [lambda state: state["tags"] + tag_change],
           Cmd.action: transcript }
    actproc().sendToParentConflict(act)

def if_drifting(state):
    return is_tag_count_positive("ship drifting <ACTOR SHIP>", state)    
    
def if_reef_danger(state):
    return False # TODO: check for danger of running aground

actcat_ship_drift = [
{Cmd.prereq: [is_ship, if_drifting], Cmd.effects: [], Cmd.command: [cmd_efx_end_drift, cmd_efx_resolve_conflict], Cmd.action: "The ship drifted with the tide.<PAR>"},
#{Cmd.prereq: [], Cmd.effects: [], Cmd.command: [], Cmd.action: ""},
#{Cmd.prereq: [], Cmd.effects: [], Cmd.command: [], Cmd.action: ""},
#{Cmd.prereq: [], Cmd.effects: [], Cmd.command: [], Cmd.action: ""},                     
]












actcat_ship_grounded = [
#{Cmd.prereq: [respond_start_pull_off], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "<PAR>With the anchor secured, the messenger was run out and the capstan manned."},                 
]
#The men strained at the bars until it seemed as though they would burst their very sinews; another reluctant click or two of the pawl showed that something was at length yielding; and then, first with a slow jerky motion which quickened rapidly, and ended in a mighty surge as the men drove the capstan irresistibly round, the bows of the schooner swerved to seaward, the vessel herself righted, hung for a moment, and then glided off the tail of the bank, finally swinging to her anchor, afloat once more.


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
    
