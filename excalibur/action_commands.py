# -*- coding: utf-8 -*-

import collections
import functools
from enum import Enum
import numpy.random
import sys
from character import Character
from character import generatePirate
import tracery

class Cmd(Enum):
    current_actor = 1 # character currently acting, set dynamically
    current_target = 2 # object of the character's action, set dynamically
    action = 3
    prereq = 4
    effects = 5
    last_time = 999
    
def translateActionDescription(action):
    actor = action[Cmd.current_actor]
    target = action[Cmd.current_target] 
    # TODO: translate the variables into their description forms
    action_string = action[Cmd.action]
    action_string = action_string.replace("{ACTOR}", actor.name)
    action_string = action_string.replace("{ANTAGONIST}", target.name)
    action_string = action_string.replace("{ACTOR_WEAPON}", actor.weapon_name)
    action_string = action_string.replace("{ANTAGONIST_WEAPON}", target.weapon_name)
    action_string = action_string.replace("{TARGET_WEAPON}", target.weapon_name)
    action_string = action_string.replace("{ANTAGONIST'S}", target.possessive)
    action_string = action_string.replace("{TARGET}", target.name)
    action_string = action_string.replace("{TARGET'S}", target.possessive)
    action_string = action_string.replace("{ACTOR'S}", actor.possessive)
    action_string = action_string.replace("{TARGET_HIM}", target.him)
    action_string = action_string.replace("{ACTOR_HIM}", actor.him)
    action_string = action_string.replace("{ANTAGONIST_HER}", target.him)
    action_string = action_string.replace("{ANTAGONIST_HIM}", target.him)
    action_string = action_string.replace("{TARGET_HER}", target.him)
    action_string = action_string.replace("{ACTOR_HER}", actor.him)
    action_string = action_string.replace("{ANTAGONIST_SELF}", target.herself)
    action_string = action_string.replace("{TARGET_SELF}", target.herself)
    action_string = action_string.replace("{ACTOR_SELF}", actor.herself)
    # TODO: replace the following with actual lookups
    action_string = action_string.replace("{ACTOR_ATTRIBUTE}", "skill")
    action_string = action_string.replace("{ANTAGONIST_ATTRIBUTE}", "strength")
    action_string = action_string.replace("{ACTOR_WEAPON_SOUND}", "clank")
    action_string = action_string.replace("{ANTAGONIST_ARMOR}", "leather cap")
    # TODO: add lookups for ships and crew
    return action_string

class ActionProcessor:
    def __init__(self):
        self.queue = collections.deque()
        
    def addAction(self, act):
        self.queue.append(act)
            
    def currentState(self):
        """
        Runs the effects in the queue, returning the current collection of tags
        """
        effect_bag = collections.Counter()
        for act in self.queue:
            if not act is None:
                if Cmd.effects in act:
                    for efx in act[Cmd.effects]:
                        effect_bag = efx({"action": act, "tags": effect_bag})
                effect_bag = +effect_bag # remove zero and negative counts
                for efx in list(effect_bag): # some signals decay over time...
                    if "decay" in efx:
                        effect_bag.subtract([efx])
                effect_bag = +effect_bag # remove zero and negative counts
        return effect_bag
    
    def currentTranscript(self):
        transcript = []
        for act in self.queue:
            if not act is None:
                transcript.append(translateActionDescription(act))
        return transcript
                

def expandTag(tag, actor, target):
    tag = tag.replace("{ACTOR}", actor.id)
    tag = tag.replace("{TARGET}", target.id)
    return tag
    
def expandTagFromState(tag, state):
    return expandTag(tag, state["actor"], state["target"])

def expandTagFromAction(tag, state):
    return expandTag(tag, state["action"][Cmd.current_actor], state["action"][Cmd.current_target])    
               
class Conflict:
    def __init__(self, action_catalog, protagonist, antagonist):
        self.char_one = protagonist#Character("Robin Hood")
        self.char_two = antagonist#Character("Sir Galahad")
        self.action_processor = ActionProcessor()
        self.deck_of_actions = action_catalog
        #self.current_state = []
        self.actions_last_time = []
        for act in self.deck_of_actions:
            act.update({Cmd.last_time: 0.0})
        
        
    def performAction(self, actor, target, action):
        action.update({Cmd.current_actor: actor, Cmd.current_target: target})
        print(action)
        self.action_processor.addAction(action)
        
    def currentState(self):
        #self.current_state = 
        return self.action_processor.currentState()
    
    def currentTranscript(self):
        return self.action_processor.currentTranscript()
        
    def prereqCheck(self, action, actor, target):
        if Cmd.prereq in action:
            for pre in action[Cmd.prereq]:
                if not pre({"conflict":self, "actor": actor, "target": target}):
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
            act[Cmd.last_time] = act[Cmd.last_time] * 0.99
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

def WeighAnchor(conflict):
    conflict.performNextAction(0)
    print(conflict.currentState())
    print("===")
    
        
def in_combat(state):
    cur_tags = state["conflict"].currentState()
    if ("end combat" in cur_tags):
        return False
    if ("begin combat" in cur_tags):
        return False
    return ("in combat" in cur_tags)
    
def not_in_combat(state):
    cur_tags = state["conflict"].currentState()
    return not ("in combat" in cur_tags)
    
def not_end_combat(state):
    cur_tags = state["conflict"].currentState()
    return not ("end combat" in cur_tags)

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
    if not is_tag_count_positive("has weapon {ACTOR}", state):
        return False
    return can_proact(state)

def incoming_attack(state): # AKA "should parry", a necessary but not complete componet of "can parry"
    cur_tags = state["conflict"].currentState()
    if not in_combat(state):
        return False
    return (expandTagFromState("attacking {ACTOR}", state) in cur_tags)
    
def can_parry(state):
    if not incoming_attack(state):
        return False
    if is_offbalance_actor(state):
        return False
    return True
    
def is_tag_count_positive(tag, state):
    cur_tags = state["conflict"].currentState()
    if (expandTagFromState(tag, state) in cur_tags):
        return cur_tags[expandTagFromState(tag, state)] > 0

def is_staggered_actor(state):
    return is_tag_count_positive("staggered {ACTOR}", state)
    
def is_staggered_target(state):
    return is_tag_count_positive("staggered {TARGET}", state)

def is_wounded_actor(state):
    return is_tag_count_positive("wounded {ACTOR}", state)
    
def is_wounded_target(state):
    return is_tag_count_positive("wounded {TARGET}", state)

def not_is_wounded_actor(state):
    return not is_tag_count_positive("wounded {ACTOR}", state)
    
def not_is_wounded_target(state):
    return not is_tag_count_positive("wounded {TARGET}", state)
        
def is_fallen_actor(state):
    return is_tag_count_positive("fallen {ACTOR}", state)
    
def is_fallen_target(state):
    return is_tag_count_positive("fallen {TARGET}", state)

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
    cur_tags = state["conflict"].currentState()
    return (expandTagFromState("broken weapon {TARGET}", state) in cur_tags)
    return False

def actor_broken_weapon(state):
    cur_tags = state["conflict"].currentState()
    return (expandTagFromState("broken weapon {ACTOR}", state) in cur_tags)
    return False
    
def respond_actor_broken_weapon(state):
    """
    Respond actions happen as immidiate priority responses...
    """
    cur_tags = state["conflict"].currentState()
    for tag in cur_tags:
        if ("signal broken weapon" in tag):
            return actor_broken_weapon(state)
    return False
    
def respond_start_combat(state):
    """
    Respond actions happen as immidiate priority responses...
    """
    cur_tags = state["conflict"].currentState()
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
    effects.update(["in combat"])
    effects.update([expandTagFromAction("has weapon {ACTOR}", state)])
    effects.update([expandTagFromAction("has weapon {TARGET}", state)])
    return effects
    
def efx_attack_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("attacking {TARGET}", state)])
    return effects

def efx_knockdown_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("fallen {TARGET}", state)])
    return effects
    
def efx_knockdown_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("fallen {ACTOR}", state)])
    return effects
    
def efx_wound_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("wounded {TARGET}", state)])
    return effects
    
def efx_wound_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("wounded {ACTOR}", state)])
    return effects
    
def efx_stagger_target(state):
    effects = state["tags"]
    effects[expandTagFromAction("staggered {TARGET}", state)] = 0
    return effects
    
def efx_stagger_actor(state):
    effects = state["tags"]
    effects[expandTagFromAction("staggered {ACTOR}", state)] = 0
    return effects

def efx_break_weapon_target(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("broken weapon {TARGET}", state)])
    effects.update(["signal broken weapon"])
    effects.subtract([expandTagFromAction("has weapon {TARGET}", state)])
    effects = efx_signal_broken_weapon(state)
    return effects
    
def efx_drop_weapon_target(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("has weapon {TARGET}", state)])
    effects = efx_signal_dropped_weapon(state)
    return effects
    
def efx_break_weapon_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("broken weapon {ACTOR}", state)])
    effects.update(["signal broken weapon"])
    effects.subtract([expandTagFromAction("has weapon {ACTOR}", state)])
    effects = efx_signal_broken_weapon(state)
    return effects
    
def efx_recover_balance_actor(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("staggered {ACTOR}", state)])
    return effects

def efx_end_attack(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("attacking {ACTOR}", state)])
    return effects

def efx_parry(state):
    effects = state["tags"]
    effects = efx_end_attack(state)
    return effects

def efx_end_combat(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("end combat", state)])
    del effects[expandTagFromAction("in combat", state)]
    return effects
    
def efx_emotion_anger_actor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("emotion {ACTOR}: anger", state)])
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
{Cmd.prereq: [not_in_combat, not_end_combat], Cmd.effects: [efx_signal_start_combat], Cmd.action: "BEGIN"},
#Begin
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "In a moment {ACTOR} stepped quickly {UPON THE PLACE} where {ANTAGONIST} stood."},
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "At last {ACTOR} struck like a flash, and--\"rap!\"--{ANTAGONIST} met the blow and turned it aside, and then smote back at {ACTOR}, who also turned the blow; and so this mighty battle began."},
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "Then {ACTOR} spat upon {ACTOR'S} hands and, grasping {ACTOR'S} {ACTOR_WEAPON}, came straight at the other."},
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "{ACTOR} gripped {ACTOR'S} {ACTOR_WEAPON} and threw {ACTOR_SELF} upon {ACTOR'S} guard."},
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "{ACTOR} said nothing at first but stood looking at {ANTAGONIST} with a grim face."},
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "Whatever {ACTOR} thought, {ACTOR} stood {ACTOR'S} ground, and now {ACTOR} and {ANTAGONIST} stood face to face."},
# Start Attack
{Cmd.prereq: [can_attack], Cmd.effects: [efx_attack_target], Cmd.action: "{PAR}{ACTOR} made a feint, and then delivered a blow at {ANTAGONIST} that, had it met its mark, would have tumbled {ANTAGONIST} speedily."},
{Cmd.prereq: [can_attack], Cmd.effects: [efx_attack_target], Cmd.action: "{PAR}At last {ACTOR} saw {ACTOR'S} chance, and, throwing all the strength {ACTOR} felt going from {ACTOR_HIM} into one blow that might have felled an ox, {ACTOR} struck at {ANTAGONIST} with might and main."},
# Response, leading to knockdown of original attacker
{Cmd.prereq: [incoming_attack, is_offbalance_actor], Cmd.effects: [efx_knockdown_target, efx_recover_balance_actor, efx_drop_weapon_target], Cmd.action: "But {ACTOR} regained {ACTOR_SELF} quickly and, at arm's length, struck back a blow at {ANTAGONIST}, and this time the stroke reached its mark, and down went {ANTAGONIST} at full length, {ANTAGONIST'S} {ANTAGONIST_WEAPON} flying from {ANTAGONIST'S} hand as {ANTAGONIST} fell."},
# Back-and-forth stalemate
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "{ACTOR} struck like a flash, and--\"rap!\"--{ANTAGONIST} met the blow and turned it aside, and then smote back at {ACTOR}, who also turned the blow."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "But {ACTOR} turned the blow right deftly and in return gave one as stout, which {ANTAGONIST} also turned as {ACTOR} had done."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "Thrice {ACTOR} struck {ANTAGONIST}; once upon the arm and twice upon the ribs, and yet {ACTOR} warded all the other's blows, only one of which, had it met its mark, would have laid {ACTOR} lower in the dust than {ACTOR} had ever gone before."},
#Response, counterattack wounds original attacker
{Cmd.prereq: [can_parry], Cmd.effects: [efx_wound_target, efx_end_attack], Cmd.action: "{ANTAGONIST} soon found that {ANTAGONIST} had met {ANTAGONIST'S} match, for {ACTOR} warded and parried all of the attacks, and, before {ANTAGONIST} thought, {ACTOR} gave {ANTAGONIST} a rap upon the ribs in return."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_wound_target, efx_end_attack], Cmd.action: "So shrewd was the stroke that {ACTOR} came within a hair's-breadth of falling, but {ACTOR} regained {ACTOR_SELF} right quickly and, by a dexterous blow, gave {ANTAGONIST} a crack on the crown that caused the blood to flow."},
#Response, counterattack knocks down original attacker
{Cmd.prereq: [can_parry, target_vulnerable], Cmd.effects: [efx_knockdown_target, efx_end_attack], Cmd.action: "But {ACTOR} warded the blow and thwacked {ANTAGONIST}, and this time so fairly that {ANTAGONIST} fell heels over head, as the queen pin falls in a game of bowls."},
{Cmd.prereq: [can_parry, target_vulnerable], Cmd.effects: [efx_knockdown_target, efx_end_attack], Cmd.action: "In response, {ACTOR} struck {ANTAGONIST'S} {ANTAGONIST_WEAPON} so fairly in the middle that {ANTAGONIST} could hardly hold {ANTAGONIST'S} {ANTAGONIST_WEAPON} in {ANTAGONIST'S} hand; again {ACTOR} struck, and {ANTAGONIST} bent beneath the blow; a third time {ACTOR} struck, and now not only fairly beat down {ANTAGONIST'S} guard, but gave {ANTAGONIST} such a rap, also, that down {ANTAGONIST} tumbled."},
# Response: failed, weapon breaks
{Cmd.prereq: [can_parry, target_vulnerable], Cmd.effects: [efx_break_weapon_target], Cmd.action: "{ANTAGONIST} warded two of the strokes, but at the third, {ANTAGONIST'S} {ANTAGONIST_WEAPON} broke beneath the mighty blows of {ACTOR}."},
#React to broken weapon
{Cmd.prereq: [respond_actor_broken_weapon], Cmd.effects: [efx_end_combat, efx_clear_signal_broken_weapon], Cmd.action: "\"Now, ill betide thee, traitor {ACTOR_WEAPON},\" cried {ACTOR}, as it fell from {ACTOR'S} hands; \"a foul {ACTOR_WEAPON} art thou to serve me thus in my hour of need.\""},
#Land a hit
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "At last {ACTOR} gave {ANTAGONIST} a blow upon the ribs that made {ANTAGONIST'S} jacket smoke like a damp straw thatch in the sun."},
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "And now did {ANTAGONIST'S} {ANTAGONIST_ARMOR} stand {ANTAGONIST} in good stead, and but for it {ANTAGONIST} might never have held {ANTAGONIST_WEAPON} in hand again."},
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "As it was, the blow {ANTAGONIST} caught beside the head was so shrewd that it sent {ANTAGONIST} staggering, so that, if {ACTOR} had had the strength to follow up {ACTOR'S} vantage, it would have been ill for {ANTAGONIST}."},
{Cmd.prereq: [can_attack, target_vulnerable], Cmd.effects: [efx_stagger_target], Cmd.action: "Then, raising {ACTOR'S} {ACTOR_WEAPON}, {ACTOR} dealt {ANTAGONIST} a blow upon the ribs."},
#Reaction: Emotion, leading to renewed attack
{Cmd.prereq: [react_with_anger_actor], Cmd.effects: [efx_emotion_anger_actor], Cmd.action: "Then {ACTOR} grew mad with anger and smote with all {ACTOR'S} might at the other."},
{Cmd.prereq: [react_with_anger_actor], Cmd.effects: [efx_emotion_anger_actor], Cmd.action: "At this {ANTAGONIST} laughed aloud, and {ACTOR} grew more angry than ever, and smote again with all {ACTOR'S} might and main."},
# General back and forth
{Cmd.prereq: [can_attack], Cmd.action: "Well did {ACTOR} hold {ACTOR'S} own that day."},
{Cmd.prereq: [can_attack], Cmd.action: "This way and that they fought, and back and forth, {ACTOR'S} {ACTOR_ATTRIBUTE} against the {ANTAGONIST'S} {ANTAGONIST_ATTRIBUTE}."},
{Cmd.prereq: [can_attack], Cmd.action: "Then up and down and back and forth they trod, the blows falling so thick and fast that, at a distance, one would have thought that half a score were fighting."},
{Cmd.prereq: [can_attack], Cmd.action: "Thus they fought for nigh a half an hour, until the ground was all plowed up with the digging of their heels, and their breathing grew labored like the ox in the furrow."},
{Cmd.prereq: [can_attack], Cmd.action: "The dust of the highway rose up around them like a cloud, so that at times the onlookers could see nothing, but only hear the {ACTOR_WEAPON_SOUND} of {ACTOR_WEAPON} against {ANTAGONIST_WEAPON}."},
{Cmd.prereq: [can_attack], Cmd.action: "So they stood, each in their place, neither moving a finger's-breadth back, for one good hour, and many blows were given and received by each in that time, till here and there were sore bones and bumps, yet neither thought of crying \"Enough,\" nor seemed likely to fall."},
{Cmd.prereq: [can_attack], Cmd.action: "Now and then they stopped to rest, and each thought that they never had seen in all their life before such a hand at {ACTOR_WEAPON} or {ANTAGONIST_WEAPON}."},
{Cmd.prereq: [is_fallen_actor, not_end_combat], Cmd.effects: [efx_end_combat], Cmd.action: "And so {ACTOR} was defeated by {ANTAGONIST'S} {ANTAGONIST_WEAPON}"},
# Friar Tuck
{Cmd.prereq: [respond_start_combat], Cmd.effects: [efx_begin_combat], Cmd.action: "So, without more ado, they came together, and thereupon began a fierce and mighty battle."},
{Cmd.prereq: [can_attack], Cmd.action: "Right and left, and up and down and back and forth they fought."},
{Cmd.prereq: [can_attack], Cmd.action: "The {ACTOR_WEAPON} {ACTOR_WEAPON_VERB} and then met with a {ACTOR_WEAPON_SOUND} that sounded far and near."},
{Cmd.prereq: [can_attack], Cmd.action: "This was no playful bout, but a grim and serious fight of real earnest."},
{Cmd.prereq: [can_attack], Cmd.action: "Thus they strove for an hour or more, pausing every now and then to rest, at which times each looked at the other with wonder, and thought that never had they seen so stout a foe; then once again they would go at it more fiercely than ever."},
{Cmd.prereq: [can_attack, not_is_wounded_actor, not_is_wounded_target], Cmd.action: "Yet in all this time neither had harmed the other nor caused his blood to flow."},
# Beggar Riccon
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action: "Then {ACTOR} swung his {WEAPON} also, and struck a mighty blow at {TARGET}, which {TARGET} turned."},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_parry], Cmd.action:  "Three blows {TARGET} struck, yet never one touched so much as a hair of {ACTOR'S} head. "},
{Cmd.prereq: [can_parry], Cmd.effects: [efx_knockdown_target, efx_drop_weapon_target], Cmd.action: "Then {ACTOR} saw {ACTOR'S} chance, and, ere you could count three, {TARGET'S} {TARGET_WEAPON} was flying away, and {TARGET} {TARGET_SELF} lay upon the {GROUND_DESCRIPTION} with no more motion than you could find in an empty pudding bag."}
]

def respond_start_weigh_anchor(state):
    cur_tags = state["conflict"].currentState()
    search_tag = expandTagFromState("signal start weigh anchor {ACTOR SHIP}", state)
    for tag in cur_tags:
        if search_tag in tag:
            return True
    return False

def respond_prepare_capstan(state):
    cur_tags = state["conflict"].currentState()
    search_tag = expandTagFromState("signal prepare capstan {ACTOR SHIP}", state)
    for tag in cur_tags:
        if search_tag in tag:
            return True
    return False

def if_anchor_aweigh(state):
    return is_tag_count_positive("anchor aweigh {ACTOR SHIP}", state)
    
def not_anchor_aweigh(state):
    return not is_tag_count_positive("anchor aweigh {ACTOR SHIP}", state)
    
def if_turning_capstan(state):
    return is_tag_count_positive("turning capstan {ACTOR SHIP}", state)

def if_weighing_anchor(state):
    return is_tag_count_positive("weighing anchor {ACTOR SHIP}", state)

def if_weighing_anchor_end(state):
    return is_tag_count_positive("weighing anchor end{ACTOR SHIP}", state)

#def begin_weighing_anchor(state):
#    return is_tag_count_positive("begin weighing anchor {ACTOR SHIP}", state)

def if_anchor_struggle(state):
    return is_tag_count_positive("anchor struggle {ACTOR SHIP}", state)

def not_turning_capstan(state):
    return not is_tag_count_positive("turning capstan {ACTOR SHIP}", state)

def not_weighing_anchor(state):
    return not is_tag_count_positive("weighing anchor {ACTOR SHIP}", state)

def not_weighing_anchor_end(state):
    return not is_tag_count_positive("weighing anchor end {ACTOR SHIP}", state)
    
def not_anchor_struggle(state):
    return not is_tag_count_positive("anchor struggle {ACTOR SHIP}", state)
    
def is_tag_count_greater_than(tag, than, state):
    cur_tags = state["conflict"].currentState()
    if (expandTagFromState(tag, state) in cur_tags):
        return cur_tags[expandTagFromState(tag, state)] > than

def is_tag_count_less_than(tag, than, state):
    cur_tags = state["conflict"].currentState()
    if (expandTagFromState(tag, state) in cur_tags):
        return cur_tags[expandTagFromState(tag, state)] < than
                        
def if_anchor_at_long_stay(state):
    return is_tag_count_less_than("turning capstan {ACTOR SHIP}", 10, state)

def if_anchor_at_short_stay(state):
    return is_tag_count_less_than("turning capstan {ACTOR SHIP}", 7, state)

def if_anchor_at_up_and_down(state):
    return is_tag_count_less_than("turning capstan {ACTOR SHIP}", 4, state)

def if_anchor_at_anchor_aweigh(state):
    return is_tag_count_less_than("turning capstan {ACTOR SHIP}", 2, state)

def efx_signal_start_weigh_anchor(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("signal start weigh anchor {ACTOR SHIP}", state)])
    effects.update([expandTagFromAction("weighing anchor {ACTOR SHIP}", state)])
    #effects = efx_clear_signal(state, expandTagFromAction("begin weighing anchor {ACTOR SHIP}", state))
    return effects
    
def efx_signal_prepare_capstan(state):
    effects = state["tags"]
    effects.update([expandTagFromAction("signal prepare capstan {ACTOR SHIP}", state)])
    effects = efx_clear_signal(state, expandTagFromAction("signal start weigh anchor {ACTOR SHIP}", state))
    #effects = efx_clear_signal(state, expandTagFromAction("begin weighing anchor {ACTOR SHIP}", state))
    return effects
    
def efx_begin_turning_capstan(state):
    effects = state["tags"]
    effects[expandTagFromAction("turning capstan {ACTOR SHIP}", state)] = 12
    effects = efx_clear_signal(state, expandTagFromAction("signal prepare capstan {ACTOR SHIP}", state))
    return effects
    
def efx_turn_capstan(state):
    effects = state["tags"]
    effects.subtract([expandTagFromAction("turning capstan {ACTOR SHIP}", state)])
    return effects
    
def efx_finish_turn_capstan(state):
    effects = state["tags"]
    effects[expandTagFromAction("turning capstan {ACTOR SHIP}", state)] = 0
    return effects
    
def efx_end_weigh_anchor(state):
    effects = state["tags"]
    effects[expandTagFromAction("turning capstan {ACTOR SHIP}", state)] = 0
    effects[expandTagFromAction("weighing anchor {ACTOR SHIP}", state)] = 0
    effects[expandTagFromAction("anchor aweigh {ACTOR SHIP}", state)] = 1
    effects[expandTagFromAction("end weigh anchor {ACTOR SHIP}", state)] = 1
    effects = efx_clear_signal(state, expandTagFromAction("weighing anchor {ACTOR SHIP}", state))
    return effects
    
# Crew vs Anchor
weigh_anchor_actcat = [
#Temp: an order to jumpstart the conflict
{Cmd.prereq: [not_weighing_anchor, not_weighing_anchor_end, not_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_signal_start_weigh_anchor], Cmd.action: "{BEGIN: WEIGH ANCHOR}"},
{Cmd.prereq: [not_weighing_anchor, not_weighing_anchor_end, if_weighing_anchor, not_anchor_aweigh], Cmd.effects: [efx_signal_start_weigh_anchor], Cmd.action: "{BEGIN: WEIGH ANCHOR}"},
# clear the deck, make ready
{Cmd.prereq: [respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "The crew #adjectively# cleared the capstan and made ready to weigh anchor."},
{Cmd.prereq: [respond_start_weigh_anchor], Cmd.effects: [efx_signal_prepare_capstan], Cmd.action: "The order was given, and soon the messenger was run out and the capstan manned."},
# capstan bars fitted to capstan
{Cmd.prereq: [respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "{crewmember} fitted the bars, and the #sailors# took their positions around the capstan."},
{Cmd.prereq: [respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "{crewmember} took the bars from where they were stowed, and the #sailors# fitted them to the capstan."},
{Cmd.prereq: [respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "\"Take your positions, you #sailors#,\" said {THE BOATSWAIN}."},
{Cmd.prereq: [respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "There came soon the familiar racket of making sail and trimming yards and the clank of the capstan pawls. "},
{Cmd.prereq: [respond_prepare_capstan], Cmd.effects: [efx_begin_turning_capstan], Cmd.action: "The capstan bars were now fully manned."},
#pulling at the capstan
{Cmd.prereq: [if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The #sailors# pressed their broad chests against the powerful levers, planted their feet firmly upon the deck, straightened out their backs, and slowly pawl after pawl was gained."},
{Cmd.prereq: [if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "\"That's your sort, my hearties,\" exclaimed {THE BOATSWAIN} encouragingly, as {THE BOATSWAIN} applied {THE BOATSWAIN'S} tremendous strength to the outer extremity of one of the bars, \"heave with a will! heave, and she _must_ come! _heave_, all of us!! now--one--_two_--three!!!"},
{Cmd.prereq: [if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The #sailors# strained at the bars, the pawl clicking as they drove the capstan round."},
{Cmd.prereq: [if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: "The chorus of the shanty kept time with the clicks of the pawl."},
#sing a shanty
{Cmd.prereq: [if_turning_capstan], Cmd.effects: [efx_turn_capstan], Cmd.action: ["As the #sailors# turned the capstan, {THE BOATSWAIN} took up the verse and the crew repeated the chorus: {SHANTY}", "The crew sang in time with their work: {SHANTY}", "As was their practice, they sang to maintain the rhythm. {SHANTY}"]},
# straining, it goes slowly...
{Cmd.prereq: [if_turning_capstan, if_anchor_struggle], Cmd.effects: [], Cmd.action: ["The anchor held fast, drawing line tighter and pulling the ship closer.", "The #sailors# strained against the wheel of the capstan, each rachet of the pawl a hard won fight."]},
# call out: at long stay / at short stay, up and down, anchors aweigh
{Cmd.prereq: [if_turning_capstan, if_weighing_anchor, if_anchor_at_long_stay], Cmd.effects: [efx_turn_capstan], Cmd.action: "#weigh_anchor_long_stay#"},
{Cmd.prereq: [if_turning_capstan, if_weighing_anchor, if_anchor_at_short_stay], Cmd.effects: [efx_turn_capstan], Cmd.action: "#weigh_anchor_short_stay#"},
{Cmd.prereq: [if_turning_capstan, if_weighing_anchor, if_anchor_at_up_and_down], Cmd.effects: [efx_turn_capstan], Cmd.action: "#weigh_anchor_up_and_down#"},
{Cmd.prereq: [if_turning_capstan, if_weighing_anchor, if_anchor_at_anchor_aweigh], Cmd.effects: [efx_finish_turn_capstan], Cmd.action: "#weigh_anchor_aweigh#"},
# catting the anchor
{Cmd.prereq: [if_weighing_anchor, if_anchor_at_anchor_aweigh], Cmd.effects: [efx_end_weigh_anchor], Cmd.action: "{PAR}#catting_1# #catting_2# #catting_3# #catting_4#"}
]

postprocessing_table = {
"the_call_went_out": ["the call went out", "sang out {THE BOATSWAIN}", "cried {THE BOATSWAIN}", "was the call", "came the cry", "said {THE BOATSWAIN}, though it hardly took a keen eye to see it: the #sailors# could feel the strain"],
"the_crew_pushed": ["and the crew pushed around with a will", "accompanied by the clank of the pawl", "the great cable hauled by the messenger as it was driven by the capstan", "by the sweat and strain of the crew as they pushed","and the crew heaved again","with another heave on the capstan", "followed by the crew grunting as they gave the capstan another mighty shove"],
"sailors":["sailors","tars"],
"catting_1":["It took only a little more effort to bring the anchor up from the water, and the #sailors# completed the job with gusto.","Then the anchor flukes scraped and banged against the bow timbers.","With one last strain on the capstan, the anchor was brought to the cathead.", ""],
"catting_2":["#sailors.capitalize# rushed to cat the anchor.","The anchor was soon secured to the cathead.","Once the anchor was catted, the #sailors# stowed the capstan bars again.",""],
"catting_3":["The #ship_type# was alive and in motion.","The voyage was now properly begun.","The ship felt freer and lighter, as if it was glad to get underway.","","",""],
"catting_4":["The vessel heeled a little and the lapping water changed its tune to a swash-swash as the hull pushed it aside.","",""],
"weigh_anchor_long_stay":["\"At long stay,\" #the_call_went_out#, #the_crew_pushed#.", "#the_call_went_out.capitalize#: \"At long stay,\" #the_crew_pushed#", "As the capstan turned, the cable could be seen cutting through the surf.", "\"At long stay!\" #the_crew_pushed.capitalize#.", "\"At long stay!\""],
"weigh_anchor_short_stay": ["#the_crew_pushed.capitalize#, the anchor cable drawing taut.","\"At short stay,\" #the_call_went_out#, #the_crew_pushed#.", "The anchor cable was hauled aboard, #the_crew_pushed#.", "The cable drew taut, prompting the call: \"At short stay.\"","With each heave on the capstan, the ship was pulled closer to the anchor."],
"weigh_anchor_up_and_down": ["Below the waves, the anchor began to shift, the top lifting off the seafloor, #the_crew_pushed#.","\"Up and down,\" #the_call_went_out#, as the anchor pulled vertical, still in contact with the seafloor.","The anchor's tilt prompted {THE BOATSWAIN} to sing out, \"Up and down!\"","\"Up and down,\" #the_call_went_out, and the crew knew the end of their task was near."],
"weigh_anchor_anchors_aweigh": ["And at last {THE BOATSWAIN} called: \"Anchor aweigh!\"", "\"Anchor aweigh,\" #the_call_went_out#.", "The ship gave a lurch as the anchor came free of the bottom, #the_crew_pushed#.","With another shove, the anchor was free."],
}


test_char_one = Character("Robin Hood")
test_char_two = Character("Little John")

def parseActionForResearch(action):
    action.update({Cmd.current_actor: test_char_one, Cmd.current_target: test_char_two})
    desc = translateActionDescription(action)
    desc.replace("{PAR}", "")
    desc.replace("{DIALOG}", "")
    return desc

def parseActionCatalog(action_catalog):
    return [parseActionForResearch(act) for act in action_catalog]
    
