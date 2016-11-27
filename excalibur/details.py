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
    return output + "\n"
    
def singShanty(char, actor, target):
    return singShantySubset(random.choice(shanties))
    
    
print(singShantyVerse(shanties[0], 0))
print(singCompleteShanty(shanties[1]))
print(singRandomShantyVerse(shanties[2]))


#"<ACTOR>, as <ACTOR> called out the order, ran forward through the smoke, snatching one of <ACTOR'S> pistols out of <ACTOR'S> pocket and the cutlass out of its sheath as <ACTOR> did so. "
#Behind him the men were coming, swarming up from below. 
#There was a sudden stunning report of a pistol, and then another and another, almost together. 
#There was a groan and the fall of a heavy body, and then a figure came jumping over the rail, with two or three more directly following. 
#The lieutenant was in the midst of the gun powder smoke, when suddenly Blackbeard was before him. 
#The pirate captain had stripped himself naked to the waist. 
#His shaggy black hair was falling over his eyes, and he looked like a demon fresh from the pit, with his frantic face. 
#Almost with the blindness of instinct the lieutenant thrust out his pistol, firing it as he did so. 
#The pirate staggered back: he was down—no; he was up again. 
#He had a pistol in each hand; but there was a stream of blood running down his naked ribs. 
#Suddenly, the mouth of a pistol was pointing straight at the lieutenant's head. 
#He ducked instinctively, striking upward with his cutlass as he did so. 
#There was a stunning, deafening report almost in his ear. 
#He struck again blindly with his cutlass. 
#He saw the flash of a sword and flung up his guard almost instinctively, meeting the crash of the descending blade. 
#Somebody shot from behind him, and at the same moment he saw some one else strike the pirate. 
#Blackbeard staggered again, and this time there was a great gash upon his neck. 
#Then one of Maynard's own men tumbled headlong upon him. 
#He fell with the man, but almost instantly he had scrambled to his feet again, and as he did so he saw that the pirate sloop had drifted a little away from them, and that their grappling irons had evidently parted. 
#His hand was smarting as though struck with the lash of a whip. 
#He looked around him; the pirate captain was nowhere to be seen—yes, there he was, lying by the rail. 
#He raised himself upon his elbow, and the lieutenant saw that he was trying to point a pistol at him, with an arm that wavered and swayed blindly, the pistol nearly falling from his fingers. 
#Suddenly his other elbow gave way and he fell down upon his face. 
#He tried to raise himself—he fell down again. 
#There was a report and a cloud of smoke, and when it cleared away Blackbeard had staggered up again.
#He was a terrible figure his head nodding down upon his breast.
#Somebody shot again, and then the swaying figure toppled and fell.
#It lay still for a moment—then rolled over—then lay still again.
    
   
describe_reef = [
["The reefs were not dry in any part, with the exception of some small black lumps, which at a distance resembled the round heads of penguins; the sea broke upon the edges, but inside the water was smooth, and of a light green colour.",
"The water was very clear round the edges of the reef, and there was presented to view a new creation: new to those land-dwellers who observed it, but imitative of the old. There were wheat sheaves, mushrooms, stags horns, cabbage leaves, and a variety of other forms, glowing under water with vivid tints of every shade betwixt green, purple, brown, and white; equalling in beauty and excelling in grandeur the most favourite parterre of the curious florist. ",
"These were different species of coral and fungus, growing, as it were, out of the solid rock, and each had its peculiar form and shade of colouring; but whilst contemplating the richness of the scene, one could not long forget with what destruction it was pregnant.",
"Different corals in a dead state, concreted into a solid mass of a dull-white colour, composed the stone of the reef.",
"The penguin heads were lumps which stood higher than the rest; and being generally dry, were blackened by the weather; but even in these, the forms of the different corals, and some shells were distinguishable."],
["The edges of the reef, but particularly on the outside where the sea broke, were the highest parts; within, there were pools and holes containing live corals, sponges, and sea eggs and cucumbers;^[* What we called sea cucumbers, from their shape, appears to have been the bêche de mer, or trepang; of which the Chinese make a soup, much esteemed in that country for its supposed invigorating qualities.] and many enormous cockles (chama gigas) were scattered upon different parts of the reef." ,
"At low water, this cockle seems most commonly to lie half open; but frequently closes with much noise; and the water within the shells then spouts up in a stream, three or four feet high: it was from this noise and the spouting of the water, that the #sailors# discovered them, for in other respects they were scarcely to be distinguished from the coral rock.",
"A number of these cockles were taken on board the ship, and stewed in the coppers; but they were too rank to be agreeable food, and were eaten by few.",
"One of them weighed 47½ lbs. as taken up, and contained 3lbs. 2 oz. of meat; but this size is much inferior to what was found by #famous_explorer#, upon the reefs of the coast further northward, or to several in the #British_Museum#; and I have since seen single shells more than four times the weight of the above shells and fish taken together.",
"There were various small channels amongst the reefs, some of which led to the outer breakers, and through these the tide was rushing in; but none appeared to be an opening sufficiently wide for the #ship#."]
]

describe_island = [
["This little island was of a triangular shape, and each side of it a mile long; it was surrounded by a coral reef which, as usual, presented a beautiful piece of marine scenery.",
"The stone which formed the basis of the island, and is scattered loosely over the surface, is a kind of porphyry; a small piece of it, applied to the theodolite, did not affect the needle, although, on moving the instrument a few yards southward, the east variation was increased 2° 23'.",
"Not much vegetable earth was contained amongst the stones on the surface, yet the island was thickly covered with trees and brush wood, whose foliage was not devoid of luxuriance.",
"Pines grow there, but they were more abundant, and seemingly larger, upon some other of the islands, particularly on the one to the westward.",
"There did not appear to be any fixed inhabitants; but proofs of the island having been visited some months before, were numerous; and upon the larger island there was a smoke."],
["Those who for the first time visit #ocean_sea_name.the#, generally are surprised at the appearance of the islands when beheld from the sea.",
"From the vague accounts we sometimes have of their beauty, many people are apt to picture to themselves enamelled and softly swelling plains, shaded over with delicious groves, and watered by purling brooks, and the entire country but little elevated above the surrounding ocean.",
"The reality is very different; bold rock-bound coasts, with the surf beating high against the lofty cliffs, and broken here and there into deep inlets, which open to the view thickly-wooded valleys, separated by the spurs of mountains clothed with tufted grass, and sweeping down towards the sea from an elevated and furrowed interior, form the principal features of these islands."]
]


cat_facts = ["<PAR>Cats have any amount of wiliness about them. A dog would scarcely think of hiding below a bush until its prey came within reach; but cats are adepts at an ambuscade. A cat knows by experience that a bird--say a sparrow--looks almost in every direction, saving directly beneath it, and so pussy always steals a march on it, from below. If a bird is foolish enough to alight on the top of a clothes-pole, pussy has a very easy victory. It is that same habit of never looking downwards, which causes those large birds, which alight on a ship's yards at sea, to be so easily captured by the sailors.<PAR>"]