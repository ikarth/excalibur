# -*- coding: utf-8 -*-


import tracery
import pycorpora
import itertools
from tracery.modifiers import base_english
import re
import numpy.random
import badwords
import copy
from uuid import uuid4
import uuid

#
# Island Description Text
#

corpora_rules = {
"flower": pycorpora.plants.flowers["flowers"],
"common_animal": pycorpora.animals.common["animals"],
"animal_use": ["for food","as pets","to make coats","to impress with their wealth","to eat","for their byproducts","as food","as watchguards","for their #xkcd_color# color","as symbols of #ritual_meaning#","to annoy their neighbors","because of their loud noises","as hunting beasts","and use them for divination","and claim they are edible","to eat","as <+feature tributary>tribute</+>"],
"to_hunt": ["to hunt","to see","to sight","to see for themselves","to look for","to find","to catch","to observe"],
"crayola_color": [c.get("color") for c in pycorpora.colors.crayola.get("colors")],
"xkcd_color": badwords.filterNaughtyWords([c.get("color") for c in pycorpora.colors.xkcd["colors"]]),
"ritual_meaning": list(itertools.chain.from_iterable([[c.get("name")] + c.get("synonyms") for c in pycorpora.archetypes.event["events"]])),
"gemstone": pycorpora.materials.gemstones["gemstones"],
"building_material": ["<+feature architecture material>{0}</+>".format(t) for t in pycorpora.materials.get_file("building-materials").get("building materials")],
"natural_material": ["<+feature architecture material>{0}</+>".format(t) for t in pycorpora.materials.get_file("natural-materials")["natural materials"]],
"drunkeness": pycorpora.words.states_of_drunkenness.get("states_of_drunkenness"),
"personal_noun": pycorpora.words.personal_nouns.get("personalNouns"),
"person_description": pycorpora.humans.descriptions.get("descriptions"),
"occupation": pycorpora.humans.occupations.get("occupations"),
"mood": pycorpora.humans.moods.get("moods"),
"diagnosis": [c.get("desc") for c in pycorpora.medicine.diagnoses.get("codes")],
"greek_titans": pycorpora.get_file("mythology/greek_titans")["greek_titans"],
"vegetable": pycorpora.foods.vegetables.get("vegetables"),
"fruit": pycorpora.foods.fruits.get("fruits"),
"wine_taste": pycorpora.foods.wine_descriptions.get("wine_descriptions"),
"condiment": [c.lower() for c in pycorpora.foods.condiments.get("condiments")],
"knot": pycorpora.technology.knots.get("knots"),
"unusual_thing": ["<+feature gemstone>#gemstone#</+>","<+feature fauna>#common_animal#</+>","<+feature fruit flora>#fruit#</+>","<+feature vegetable flora>#vegetable#</+>"],
"a_kind_of" :["a kind of","a sort of","something resembling","what you might think of as a","something that is almost, but not entirely, unlike", "what some refer to as a", "what I would consider", "something that vaugely resembles", "a variety of", "a species of", "what some call", "something that resembles", "a local variant of", "what they refer to as","what they consider to be","a kind of","a local","a peculiar","what they call","a singular","a unique","a pungent","a strong","a thick","a bitter","a sweet","a variety of","something that resembles","something with the flavor of"],
"heard_rumors_of":["heard could be found there","heard rumors of","once heard a tale about","heard tales they swore were true","once encountered before","remembered from past voyages","great expectations for","believed would be a sight worth seeing"],
"sailors":["sailors","tars","pirates"],
"isle":["isle","island","cay","key","atoll","islet","land","island","island","island","isle","isle","island"],
"island_name_construction":["#isle.capitalize# of the #person_description.capitalizeAll# #common_animal.capitalize#","#mood.capitalize# #isle.capitalize#","The #crayola_color# Isle of #greek_titans.capitalize#","#isle.capitalize# of #greek_titans.capitalize#","#gemstone.capitalizeAll# #vegetable.capitalizeAll# #isle.capitalize#"],
"inhabitants":["inhabitants","those who live there","inhabitants","island-dwellers","people","inhabitants","people of that place","islanders"],
"ocean_sea_name":["the great sea","the grand line","the ocean blue","the ocean sea","the world-ocean","the silver-sparkling sea","the distant sea","the wine-dark sea"],
}

#landscape
island_desc_flora = ["There is a flower there, a species of <+feature flora flower>#flower# with #xkcd_color# petals</+>. ", "A flower grows on the island, <+feature flora flower>#flower.a# with #xkcd_color# petals</+>. "]
island_desc_fauna = ["That place is known for a rare kind of <+feature fauna>#xkcd_color# #common_animal#</+>.","The #sailors# were eager #to_hunt# the <+feature fauna>#common_animal#</+>, which they had #heard_rumors_of#."]
island_desc_rumors_and_legends = ["Whenever they visit this island, #sailors# will conduct a kind of ritual, which they claim symbolizes <+feature ritual>#ritual_meaning#</+>.","The #sailors# told stories of #unusual_thing.a# from the island, which they had #heard_rumors_of#."]
#cuisine
island_desc_condiment = ["The #inhabitants# use #a_kind_of# <+feature condiment>#condiment#</+> in their cooking.", "The food of that island is characterized by #a_kind_of# <+feature condiment>#condiment#</+>.","The #inhabitants# have #a_kind_of# <+feature condiment>#condiment# made from the #fruit#</+> of that island.","The #inhabitants#' cooking is characterized by <+feature condiment>#condiment# with #wine_taste.a# flavor</+>.","The cuisine of that island is known for #a_kind_of# <+feature condiment>#wine_taste# #condiment#</+>."]
#domestication
island_desc_domestication = ["The #inhabitants# raise #common_animal.s#, #animal_use#.",
"The <+feature inhabitants>inhabitants</+> are known for their <+feature skills>fishing skills</+>.",
"The <+feature inhabitants>inhabitants</+> live off of <+feature flora fruit>coconuts</+> and <+feature resource>fish</+>.",
]

island_desc_buildings = [
"Around the <+feature landmark harbor no_one_harbor>principle harbor</+>, there were a great many #natural_material# buildings, forming a <+feature no_populous inhabitants>small town</+>.",
"The <+feature hills no_flat>hills</+> of the island were dotted with #natural_material# buildings, <+feature inhabitants>small farmsteads</+>, smokehouses, and evidences of industry.",
"The #building_material# <+feature inhabitants>tower</+> on the island's highest point is used as both a lighthouse and a kind of clock, its flags and lights marking time by day and by night. ",
"The <+feature inhabitants>largest building</+> on the island is the <+feature no_kingdom>governor's palace</+>, constructed out of #building_material#.",
]

island_desc_shape = [
"<+feature do_not_repeat></+><+feature size=small></+>This little island was of a triangular shape, and each side of it a mile long; it was surrounded by a <+feature reef>coral reef</+> which, as usual, presented a beautiful piece of marine scenery.",
"<+feature do_not_repeat></+><+feature size=tiny></+>The island was quite small, composed of <+feature landscape>rocks</+>, which rose sixty or eighty feet above the water, and was crowned with pleasant <+feature flora>shrubbery</+>. It had a wing extending out fifty feet or more, which was about thirty feet high, and through this there was a natural tunnel, having much the appearance of an artificial <+feature landscape>arch of stone</+>, and apparently large enough to allow a common-sized boat to pass.",
"<+feature do_not_repeat></+><+feature size=medium></+>Those who for the first time visit the #ocean_sea_name#, generally are surprised at the appearance of the islands when beheld from the sea. From the vague accounts we sometimes have of their beauty, many people are apt to picture to themselves enamelled and softly swelling plains, shaded over with delicious groves, and watered by purling brooks, and the entire country but little elevated above the surrounding ocean. The reality is very different; bold rock-bound coasts, with the surf beating high against the lofty <+feature landscape cliffs>cliffs</+>, and broken here and there into deep <+feature landscape>inlets</+>, which open to the view thickly-wooded <+feature landscape>valleys</+>, separated by the spurs of <+feature landscape mountains no_flat>mountains</+> clothed with tufted grass, and sweeping down towards the sea from an elevated and furrowed interior, form the principal features of these islands.",
"<+feature do_not_repeat></+><+feature size=small></+>There were two islands there. The distance from one to the other was about one mile. The small island <feature cliffs>rose very abruptly</+> many hundred feet above the sea. At the top was <+feature landmark>a rock with a conical form, which eternally seems on the point of rolling down with a tremendous crash into the sea</+>. The other island was larger, if less remarkable.",
"<+feature do_not_repeat></+><+feature size=medium></+>The newly discovered land was perceived to consist of a <+feature flat>flat</+> island fifteen leagues in length, <+feature no_hills no_mountains>without any hills</+>, all covered with <+feature landscape flora trees>trees</>, and having <+feature landmark>a great lake in the middle</+>.",
"<+feature do_not_repeat></+><+feature size=small></+>It is a flat and low-lying island of coral and limestone, its <+feature climate>tropical</+> climate moderated by northeast trade winds. ",
"<+feature size=small></+>It is a <+feature landscape flat no_mountains no_hills no_cliffs>low, nearly level</+> <+feature landscape>coral</+> island surrounded by a narrow fringing <+feature reef>reef</+>.",
"<+feature size=small></+>It is a <+feature landscape flat no_mountains no_hills no_cliffs>very flat place</+>, made up of several <+feature landscape>low-lying coral atolls</+>.",
"<+feature do_not_repeat></+><+feature size=medium></+>Though it's total area is thirty square miles, the land is <+feature landscape flat no_mountains no_hills no_cliffs>flat and low</+>. The highest elevation is only 4 meters.",
"<+feature size=small></+>The island is actually two <+feature landscape reef>coral atolls</+> thickly covered with <+feature flora trees landscape>coconut palms</+> and other vegetation.",
]


island_desc_clime = [
"The natural resources are negligible: the <+feature inhabitants>inhabitants</+> produce <+feature resource>salt</+>, <+feature resource>fish</+>, and <+feature resource>lobsters</+>, while the land is mostly <+feature landscape>rock</+> with sparse scrub oak and <+feature no_flora>few other trees</+>, plus some man-made salt ponds." ,
"<+feature no_inhabitants></+>Its most productive natural resource is the <+feature resource>guano deposits</+>.",
"The environment is <+feature no_trees>treeless</+>, with sparse and scattered vegetation consisting of <+feature flora>grasses, prostrate vines, and low growing shrubs</+>. <+feature no_inhabitants></+>It lacks fresh water and is primarily a nesting, roosting, and foraging habitat for seabirds, shorebirds, and marine wildlife.",
"The climate is <+feature climate>tropical</+>, with a rainy season from June to October.",
"The terrain is relatively <+feature flat no_mountains no_cliffs>flat</+> and rises gently to <+feature hills>central highland region</+>.",
"The climate is <+feature climate>tropical marine</+>: hot, humid, and moderated by trade winds.",
"The climate is <+feature climate>pleasant</+>, modified by the southeast trade winds for about nine months of the year with moderate rainfall.",
]

describe_reef = [
"<+feature do_not_repeat></+>The <+feature no_mountains no_hills landscape reefs>reefs</+> were not dry in any part, with the exception of some small black lumps, which at a distance resembled the round heads of penguins; the sea broke upon the edges, but inside the water was smooth, and of a light green colour. The water was very clear round the edges of the reef, and there was presented to view a new creation: new to those land-dwellers who observed it, but imitative of the old. There were wheat sheaves, mushrooms, stags horns, cabbage leaves, and a variety of other forms, glowing under water with vivid tints of every shade betwixt green, purple, brown, and white; equalling in beauty and excelling in grandeur the most favourite parterre of the curious florist. These were different species of coral and fungus, growing, as it were, out of the solid rock, and each had its peculiar form and shade of colouring; but whilst contemplating the richness of the scene, one could not long forget with what destruction it was pregnant. Different corals in a dead state, concreted into a solid mass of a dull-white colour, composed the stone of the reef. The penguin heads were lumps which stood higher than the rest; and being generally dry, were blackened by the weather; but even in these, the forms of the different corals, and some shells were distinguishable.",
"<+feature do_not_repeat></+>The edges of the <+feature no_mountains no_hills reefs landscape>reef</+>, but particularly on the outside where the sea broke, were the highest parts; within, there were pools and holes containing live corals, sponges, and sea eggs and cucumbers;^[* What we called sea cucumbers, from their shape, appears to have been the bêche de mer, or trepang; of which the Chinese make a soup, much esteemed in that country for its supposed invigorating qualities.] and many enormous cockles (chama gigas) were scattered upon different parts of the reef. At low water, this cockle seems most commonly to lie half open; but frequently closes with much noise; and the water within the shells then spouts up in a stream, three or four feet high: it was from this noise and the spouting of the water, that the #sailors# discovered them, for in other respects they were scarcely to be distinguished from the coral rock. A number of these cockles were taken on board the ship, and stewed in the coppers; but they were too rank to be agreeable food, and were eaten by few. One of them weighed 47½ lbs. as taken up, and contained 3lbs. 2 oz. of meat; but this size is much inferior to what was found by #famous_explorer#, upon the reefs of the coast further northward, or to several in the #British_Museum#; and I have since seen single shells more than four times the weight of the above shells and fish taken together. There were various small channels amongst the reefs, some of which led to the outer breakers, and through these the tide was rushing in; but none appeared to be an opening sufficiently wide for the #ship#."]





island_desc_no_inhabitants = ["<+feature no_inhabitants></+>There did not appear to be any fixed inhabitants; but proofs of the island having been visited some months before, were numerous; and upon the larger island there was a smoke."]

island_desc_soil = [
"<+feature do_not_repeat></+>The <+feature landscape>stone</+> which formed the basis of the island, and is scattered loosely over the surface, is a kind of <+feature landscape>porphyry</+>; a small piece of it, applied to the theodolite, did not affect the needle, although, on moving the instrument a few yards southward, the east variation was increased 2° 23'.",
"Not much vegetable earth was contained amongst the <+feature landscape>stones</+> on the surface, yet the island was thickly covered with <+feature landscape flora trees>trees and brush wood</+>, whose foliage was not devoid of luxuriance.",
"<+feature landscape flora trees>Pines</+> grow there, but they were more abundant, and seemingly larger, upon some other of the islands, particularly on the one to the <+feature nearby_island>westward</+>.",
]

island_desc_arrival = [
"They saw #island_name# directly ahead, rising like a deep blue cloud out of the sea.",
"They were then probably nearly seventy miles from it; and so <+feature mountains>high</+> and so blue did it appear that one might mistake it for a cloud resting over the island, and look for the island under it, until it gradually turned to a deader and <+feature trees>greener</+> color, and one could mark the inequalities upon its surface. ",
"At length the #sailors# could distinguish <+feature landscape flora trees>trees</+> and <+feature landscape>rocks</+>; and by the afternoon this beautiful island lay fairly before the #ship#, and they directed their course to <+feature landmark harbor one_harbor>the only harbor</+>. ",
"The <+feature landscape mountains cliffs>mountains</+> were high, but not so overhanging as they appeared to be by starlight. They seemed to bear off towards the centre of the island, and were <+feature landscape flora trees>green and well wooded</+>, with some large, and, I am told, exceedingly fertile <+feature landscape hills>valleys</+>, with mule-tracks leading to different parts of the island.",
]

island_landing = [
"The ship's boat coasted some distance before landing; followed by a long walk, first on a sandy beach and then among rocks composed of marine shells interlaid with coral and shells of infinite variety. The land was all one unbroken jungle. Much of the small timber was of a thorny kind, which seemed to bid defiance to human invasion. ",
"The #sailors# were chiefly engaged in picking up shells suitable for gambling purposes.",
]

"They continued sailing along with a fair wind and fine weather. "

island_history = [
"<+feature do_not_repeat></+><+feature size=large></+>This <+feature kingdom>kingdom</+> is on a large island, extending from east to west five hundred miles, and from north to south three hundred. Left and right from it there are as many as one hundred small islands, distant from one another ten, twenty, or even two hundred miles; but all subject to the large island. Most of them produce <+feature gemstones>pearls</+> and <+feature gemstones>precious stones of various kinds</+>; there is one which produces the pure and brilliant pearl--an island which would form a square of about three miles. The king employs <+feature inhabitants>men</+> to watch and protect it, and requires three out of every ten pearls which the collectors find.",
"<+feature do_not_repeat></+>The country originally had no human inhabitants, but was occupied only by spirits and <+feature monsters>nagas</+>, with which merchants of various countries carried on a trade. When the trafficking was taking place, the spirits did not show themselves. They simply set forth their precious commodities, with labels of the price attached to them; while the merchants made their purchases according to the price; and took the things away. Through the coming and going of the merchants in this way, when they went away, the people of their various countries heard how pleasant the land was, and flocked to it in numbers till it became a great nation. The climate is <+feature climate>temperate and attractive</+>, without any difference of summer and winter. The <+feature landscape flora>vegetation</+> is always luxuriant. Cultivation proceeds whenever men think fit: there are no fixed seasons for it.",
"<+feature do_not_repeat></+>This island had <+feature no_inhabitants>no human inhabitants</+>, but was occupied only by spirits and <+feature monsters>nagas</+>, with which merchants of various countries carried on a trade. When the trafficking was taking place, the spirits did not show themselves. They simply set forth their precious commodities, with labels of the price attached to them; while the merchants made their purchases according to the price; and took the things away. ",
"<+feature do_not_repeat></+>Through the many visits of merchants to the island, the people of their various countries heard how pleasant the land was, and <+feature inhabitants>flocked to it in numbers</+> till it became a <+feature populus>great nation</+>. The climate is <+feature climate>temperate and attractive</+>, without any difference of summer and winter. The <+feature landscape flora>vegetation</+> is always luxuriant. Cultivation proceeds whenever men think fit: there are no fixed seasons for it.",
"<+feature do_not_repeat></+>Historically, the economy was based on the cultivation of <+feature flora resource>sugarcane</+> and related activities. In recent years, however, the economy has diversified into <+feature resource>manufacturing</+> and <+feature resource>tourism</+>. The tourist industry is now a major employer of the labor force and a primary source of foreign exchange. ",
]












# Island Content Datastructure

island_content = [
{"tags":["fauna"],                "importance": 7,"content": island_desc_fauna},                  
{"tags":["fauna"],                "importance": 7,"content": island_desc_flora},
{"tags":["rumors"],               "importance": 7,"content": island_desc_rumors_and_legends},
{"tags":["inhabitants","cuisine"],"importance": 5,"content": island_desc_condiment},
{"tags":["inhabitants","fauna"],  "importance": 5,"content": island_desc_domestication},
{"tags":[],                       "importance": 6,"content": island_desc_buildings},
{"tags":["arrival"],              "importance": 15,"content": island_desc_arrival},
{"tags":["shape"],                "importance": 9,"content": island_desc_shape},
{"tags":["landscape"],            "importance": 8,"content": island_desc_soil},
{"tags":["landscape"],            "importance": 8,"content": describe_reef},
{"tags":[],                       "importance": 8,"content": island_desc_clime},
{"tags":["history"],              "importance": 1,"content": island_history},
{"tags":["no_inhabitants"],       "importance": 6,"content": island_desc_no_inhabitants},
#{"tags":[],                       "importance": 0,"content": []},
]



island_grammar = tracery.Grammar(corpora_rules)
island_grammar.add_modifiers(base_english)



############################


#
# Island tag translation
#

def expandDescriptionRecord(record):
    return record
    
def flattenDescriptionRecords(content):
    expanded_content = []
    for i in content: #{}
        records = i.get("content")
        for j in records:
            indiv = copy.deepcopy(i)
            indiv["content"] = j
            expanded_content.extend([indiv])            
    return expanded_content
    
def expandDescriptionRecords(content_records):
    content_records = flattenDescriptionRecords(content_records)
    record_id = 0
    for i in content_records:
        record_id += 1
        content = island_grammar.flatten(i.get("content"))
        i["id"] = record_id
        i["content"] = content
        new_tags = harvestTagsFromDescription(content)
        old_tags = i["tags"]
        new_old_tags = []
        for j in old_tags:
            if not hasattr(j, "get"):
                new_old_tags.append({"type": [j], "content":""})
            else:
                new_old_tags.append(j)            
            #print(new_old_tags)
        new_old_tags.extend(new_tags)
        new_old_tags.append({"type": ["id_{0}".format(str(record_id))], "content":""})
        i["tags"] = new_old_tags
        i["flat_tags"] = flattenTags(i)
    return content_records
        
def flattenTags(content_record):
    flat_tags = [i["type"] for i in content_record.get("tags")]
    return list(itertools.chain.from_iterable(flat_tags))
    
def translateMarkupToTag(markup):
    tag = {}
    markup_pattern = re.compile("<\+feature (.*?)>")
    content_pattern = re.compile("<\+feature .*?>(.*?)</\+>")
    tag["type"] = markup_pattern.search(markup).group(1).split()
    tag["content"] = content_pattern.search(markup).group(1)
    return tag

def harvestTagsFromDescription(description):
    """
    Given a description text with markup of the signifigant features, 
    translate that into tags that the engine understands and can use for 
    future content and callbacks."
    """
    if not isinstance(description, str):
        return [] # Only works on strings...
    tags = [translateMarkupToTag(t.group()) for t in re.finditer("<\+feature .*?>.*?</\+>", description)]
    return tags
    
do_not_repeat = set()
    
def getIslandContent():
    content_records = expandDescriptionRecords(island_content)
    global do_not_repeat
    for cr in content_records:
        if "do_not_repeat" in cr["flat_tags"]:
            do_not_repeat = do_not_repeat.union(set([i for i in cr["flat_tags"] if "id_" in i]))
    return content_records
    

def compareTagsOneWay(current_tags, new_tags):
    """
    Returns True if there is no conflict between the two lists of tags.
    """
    #print("=%=%=%=")
    #print(current_tags)
    #print("=")
    #print(new_tags)
    id_list1 = [i for i in current_tags if "id_" in i]
    id_list2 = [i for i in new_tags if "id_" in i]
    #print(id_list1)
    #print(id_list2)
    if None != id_list1 and None != id_list2:
        if len(id_list1) > 0 and len(id_list2) > 0:
            for idi in id_list1:
                if idi in id_list2:
                    #print("Same ID")
                    return False # don't use the same record twice
            for idi in id_list2:
                if idi in id_list1:
                    #print("Same ID")
                    return False # don't use the same record twice
    forbid_list = [i for i in current_tags if "no_" in i]
    for i in forbid_list:
        #print("Forbid!", end="")
        #print(forbid_list, end=": ")
        check_for = copy.deepcopy(i)
        check_for = check_for.replace("no_","",1)
        #print(check_for,end="-> ")
        for j in new_tags:
            #print(j, end=",")
            if check_for == j:        
                #print("No")
                return False # "no_" tags can never co-exist with their positive counterparts
    cur_size_list = set([i for i in current_tags if "size=" in i])
    new_size_list = set([i for i in new_tags if "size=" in i])
    if len(cur_size_list.union(new_size_list)) > 1:
        #print("Size Mismatch")
        return False # At most one size is allowed
    harbor_list = set([i for i in current_tags if "_harbor" in i]).union(set([i for i in new_tags if "_harbor" in i]))
    if len(harbor_list) > 1:
        #print("Harbor")
        return False # All _harbor characteristics are mutually exclusive        
    if (len(list([i for i in current_tags if "shape" in i]) + list([i for i in new_tags if "shape" in i])) > 1):
        #print("Shape")
        return False #only one shape allowed
    if (len(list([i for i in current_tags if "condiment" in i]) + list([i for i in new_tags if "condiment" in i])) > 1):
        #print("Condiment")
        return False #only one condiment allowed
    if (len(list([i for i in current_tags if "history" in i]) + list([i for i in new_tags if "history" in i])) > 1):
        #print("History")
        return False #only one history allowed
    if (len(list([i for i in current_tags if "climate" in i]) + list([i for i in new_tags if "climate" in i])) > 1):
        return False #only one climate allowed
    if (len(list([i for i in current_tags if "material" in i]) + list([i for i in new_tags if "material" in i])) > 1):
        return False #only one architectural material allowed
    #print("True")
    return True
    

def compareTags(current_tags, new_tags):            
    """
    Returns True if there is no conflict between the two lists of tags.
    """
    if len(do_not_repeat.intersection(set([i for i in new_tags if "id_" in i]))) > 0:
        return False # new item is on the do-not-repeat list
    return (compareTagsOneWay(current_tags, new_tags)) and (compareTagsOneWay(new_tags, current_tags))    
    
#################################    







    

#test_string = numpy.random.choice(["The #inhabitants# use #a_kind_of# <+feature condiment>#condiment#</+> in their cooking.", "The food of that island is characterized by #a_kind_of# <+feature condiment>#condiment#</+>.","They have #a_kind_of# <+feature condiment>#condiment# made from the #fruit#</+> of that island.","Their cooking is characterized by <+feature condiment>#condiment# with #wine_taste.a# flavor</+>.","The cuisine of that island is known for #a_kind_of# <+feature condiment>#wine_taste# #condiment#</+>."])
#test = island_grammar.flatten(test_string)
#print(test)
#tags = harvestTagsFromDescription(test)
#print(tags)
#print(tags[0])
#print(tags[0].group())



"I was called on deck to stand my watch at about three in the morning, and I shall never forget the peculiar sensation which I experienced on finding myself once more surrounded by land, feeling the night-breeze coming from off shore, and hearing the frogs and crickets. The mountains seemed almost to hang over us, and apparently from the very heart of them there came out, at regular intervals, a loud echoing sound, which affected me as hardly human. We saw no lights, and could hardly account for the sound, until the mate, who had been there before, told us that it was the ``Alerta'' of the Chilian soldiers, who were stationed over some convicts confined in caves nearly half-way up the mountain. At the expiration of my watch, I went below, feeling not a little anxious for the day, that I might see more nearly, and perhaps tread upon, this romantic, I may almost say classic, island. " 
"When all hands were called it was nearly sunrise, and between that time and breakfast, although quite busy on board in getting up water-casks, &c., I had a good view of the objects about me. The harbor was nearly land-locked, and at the head of it was a landing, protected by a small breakwater of stones, upon which two large boats were hauled up, with a sentry standing over them. Near this was a variety of huts or cottages, nearly a hundred in number, the best of them built of mud or unburnt clay, and whitewashed, but the greater part Robinson Crusoe like,— only of posts and branches of trees. The governor's house, as it is called, was the most conspicuous, being large, with grated windows, plastered walls, and roof of red tiles; yet, like all the rest, only of one story. Near it was a small chapel, distinguished by a cross; and a long, low, brown-looking building, surrounded by something like a palisade, from which an old and dingy-looking Chilian flag was flying. This, of course, was dignified by the title of Presidio. A sentinel was stationed at the chapel, another at the governor's house, and a few soldiers, armed with bayonets, looking rather ragged, with shoes out at the toes, were strolling about among the houses, or waiting at the landing-place for our boat to come ashore."

"Arriving at the entrance soon after sundown, we found a Chilian man-of-war brig, the only vessel, coming out. "
"She hailed us; and an officer on board, whom we supposed to be an American, advised us to run in before night, and said that they were bound to Valparaiso. "
"We ran immediately for the anchorage, but, owing to the winds which drew about the mountains and came to us in flaws from different points of the compass, we did not come to an anchor until nearly midnight. "
"We had a boat ahead all the time that we were working in, and those aboard ship were continually bracing the yards about for every puff that struck us, until about twelve o'clock, when we came to in forty fathoms water, and our anchor struck bottom for the first time since we left Boston,— one hundred and three days. "
"We were then divided into three watches, and thus stood out the remainder of the night."


###########################################


def flattenIslandTags(island_tags):
    ctags = list(itertools.chain.from_iterable([i["tags"] for i in island_tags]))
    if len(ctags) > 0:
        ctags = [j["type"] for j in ctags]
        ctags = list(itertools.chain.from_iterable(ctags))
    return ctags

def flattenContentTags(content_tags)    :
    ctags = [i["type"] for i in content_tags]
    ctags = list(itertools.chain.from_iterable(ctags))
    return ctags
    
def generateDescription(island, content):
    new_desc = []
    #print("=^=^=")
    #ctags = list(itertools.chain.from_iterable([i["tags"] for i in island["description"]]))
    #if len(ctags) > 0:
    #    ctags = [j["type"] for j in ctags]
    #    ctags = list(itertools.chain.from_iterable(ctags))
    ctags = flattenIslandTags(island["description"])
    island["tags"] = ctags
    #print(ctags)
    #print("==^==")
    if len(content) <= 0:
        return island
    valid_content = [i for i in content if compareTags(ctags, flattenContentTags(i["tags"]))]
    #print(len(valid_content))
    if len(valid_content) <= 0:
        return generateDescription(island, []) # get final ctags
    #print(valid_content)
    new_desc = numpy.random.choice(valid_content)
    island["description"].append(new_desc)
    #print("==&==")
    
    return island

def generateIslandName(island):
    name = island_grammar.flatten("#island_name_construction#")
    return name
    
def generateIsland():
    island = {"description":[], "name":"", "tags":[], "arrival":[], "uuid": uuid4()}
    content = getIslandContent()
    for i in range(6):
        island = generateDescription(island, content)
        island["name"] = generateIslandName(island)
    return island
    
def describeIsland(island, trim_tags=True):
    if None == island:
        return None
    desc = ""
    para_breaks = [{"tags":[],"importance":2, "content":"<PAR>"},{"tags":[],"importance":6, "content":"<PAR>"},{"tags":[],"importance":4, "content":"<PAR>"},{"tags":[],"importance":8, "content":"<PAR>"},{"tags":[],"importance":14, "content":"<PAR>"}]
    sort_desc = sorted(island["description"] + para_breaks, key=lambda i: i.get("importance"), reverse=True)
    specific_island_rules = {"island_name": island["name"]}
    desc_grammar = tracery.Grammar(specific_island_rules)
    desc_grammar.add_modifiers(base_english)
    for i in sort_desc:
        desc = desc + i["content"] + " "
    desc = desc.replace("  "," ")
    if trim_tags:
        desc = re.sub(" ?<PAR> ?", "<PAR>", desc)
        desc = re.sub("<\+feature.*?>", "", desc)
        desc = re.sub("</\+>", "", desc)
    desc = re.sub("\(\((.*?)\)\)", "#\g<1>#", desc)
    desc = desc_grammar.flatten(desc)
    desc = re.sub("\(\((.*?)\)\)", "#\g<1>#", desc)
    return desc 
    
    
#put_island_content = getIslandContent()
print("\n____...ttt^ttt...____\n")
il = generateIsland()
print(describeIsland(il))
print(il["tags"])

#print(expandDescriptionRecords(island_content))
#for i in expandDescriptionRecords(island_content):
#    #print("")
#    #print(i)
#    print(flattenTags(i))

_master_tag_list = []

def masterTagList(islands):
    global _master_tag_list
    _master_tag_list = list(itertools.chain.from_iterable([i["tags"] for i in islands]))
    return _master_tag_list

def generateArchipegalo():
    global _master_tag_list 
    _master_tag_list = []
    islands = []
    for i in range(36):
        islands.append(generateIsland())
        masterTagList(islands)
    return islands

####################################################

#
# Public Interface
#
    
archipegalo = generateArchipegalo() 

def getArchipegalo():
    global archipegalo
    if archipegalo == None:
        archipegalo = generateArchipegalo() 
    return archipegalo
    
def getRandomDestination():
    return numpy.random.choice(getArchipegalo())
    
def getPlaceId(place):
    #print("===id===")
    #print(place.get("uuid"))
    return place.get("uuid")
    
def getCuisine():
    cuisine_list = []
    for i in getArchipegalo():
        tags = list(itertools.chain.from_iterable([c["tags"] for c in i["description"]]))
        #print(tags)
        for t in tags:
            if ("condiment" in t["type"]) or ("cuisine" in t["type"]):
                if t["content"] != "":
                    cuisine_list.append("{0} from {1}".format(t["content"], i["name"]))
    return cuisine_list

    
def findPlaceById(place_id):
    #print("---find---")
    #print(place_id)
    if place_id == None:
        return None
    result = [x for x in getArchipegalo() if uuid.UUID(hex=place_id) == x.get("uuid")][0]
    #print(result)
    if result == []:
        return None
    
    return result
    
def getPlaceName(place):
    if None == place:
        return None
    return str(place.get("name"))# + str( place.get("uuid"))
    
def getPlaceDescription(place):
    if None == place:
        return None
    return describeIsland(place)