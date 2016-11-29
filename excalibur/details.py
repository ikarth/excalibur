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


quotes = [["Nullus enim locus sine genio est.","_Servius_"],
["  To run o'er better waters hoists its sail  \n  The little vessel of my genius now,  \n  That leaves behind itself a sea so cruel;  ", "Dante"]
]

poetry = [
# Edgar Allen Poe
"""
  Up rose the maiden in the yellow night,  
  The single-mooned eve!-on earth we plight  
  Our faith to one love--and one moon adore--  
  The birth-place of young Beauty had no more.  
  As sprang that yellow star from downy hours,  
  Up rose the maiden from her shrine of flowers,  
  And bent o'er sheeny mountain and dim plain  
  Her way--but left not yet her Therasaean reign ^[Therasaea, or Therasea, the island mentioned by Seneca, which, in a moment, arose from the sea to the eyes of astonished mariners.]  
""","""
      My beautiful one!
    Whose harshest idea
      Will to melody run,
    O! is it thy will
      On the breezes to toss?
    Or, capriciously still,
      Like the lone Albatross,^[The Albatross is said to sleep on the wing.]
    Incumbent on night
      (As she on the air)
    To keep watch with delight
      On the harmony there?
""","""
    No magic shall sever  
      Thy music from thee.  
    Thou hast bound many eyes  
      In a dreamy sleep--  
    But the strains still arise  
      Which _thy_ vigilance keep--  
    The sound of the rain  
      Which leaps down to the flower,  
    And dances again  
      In the rhythm of the shower--  
    The murmur that springs ^[I met with this idea in an old English tale, which I am now unable to obtain and quote from memory:  \n  \"The verie essence and, as it were, springe heade and origine of all  \n  musiche is the verie pleasaunte sounde which the trees of the forest  \n  do make when they growe.\"  ]   
      From the growing of grass  
    Are the music of things--  
      But are modell'd, alas!  
""","""
    And without care of having any rest  
  We mounted up, he first and I the second,  
    Till I beheld through a round aperture  
    Some of the beauteous things that Heaven doth bear;  
  Thence we came forth to rebehold the stars.  
""",# Dante


]

sea_stories = [
#Edgar Allen Poe               
"""
There was an island I once saw, at a calm twilight...So mirror-like was the glassy water, that it was scarcely possible to say at what point upon the slope of the emerald turf its crystal dominion began. My position enabled me to include in a single view both the eastern and western extremities of the islet, and I observed a singularly-marked difference in their aspects. The latter was all one radiant harem of garden beauties. It glowed and blushed beneath the eye of the slant sunlight, and fairly laughed with flowers. The grass was short, springy, sweet-scented, and Asphodel-interspersed. The trees were lithe, mirthful, erect, bright, slender, and graceful, of eastern figure and foliage, with bark smooth, glossy, and parti-colored. There seemed a deep sense of life and joy about all, and although no airs blew from out the heavens, yet everything had motion through the gentle sweepings to and fro of innumerable butterflies, that might have been mistaken for tulips with wings ^[\"Florem putares nare per liquidum aethera.\" \'P. Commire\'.
The other or eastern end of the isle was whelmed in the blackest shade. A sombre, yet beautiful and peaceful gloom, here pervaded all things. The trees were dark in color and mournful in form and attitude-- wreathing themselves into sad, solemn, and spectral shapes, that conveyed ideas of mortal sorrow and untimely death. The grass wore the deep tint of the cypress, and the heads of its blades hung droopingly, and hither and thither among it were many small unsightly hillocks, low and narrow, and not very long, that had the aspect of graves, but were not, although over and all about them the rue and the rosemary clambered. The shades of the trees fell heavily upon the water, and seemed to bury itself therein, impregnating the depths of the element with darkness. I fancied that each shadow, as the sun descended lower and lower, separated itself sullenly from the trunk that gave it birth, and thus became absorbed by the stream, while other shadows issued momently from the trees, taking the place of their predecessors thus entombed.
This idea having once seized upon my fancy greatly excited it, and I lost myself forthwith in reverie. \"If ever island were enchanted,\" said I to myself, \"this is it. This is the haunt of the few gentle Fays who remain from the wreck of the race. Are these green tombs theirs?--or do they yield up their sweet lives as mankind yield up their own? In dying, do they not rather waste away mournfully, rendering unto God little by little their existence, as these trees render up shadow after shadow, exhausting their substance unto dissolution? What the wasting tree is to the water that imbibes its shade, growing thus blacker by what it preys upon, may not the life of the Fay be to the death which engulfs it?\"
As I thus mused, with half-shut eyes, while the sun sank rapidly to rest, and eddying currents careered round and round the island, bearing upon their bosom large dazzling white flakes of the bark of the sycamore, flakes which, in their multiform positions upon the water, a quick imagination might have converted into anything it pleased; while I thus mused, it appeared to me that the form of one of those very Fays about whom I had been pondering, made its way slowly into the darkness from out the light at the western end of the island. She stood erect in a singularly fragile canoe, and urged it with the mere phantom of an oar. While within the influence of the lingering sunbeams, her attitude seemed indicative of joy, but sorrow deformed it as she passed within the shade. Slowly she glided along, and at length rounded the islet and re-entered the region of light. \"The revolution which has just been made by the Fay,\" continued I musingly, \"is the cycle of the brief year of her life. She has floated through her winter and through her summer. She is a year nearer unto death: for I did not fail to see that as she came into the shade, her shadow fell from her, and was swallowed up in the dark water, making its blackness more black.\"
And again the boat appeared and the Fay, but about the attitude of the latter there was more of care and uncertainty and less of elastic joy. She floated again from out the light and into the gloom (which deepened momently), and again her shadow fell from her into the ebony water, and became absorbed into its blackness. And again and again she made the circuit of the island (while the sun rushed down to his slumbers), and at each issuing into the light there was more sorrow about her person, while it grew feebler and far fainter and more indistinct, and at each passage into the gloom there fell from her a darker shade, which became whelmed in a shadow more black. But at length, when the sun had utterly departed, the Fay, now the mere ghost of her former self, went disconsolately with her boat into the region of the ebony flood, and that she issued thence at all I cannot say, for darkness fell over all things, and I beheld her magical figure no more.
"""
]

discourses = [
# Edgar Allen Poe              
"We shall reach, however, more immediately a distinct conception of what true Poetry is, by mere reference to a few of the simple elements which induce in the Poet himself the true poetical effect. He recognizes the ambrosia which nourishes his soul in the bright orbs that shine in Heaven, in the volutes of the flower, in the clustering of low shrubberies, in the waving of the grain-fields, in the slanting of tall eastern trees, in the blue distance of mountains, in the grouping of clouds, in the twinkling of half-hidden brooks, in the gleaming of silver rivers, in the repose of sequestered lakes, in the star-mirroring depths of lonely wells. He perceives it in the songs of birds, in the harp of AEolus, in the sighing of the night-wind, in the repining voice of the forest, in the surf that complains to the shore, in the fresh breath of the woods, in the scent of the violet, in the voluptuous perfume of the hyacinth, in the suggestive odor that comes to him at eventide from far-distant undiscovered islands, over dim oceans, illimitable and unexplored. He owns it in all noble thoughts, in all unworldly motives, in all holy impulses, in all chivalrous, generous, and self-sacrificing deeds. He feels it in the beauty of woman, in the grace of her step, in the lustre of her eye, in the melody of her voice, in her soft laughter, in her sigh, in the harmony of the rustling of her robes. He deeply feels it in her winning endearments, in her burning enthusiasms, in her gentle charities, in her meek and devotional endurance, but above all, ah, far above all, he kneels to it, he worships it in the faith, in the purity, in the strength, in the altogether divine majesty of her _love._"
              ]

histories = [
"#history_hero# is accused of going to war with Samos to save the Milesians. These states were at war about the possession of the city of Priene, and the Samians, who were victorious, would not lay down their arms and allow the Athenians to settle the matter by arbitration, as they ordered them to do. For this reason Pericles proceeded to Samos, put an end to the oligarchical form of government there, and sent fifty hostages and as many children to Lemnos, to insure the good behavior of the leading men. It is said that each of these hostages offered him a talent for his own freedom, and that much more was offered by that party which was loath to see a democracy established in the city. Besides all this, Pissuthnes the Persian, who had a liking for the Samians, sent and offered him ten thousand pieces of gold if he would spare the city. Pericles, however, took none of these bribes, but dealt with Samos as he had previously determined, and returned to Athens. The Samians now at once revolted, as Pissuthnes managed to get them back their hostages, and furnished them with the means of carrying on the war. Pericles now made a second expedition against them, and found them in no mind to submit quietly, but determined to dispute the empire of the seas with the Athenians. Pericles gained a signal victory over them in a sea-fight off the Goats' Island, beating a fleet of seventy ships with only forty-four, twenty of which were transports.",
"Simultaneously with his victory and the flight of the enemy he obtained command of the harbor of Samos, and besieged the Samians in their city. They, in spite of their defeat, still possessed courage enough to sally out and fight a battle under the walls; but soon a larger force arrived from Athens, and the Samians were completely blockaded."
             ]              

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


sunrise = [
"Much has been said of the sunrise at sea; but it will not compare with the sunrise on shore. It lacks the accompaniments of the songs of birds, the awakening hum of humanity, and the glancing of the first beams upon trees, hills, spires, and house-tops, to give it life and spirit. There is no scenery. But, although the actual rise of the sun at sea is not so beautiful, yet nothing will compare for melancholy and dreariness with the early breaking of day upon \"Old Ocean's gray and melancholy waste.\"",
"There is something in the first gray streaks stretching along the eastern horizon and throwing an indistinct light upon the face of the deep, which combines with the boundlessness and unknown depth of the sea around, and gives one a feeling of loneliness, of dread, and of melancholy foreboding, which nothing else in nature can. This gradually passes away as the light grows brighter, and when the sun comes up, the ordinary monotonous sea day begins."
]


cat_facts = ["<PAR>Cats have any amount of wiliness about them. A dog would scarcely think of hiding below a bush until its prey came within reach; but cats are adepts at an ambuscade. A cat knows by experience that a bird--say a sparrow--looks almost in every direction, saving directly beneath it, and so pussy always steals a march on it, from below. If a bird is foolish enough to alight on the top of a clothes-pole, pussy has a very easy victory. It is that same habit of never looking downwards, which causes those large birds, which alight on a ship's yards at sea, to be so easily captured by the sailors.<PAR>"]


sailing = [
#sailing
"With a favorable wind, they proceeded eastward for three days, and then they encountered a great wind. ",
"On the sea hereabouts there are many pirates, to meet with whom is speedy death. ",
"The great ocean spreads out, a boundless expanse. ",
"There is no knowing east or west; only by observing the sun, moon, and stars was it possible to go forward. ",
"The sea was deep and bottomless, and there was no place where they could drop anchor and stop. ",
# overcast, no navigation...
"If the weather were dark and rainy, the ship went as she was carried by the wind, without any definite course. ",
"In the darkness of the night, only the great waves were to be seen, breaking on one another, and emitting a brightness like that of fire, with huge turtles and other monsters of the deep all about. ",
"But when the sky became clear, they could tell east and west, and the ship again went forward in the right direction. ",
"If she had come on any hidden rock, there would have been no way of escape.",
"At this time the sky continued very dark and gloomy, and the sailing-masters looked at one another and made mistakes. ",
# land lubbers aboard
"The #lubbers# were full of terror, not knowing where they were going. "
# clear skies
"The sky presented a clear expanse of the most delicate blue, except along the skirts of the horizon, where you might see a thin drapery of pale clouds which never varied their form or colour. ",
"The long, measured, dirge-like well of the #ocean_sea_name# came rolling along, with its surface broken by little tiny waves, sparkling in the sunshine. ",
"Every now and then a shoal of flying fish, scared from the water under the bows, would leap into the air, and fall the next moment like a shower of silver into the sea. ",
"Then you would see the superb albicore, with his glittering sides, sailing aloft, and often describing an arc in his descent, disappear on the surface of the water. ",
"Far off, the lofty jet of the whale might be seen, and nearer at hand the prowling shark, that villainous footpad of the seas, would come skulking along, and, at a wary distance, regard us with his evil eye. ",
"At times, some shapeless monster of the deep, floating on the surface, would, as we approached, sink slowly into the blue waters, and fade away from the sight. ",
"But the most impressive feature of the scene was the almost unbroken silence that reigned over sky and water. ",
"Scarcely a sound could be heard but the occasional breathing of the grampus, and the rippling at the cut-water. ",


           ]
           
           
         