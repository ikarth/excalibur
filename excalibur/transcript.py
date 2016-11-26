# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 10:29:15 2016

@author: Isaac Karth

Takes transcripts generated elsewhere and turns them into readable output
"""

import tracery
from tracery.modifiers import base_english
import character
from action_commands import Cmd
import details


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

def interpertTranscript(script):
    text = script.get(Cmd.transcript)
    actor = script.get(Cmd.current_actor)
    target = script.get(Cmd.current_target)
    output = ""
    for line in text:
        output = output + interpertLine(line, actor, target)
    return output

def interpertLine(text, actor, target):
    if hasattr(text, "get"): # is a complete transcript
        return interpertTranscript(text)
    if isinstance(text, str):
        return interpertString(text, actor, target)
    if hasattr(text, "index"):
        output = ""
        for line in text:
            output += interpertLine(line, actor, target)
        return output
    return str("=> {0}\n".format(str(text)))
        
# There's probably a better way to implement this...
def indexCommands(text):
    command_nest = 0
    command_indexes = []
    command_start = [-1, -1, -1, -1]
    for idx, c in enumerate(text):
        if command_nest > 0:
            if "}" == c:
                command_nest -= 1
                command_indexes.append([command_nest, command_start[command_nest], idx])
        if "{" == c:
            command_start[command_nest] = idx
            command_nest += 1
    return command_indexes

command_table = {
"{PAR}": lambda c, a, t: "\n\n",
"{THE BOATSWAIN}": character.find_character_name,
"{CREWMEMBER}": character.find_character_name,
"{THE BOATSWAIN'S}": character.find_character_name_pos_adj,
"{SHANTY}": details.singShanty
}    

def interpertCommand(command, actor, target):
    result = command
    resultfn = command_table.get(command.upper())
    if None != resultfn:
        result = resultfn(command, actor, target)
    return result
    
def processCommand(cmd_idx, text, actor, target):
    command_text = text[cmd_idx[1]:cmd_idx[2]+1]
    # TODO: actually do something with the command
    command_text = interpertCommand(command_text.upper(), actor, target)
    command_text = command_text.replace("{","$")
    command_text = command_text.replace("}","$")
    text_start = text[:cmd_idx[1]]
    text_end = text[cmd_idx[2]+1:]
    newtext = text_start + command_text + text_end
    return newtext
    
def transcribeCommands(text, actor, target):
    indexes = indexCommands(text)
    newtext = text
    while len(indexes) > 0:
        #print(len(indexes))
        max_nest = max([i[0] for i in indexes])
        nidx = [i for i in indexes if (max_nest == i[0])]
        i = nidx[0]
        newtext = processCommand(i, newtext, actor, target)
        indexes = indexCommands(newtext)
    return newtext
            
def interpertString(text, actor, target):
    if not isinstance(text, str):
        return str(text)
    text = transcribeCommands(text, actor, target)
    grammar = tracery.Grammar(postprocessing_table)
    grammar.add_modifiers(base_english)
    output = grammar.flatten(str(text))
    output = transcribeCommands(output, actor, target)
    if output[-1] in "\".?!$\n": # End of a sentence
        output = output + " " # Add a space
    # TODO: combine quotes together and break on speaker change
    return output

def compileTranscript(story_transcript):
    return interpertLine(story_transcript, None, None)