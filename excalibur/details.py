# -*- coding: utf-8 -*-

import tracery
from tracery.modifiers import base_english
import random
import numpy.random

shanties = [{"chorus":"""  
   #verse#  
   #verse#  
   #verse#  
   Early in the morning?  
   Hooray and up she rises,  
   Hooray and up she rises,  
   Hooray and up she rises  
   Early in the morning.  
   """,
"verse": [
"What shall we do with the drunken sailor,",
"Put him in the long-boat until he's sober.",
"Pull out the plug and wet him all over.",
"Put him in the scuppers with a hose-pipe on him.",
"Heave him by the leg in a running bowlin'.",
"Tie him to the taffrail when she's yard-arm under."
]},{"chorus":"""  
   #verse#  
   Storm along boys,  
   Storm along.  
   #verse#  
   Ah-ha, come along, get along,  
   Stormy along John.  
   """,
"verse":[
"Oh poor old Stormy's dead and gone.",
"I dug his grave with a silver spade.",
"I lower'd him down with a golden chain.",
"I carried him away to Mobile Bay.",
"Oh poor old Stormy's dead and gone."]
},{"chorus":"""  
   #verse#  
   Oh Rio.  
   #verse_2#  
   And we're bound for the Rio Grande.  
   Then away love, away,  
   'Way down Rio,  
   Sing fare you well my pretty young gal.  
   For we're bound for the Rio Grande.  
   """,
"verse":[
"Oh Cap-tain, oh Cap-tain, heave yer ship to,",
"I'll sing you a song of the fish of the sea.",
"Sing good-bye to Sally, and good-bye to Sue,",
"Our ship went sailing out over the Bar",
"Farewell and adieu to you ladies of Spain",
"I said farewell to Kitty my dear,",
"The oak, and the ash, and the bonny birk tree"],
"verse_2":[
"For I have got letters to send home by you",
"I'll sing you a song of the fish of the sea.",
"Sing good-bye to Sally, and good-bye to Sue,",
"And we pointed her nose for the South-er-en Star.",
"And we're all of us coming to see you again.",
"And she waved her white hand as we passed the South Pier.",
"They're all growing green in the North Countrie."]
},{"verse":[
"I thought I heard the old man say",
"We're homeward bound, I hear the sound.",
"We sailed away to Mobile Bay.",
"But now we're bound for Portsmouth Town.",
"And soon we'll be ashore again.",
"I kissed my Kitty upon the pier",
"We're homeward bound, and I hear the sound."],
"verse_2":[
"I thought I heard the old man say",
"We're homeward bound, I hear the sound.",
"We sailed away to Mobile Bay.",
"But now we're bound for Portsmouth Town.",
"And soon we'll be ashore again.",
"And it's oh to see you again my dear.",
"We're homeward bound, and I hear the sound."],
"chorus":"""  
   #verse#  
   Good-bye, fare ye well,  
   Good-bye, fare ye well.  
   #verse_2#  
   Hooray my boys we're homeward bound.  
   
   """}]

def prepShanty(shanty):
    if not ("verse_2" in shanty):
        shanty.update({"verse_2":shanty["verse"]})
    return shanty
   
def singShantyVerse(shanty, verseno):
    pshanty = prepShanty(shanty)
    verse_shanty = {"chorus":pshanty["chorus"],
                    "verse":pshanty["verse"][verseno],
                    "verse_2":pshanty["verse_2"][verseno]
                    }
    grammar = tracery.Grammar(verse_shanty)
    return grammar.flatten("#chorus#")

def singCompleteShanty(shanty):
    shanty_len = len(shanty["verse"])
    output = ""
    for i in range(shanty_len):
        output += singShantyVerse(shanty, i)
    return output

def singRandomShantyVerse(shanty):
    shanty_len = len(shanty["verse"])
    i = random.randrange(0,shanty_len - 1)
    return singShantyVerse(shanty, i)

def singShantyVerseCallAndResponse(shanty, verseno):
    pshanty = prepShanty(shanty)
    verse_shanty = {"chorus":pshanty["chorus"],
                    "verse":pshanty["verse"][verseno],
                    "verse_2":pshanty["verse_2"][verseno]
                    }
    grammar = tracery.Grammar(verse_shanty)
    split_shanty_chorus = pshanty["chorus"].splitlines()
    idx = 0
    line_one = ""
    line_two = ""
    output = []
    while idx < len(split_shanty_chorus):
        if "#verse#" in split_shanty_chorus[idx]:
            if not (line_one is ""):
                output.append("The coxswain sang out \"{0}\" and the crew joined in. ".format(line_one.strip(" ")))
            line_one = grammar.flatten(split_shanty_chorus[idx])
        else:
            line_two = split_shanty_chorus[idx]
        if line_one is "":
            if not (line_two is ""):
                output.append("Then the crew sang, \"{0}\" ".format(line_two.strip(" ")))
                line_one = ""
                line_two = ""
        else:
            if not (line_two is ""):
                output.append("The coxswain sang out \"{0}\" and the crew answered: \"{1}\" ".format(line_one.strip(" "), line_two.strip(" ")))
                line_one = ""
                line_two = ""
            #else:
            #    output.append("The coxswain sang out \"{0}\" and the crew joined in. ".format(line_one))
            #    line_one = ""
            #    line_two = ""
        idx += 1
    return output # TODO

def singShantySubset(shanty):
    verses = len(shanty["verse"])
    singing_verses = numpy.random.choice(range(verses), size=numpy.random.randint(0, verses),replace=False)
    output = "\n"
    output += singShantyVerse(shanty, 0)
    for v in singing_verses:
        output += singShantyVerse(shanty, v)
    return output
    
def singShanty(char, actor, target):
    return singShantySubset(random.choice(shanties))
    
    
print(singShantyVerse(shanties[0], 0))
print(singCompleteShanty(shanties[1]))
print(singRandomShantyVerse(shanties[2]))
    
   
