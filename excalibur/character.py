# -*- coding: utf-8 -*-

import tracery
from tracery.modifiers import base_english
import random
import pycorpora
import badwords
import itertools
from uuid import uuid4
import re

class Character:
    def __init__(self, char_name, char_gender="female"):
        self._id = char_name.upper().replace(" ", "_").replace("\"", "_").replace("\'", "_")
        self._full_name = char_name
        self._plain_name = char_name
        self._nickname = ""
        self._given_name = char_name
        self._family_name = ""
        self._name_style = "western_family_name"
        self._gender = char_gender
        self._crew_title = ""
        self._ship_id = ""
        self._weapon_name = ""
        self._weapon_tags = []
        self._character_tags = []
        self._uuid = uuid4()
        self._description = ""
        
    @property
    def description(self):
        return self._description
        
    @description.setter
    def description(self, value):
        self._description = value
    
    def getId(self):
        return self._id
        
    @property
    def id(self):
        return self._id
                
    @property
    def ship_id(self):
        return self._ship_id
    
    @ship_id.setter
    def ship_id(self, value):
        self._ship_id = value
        
    @property
    def name(self):
        return self._full_name
    
    @name.setter
    def name(self, value):
        self._full_name = value
        
    @property
    def gender(self):
        return self._gender
    
    @gender.setter
    def gender(self, value):
        self._gender = value
    
    # Kennings = alternate ways to refer to the character
    @property
    def kennings(self):
        kennings = []
        kennings.append(self._full_name)
        self._kennings = copy.deepcopy(kennings)
        return self._kennings
    
    @kennings.setter
    def kennings(self, value):
        self._kennings = value
        
        
    @property
    def possessive(self):
        return str(self._full_name) + "'s"
        
    @property
    def weapon_name(self):
        return self._weapon_name
    
    @weapon_name.setter
    def weapon_name(self, value):
        self._weapon_name = value
        
    @property
    def weapon_tags(self):
        return self._weapon_tags
        
    @weapon_tags.setter
    def weapon_tags(self, value):    
        self._weapon_tags = value
        
    def Display(self):
        print("{0}, {1}, who carries a {2}".format(self._full_name, self._crew_title, self._weapon_name))
        
    def isShip(self):
        return "ship" in self._character_tags
    
    def isCrew(self):
        return "crew" in self._character_tags
        
    def isSea(self):
        return "sea" in self._character_tags
        
    def addTag(self, tag):
        self._character_tags.append(tag)
    
    def getTags(self):
        return self._character_tags

        
    # Pronoun Object
    @property
    def him(self):
        if self.gender is "female" or self.gender is "ship":
            return "her"
        if self.gender is "first_plural":
            return "us"
        if self.gender is "third_plural":
            return "them"
        if self.gender is "neuter":
            return "it"
        if self.gender is "first":
            return "me"
        return "him"
    
    # Possessive Pronoun
    @property
    def his(self):
        if self.gender is "female" or self.gender is "ship":
            return "hers"
        if self.gender is "first_plural":
            return "ours"
        if self.gender is "third_plural":
            return "theirs"
        if self.gender is "neuter":
            return "its"
        if self.gender is "first":
            return "mine"
        return "his"
    
    # Pronoun Subject
    @property
    def she(self):
        if self.gender is "female" or self.gender is "ship":
            return "she"
        if self.gender is "first_plural":
            return "we"
        if self.gender is "third_plural":
            return "they"
        if self.gender is "neuter":
            return "it"
        if self.gender is "first":
            return "I"
        return "he"
    
    # Possessive Adjective
    @property
    def her(self):
        if self.gender is "female" or self.gender is "ship":
            return "her"
        if self.gender is "first_plural":
            return "our"
        if self.gender is "third_plural":
            return "their"
        if self.gender is "neuter":
            return "its"
        if self.gender is "first":
            return "my"
        return "his"
    
    # Reflexive Pronouns
    @property
    def herself(self):
        if self.gender is "female" or self.gender is "ship":
            return "herself"
        if self.gender is "first_plural":
            return "ourselves"
        if self.gender is "third_plural":
            return "themselves"
        if self.gender is "neuter":
            return "itself"
        if self.gender is "first":
            return "myself"
        return "himself"
        
class Crew(Character):
    def __init__(self, crew_id):
        self._crew_id = crew_id
        self._gender = "third_plural"
        self._gang = []
        
    def getId(self):
        return self._crew_id
        
    def addCrew(self, crew_member):
        self._gang.append(crew_member)
        
    def getCrew(self):
        return self._gang
        
    def Display(self):
        for c in self._gang:
            c.Display()
    
class Ship(Character):
    def __init__(self, ship_name, ship_characteristics):
        super(Ship, self).__init__(ship_name, "ship")
        self._id = uuid4()
        self._ship_id = ship_name.upper().replace(" ", "_").replace("\"", "_").replace("\'", "_")
        self._ship_type = ship_characteristics["type"]
        self._crew_complement = ship_characteristics["crew complement"]
        self._tonnage = ship_characteristics["tonnage"]
        self._speed = ship_characteristics["speed"]
        self._gun_complement = ship_characteristics["gun complement"]
        self._masts = ship_characteristics["masts"]
        self._crew = Crew("{0}_CREW".format(self._ship_id))
        self._ship_name = ship_name
        self._full_name = ship_name
        self._nickname = ship_name
        self._given_name = ship_name
        self._family_name = ship_name
        self._name_style = "ship_name"
        self._gender = "ship"
        
    def getId(self):
        return self._ship_id

    @property
    def id(self):
        return self._ship_id
        
    @property
    def ship_id(self):
        return self._ship_id
    
    @ship_id.setter
    def ship_id(self, value):
        self._ship_id = value.upper().replace(" ", "_")
        
    def Display(self):
        print("{0}, a {2}-masted {1}".format(self._ship_name, self._ship_type, len(self._masts)))
        self._crew.Display()
        
    def addCrew(self,crew_member):
        crew_member.ship_id = self._ship_id
        self._crew.addCrew(crew_member)
        
    def findInCrew(self, crewtag):
        result = None
        for c in self._crew.getCrew():
            if crewtag in c._crew_title:
                result = c
        return result
        
    def getCaptain(self):
        swaim = self.findInCrew("captain")
        return swaim
        
    def getBoatswain(self):
        swain = self.findInCrew("boatswain")
        if None == swain:
            swain = self.findInCrew("pilot")
        if None == swain:
            swain = self.findInCrew("first mate")
        if None == swain:
            swain = self.findInCrew("navigator")
        if None == swain:
            swain = self.findInCrew("second mate")
        if None == swain:
            swain = self.findInCrew("captain")
        return swain
        
    def getRandomCrewmember(self):
        return random.choice(self._crew.getCrew())
            
        
    
ship_templates = [
 {"type": "brig",
 "masts": [["foremast", "square-rigged"],["main mast","square-rigged"]],
  "tonnage":300,
  "crew complement":[16, 155],
  "gun complement":20,
  "speed":[0, 1, 2, 5, 5],# in irons, close-hauled, beam-reach, broad reach, running
  "uses":["merchant","navy","pirate"]
  },
{"type": "barque",
"masts": 
  [["foremast", "square-rigged"],["main mast","square-rigged"],["mizzenmast","fore-and-aft rigged"]],
  "tonnage":350,
  "crew complement":[12, 94],
  "gun complement":22,
  "speed":[0, 3, 4, 4, 4],# in irons, close-hauled, beam-reach, broad reach, running
  "uses":["merchant","navy","pirate"]
  },
{"type": "barquentine",
"masts": 
  [["foremast", "square-rigged"],["main mast","fore-and-aft rigged"],["mizzenmast","fore-and-aft rigged"]],
  "tonnage":300,
  "crew complement":[10, 74],
  "gun complement":20,
  "speed":[0, 4, 4, 4, 4],# in irons, close-hauled, beam-reach, broad reach, running
  "uses":["merchant","navy","pirate"]
  },
 {"type": "frigate",
 "masts": 
  [["foremast", "square-rigged"],["main mast","square-rigged"],["mizzenmast","square-rigged"]],
  "tonnage":2000,
  "crew complement":[50, 450],
  "gun complement":52,
  "speed":[0, 1, 1, 5, 6],# in irons, close-hauled, beam-reach, broad reach, running
  "uses":["navy"]
  },
 {"type": "mistico",
 "masts": [["jib"],["foremast", "lateen sail"],["main mast","lateen sail"]],
  "tonnage":80,
  "crew complement":[5, 9],
  "gun complement":4,
  "speed":[0, 4, 5, 5, 3],# in irons, close-hauled, beam-reach, broad reach, running
  "uses":["fishing","pirate","boat"]
  }
  ]
  
ship_names={"pirate":["Revenge","Ranger","Carolina","Robert","Good Intent","Walrus","Margaret",
"Crowley","Bentenmaru","Black Flag","Crossbones"],
"merchant":["Merchant Adventurer","Medford","Melita","Mentor","Mercator","Merchant","Merchant's Hope",
"Mercury","Mermaid","Merryland Merchant","Montague","Monomia","Nansimum","Nassau","Neptune's Barge",
"Newry Assistance","den Norske Klippe","Nuestra Ira","Nymph","Numa","Olive","Octavia","Oake","Ocean",
"Olive Tree","Oracle","Only Son","Only Daughter","Onslow","Orient","Orion","Orison","Orizimbo",
"Oryza","Orleans","Osgood","Ossian","Oswego","Pacific","Pallas","Packet Eliza","Patience","Philedini",
"Phanton ","Plaisance","Pineapple","Pied Cow","Pleasant","Pleasure","Plough of Woolwich","Polly",
"Pomona","Poppett","Port Royal","Portia","Portland","Portsmouth","Post Boy","Postilion","Princess Caroline",
"Priscilla","Prosperity","Prosperous","Prophet Daniel","de Pumerlander","Queen Margaret","Rachel",
"Radius","Rainbow","Rajah","Rambler","Rathornis","Rawley","Rebecca","Restoration","Resolution","Regard",
"Reindeer","Recovery","Recovery II","Unsinkable II","Richard & Ann","Reuben & Eliza","Rosetta","Rosevvay",
"Rose","Ross","Rotchell Merchant","Rover","Rowand","Spring","Roxana","Royal Charlotte","Royal Exchange","Royal Judith","Royal Oak","Royal Union","Sarah Sheaffe","Savage","Savary","Schuylkill","Scipio","Scorton Polly",
"Sea Adventure","Sea Bird","Sea Gull","Sea Serpent","Sea Venture","Seaflower","Sebella","Sibella",
"Semerest","Somerest","Seneca","Serpent","Servant","Seven Friends","Seven Sisters","Shallopp",
"Shamrock","Shannon","Shield","Success's Increase","Tobacco Plant","Ulysses","Unanimity","Unicorne",
"Two Friends","Tryphena","Truth & Delight","het Wapen van Noorwegen","het Wappen van Rensselaerswyck",
"Warren","Warrington","Warwick","Washington","Wasp","Water Witch","den Waterhondt","Waterloo",
"Weatherell","Welcome","Wellington","Weser","Westpoint","Weymouth","Whale","White Angel","White Oak",
"Wicker","Wilhelmine Charlotte"],
"navy":["Valona","Van Stephorst","Vanson","Venus","Vernon","Verny","Vestal","Victoire","Victoria",
"Victory","Vigilant","Vigorous","Vine","Vineyard","Virgin","Virginia","Virgins Venture","Virginus Grace",
"Virtuous Grace","Visitor","Volant","Voltaire","Volunteer","de Vos","Vrow Anna"]}
        
pirate_name_rules={"western_family_name":["Rackham","Boyah","al Hurra",
"Killigrew","Lindsey","Gathenhielm","Farlee",
"Crickett","Burn","Wall","Higgs","Skytte","Delahaye","Strangwish","Strangways",
"Lord","ibn Jabir al-Jalahimah","Levasseur","Hands","Roberts","Lucifer",
"Hayreddin","Barbarossa","Teach","Bonnet","Bonny","Boyah","de Graaf",
"de Grammont","Exquemelin","Kidd","Low","Dampier","Caesar","Cofresí","Lafitte",
"Morgan","Prince","l'Olonnais","Strangways","Gibbs","de Soto","Munthe",
"Gilbert","Alcantra","Bouchard","Lord","Gordon","Hicks","Boggs","Hayes",
"Aury","Maffitt","Baker","Barss","Jørgensen","Gambi","You","Youx","Lafitte",
"Hawkins","Easton","van Hoorn""Henriques","Hein","de Berry","Bellamy",
"Hornigold","Mason","Every","Braziliano","Marks","Marley","Hill","Silver",
"Pew","Bones","Flint"],
"eastern_family_name":["Shirahama","Lim","Chui","Gan","Liang","Wang","Zheng",
"Zheng","Cai","Cheung","Ching","Shap","Chui","Lai","Fuma"],
"pirate_titles":["Calico Jack","Calico","Caesar","Blackbeard","Reis",
"Barbarossa","Redbeard","Patch","Sealegs","Firebrand","Tarpit","Drowner",
"Baba","Black Caesar","Diabolito","Dieu-le-Veut","Corsair","Deepwater",
"Captain Blood","Bloody","Bones","Skull","Hammer","One-Eye","Mercy",
"Gunpowder","Jolly Roger","Irish","BlackJack","Diamond","Lucky","Honorable",
"Right Hon'ble","Jonah","Scar","Wrath","Gibbering","The Lost","Ahab","Raja",
"King","Duke","Squire","Halfhand","Back from the Dead","Red","No Quarter",
"Cutlass","Undefeated","Big Bear","Deadeye","Surefoot","Lackland","Long",
"Rags and Bones","Mizzenmast","Mizzenmast Hill's Daughter","Bart","Blind","Able",
"Verse","Chorus","Dancer","Lubber","Ballast","Weevil","Hardtack","Bilge",
"Baggywrinkle","Bowline","Scupper","Gallant","Kill-'em-All","Last Survivor",
"Fish-Eye","Sailfish","Cog","Crow","Gull","Raven","Jib","Fourth Rate","Slush",
"Topsail","Windlass","Keelhaul","Castaway","Shoeless","Pete Eye Shoeless",# Thanks, Shawn
"Q.", "Swashbuckler","Pirate McPirateface","McPirateface",# Thanks, Alex
"No-Ears","Sharkbait","Sea Wolf","Sandspit","El Gamo","Heart"],
"female_given_names":["Anne","Mary","Grace","Jeanne","Awilda","Sayyida",
"Christina","Christina Anna","Maria","Ingela","Flora","Rachel","Charlotte",
"Bess","Sao","Shih","Choi San","Elane","Elizabetha","Jacquotte","Mizzenmast",
],
"male_given_names":["Higgs","Lars","Olivier","Basilica","Bartholomew","Hendrick",
"Hayreddin","Oruç","Edward","Stede","Laurens","Abshir","Michel","Alexandre",
"William","Edward","William","Henri","Roberto","Jean","Henry","Lawrence",
"François","Henry","Charles","Benito","Pedro","Mansel","Hippolyte",
"Samuel Hall","Nathaniel","Albert W.","Eli","Bully","Rahmah", "Louis-Michel",
"John Newland","Joseph","Joseph","Jørgen","Vincenzo","Dominique","Pierre",
"John","Peter","Nicholas","Moses Cohen","Piet Pieterszoon","Samuel","Benjamin",
"Samuel","Henry","Roche","Ning","Daoming","Zhi","Hong","Zhilong","Jing","Qian",
"Po Tsai","Ng-tsai","Kotaro","Kenki"]}

melee_weapons_swords=["sword","cutlass","rapier","khopesh","sabre","estoc","claymore","flamberge","kaskara","dao","kris","kukri","sword","cutlass","rapier","khopesh","sabre","sword","cutlass","rapier","khopesh","sabre"]
        

def generatePirate():
    westeast = random.choice(["western_family_name","western_family_name","eastern_family_name"])
    gender = random.choice(["male","female"])
    name_gender = "{0}_given_names".format(gender)
    given_name = random.choice(pirate_name_rules[name_gender])
    family_name = random.choice(pirate_name_rules[westeast])
    pirate_title = random.choice(pirate_name_rules["pirate_titles"])
    pirate_title = random.choice(["{0}","{0}","{0}","{0}","{0}","{0} {2}", "{0} {2}","{0} {1}", "{2} {1}", "{2} {3}", "{3} {1}", "{0}-{3}"]).format(pirate_title, family_name, given_name, random.choice(pirate_name_rules["pirate_titles"]))
    namestring = random.choice(["{0} \"{1}\" {2}","{0} \"{1}\" {2}","{0} {2}","{0} \"{1}\" {2}","{0} {2}","{0}","{2}","{1}","\"{1}\"", "\"{1}\" {0}", "\"{1}\" {2}"])
    fullname = namestring.format(family_name, pirate_title, given_name)
    if westeast is "western_family_name":
        fullname = namestring.format(given_name, pirate_title, family_name)
    plain_namestring = namestring.replace("\"","").replace("{1}","").replace("  "," ").strip()
    plainname = plain_namestring.format(family_name, pirate_title, given_name)
    if westeast is "western_family_name":
        plainname = plain_namestring.format(given_name, pirate_title, family_name)
    if "" == plainname:
        plainname = fullname
    pirate = Character(fullname, gender)
    pirate._nickname = pirate_title
    pirate._given_name = given_name
    pirate._family_name = family_name
    pirate._plain_name = plainname
    pirate._name_style = westeast
    pirate.weapon_name = random.choice(melee_weapons_swords)
    pirate.weapon_tags = ["weapon_type_sword"]
    pirate._crew_title = "pirate"
    pirate.description = describePirate(pirate)
    return pirate    
    
def generatePirateShip():
    pick_ship_template = random.choice([s for s in ship_templates if ("pirate" in s["uses"])])
    pirate_ship_name = random.choice(ship_names["pirate"])
    pirate_ship = Ship(pirate_ship_name, pick_ship_template)
    pirate_captain = generatePirate()
    pirate_captain._crew_title = "captain"
    pirate_ship.addCrew(pirate_captain)
    pirate_crew_titles = ["first mate","quartermaster","second_mate","boatswain","cook","carpenter","sailmaker","steward"]
    for c_title in pirate_crew_titles:
        pirate = generatePirate()
        pirate._crew_title = c_title
        pirate_ship.addCrew(pirate)
    pirate_ship.addTag("ship")
    return pirate_ship
    
def generateTheSea():
    the_sea = Character("the sea", "neuter")
    the_sea.addTag("sea")
    return the_sea
    
    
def find_character(char, actor, target, exclude=None, repeat=0):
    """
    Find the specified character in the actor/target subgroupings.
    Used to, for example, return the captain of a ship if we
    know which ship but not which character is the captain.
    """
    if "CREWMEMBER" in char:
        if "ship" in actor.getTags():
            c = actor.getRandomCrewmember()
            if None != c and exclude != c:
                return c
            if repeat > 15:
                return c # Error out after too many loops. Should probably also throw out a warning.
            return find_character(char, actor, target, exclude, repeat + 1)
    if "THE BOATSWAIN" in char:
        if "ship" in actor.getTags():
            c = actor.getBoatswain()
            if None != c:
                return c
    if "THE CAPTAIN" in char:
        if "ship" in actor.getTags():
            c = actor.getCaptain()
            if None != c:
                return c
    return char
    
def find_character_name(char, actor, target, exclude=None, repeat=0):
    c = find_character(char, actor, target, exclude)
    if hasattr(c, "name"):
        if exclude == c.name and (repeat < 15):
            return find_character(char, actor, target, exclude,repeat+1)
        return c.name
    return c
    
def find_character_name_pos_adj(char, actor, target):
    c = find_character(char, actor, target)
    if hasattr(c, "her"):
        return c.her
    return c
    
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
"island_name_construction":["#isle.capitalize# of the #person_description.capitalizeAll# #common_animal.capitalize#","#mood.capitalize# #isle.capitalize#","The #crayola_color# Isle of #greek_titans.capitalize#","#isle.capitalize# of #greek_titans.capitalize#","#gemstone.capitalizeAll# #vegetable.capitalizeAll# #isle.capitalize#"]
}
    
    
character_clothes = [    
[["waistcoat","breeches","hat","sash","necklace","pistols","weapon"],"#prosub.capitalize# made a gallant figure being dressed in a rich crimson waistcoat and breeches and red feather in #posadj# hat, a gold chain around #posadj# neck, with a diamond cross hanging to it, #actor_weapon.a# in #posadj# hand, and two pair of pistols hanging at the end of a silk sling flung over #posadj# shoulders according to the fashion of the pirates."],
[["weapon","sash","pistols"],"And what a fine figure #prosub# was to be sure! What a deal of gold braid! What a fine, silver-hilted #actor_weapon#! What a gay velvet sling, hung with three silver-mounted pistols!"],
[["beard","build","hair_color"],"A great, heavy, burly fellow, was #prosub# with a beard as black as a hat--a devil with #posadj# sword and pistol afloat, but not so black as was painted when ashore."],
[["build"],"#prosub.capitalize# was a little, thin, wizened #actor_gender# with a very weathered look."],
[["waistcoat","breeches","shoes"],"#prosub.capitalize# was dressed in a rusty black suit and wore #xkcd_color# yarn stockings and shoes with brass buckles."],
[["breeches","waistcoat","shoes"],"#prosub.capitalize# was dressed in sailor fashion, with petticoat breeches of duck, a heavy pea-jacket, and thick boots, reaching to the knees."],
[["sash", "coat", "pistol"],"#prosub.capitalize# wore a red sash tied around #posadj# waist, and, as #prosub# pushed back #posadj# coat, you might glimpse the glitter of a pistol butt."],
[["hair_color","beard","build"],"#prosub.capitalize# was a powerful, thickset man, low-browed and bull-necked, #posadj# cheek, and chin, and throat closely covered with a stubble of blue-black beard."],
[["hat"],"#prosub.capitalize# wore a red kerchief tied around #posadj# head and over it a cocked hat, edged with tarnished gilt braid."],
[["coat","sash"],"#prosub.capitalize# was a splendid ruffian in a gold-laced coat of dark-blue satin with a crimson sash, a foot wide, about the waist."],
[["weapon"],"#prosub.capitalize# wore #posadj# #actor_weapon# openly, in #gemstone.a#-studded scabbared at #posadj# waist."],
[["weapon"],"Though #prosub# carried #actor_weapon.a#, #prosub# did not flaunt it as others did."],
[["hat"],"#prosub.capitalize# wore no hat, though #prosub# frequently wore #flower.a# in #posadj# hair."]

]
character_personality = [
[["backstory","personailty"],"#prosub.capitalize# had been known as #person_description.a# #occupation# before coming to sea, but who would recognize #proobj# now?"],
[["personality"],"#prosub.capitalize# was noted for being frequently #mood#."],
[["personality"],"#prosub.capitalize# had once kept a pet #common_animal#."]
]
    
def describePirate(char):
    """
    Return a flamboyant description of the pirate in question.
    """
    desc_table = {}
    desc_table["full_name"] = char.name
    desc_table["prosub"] = char.she
    desc_table["posadj"] = char.her
    desc_table["proobj"] = char.him
    desc_table["actor_weapon"] = char.weapon_name
    desc_table["actor_gender"] = "individual"
    if char.gender == "female":
        desc_table["actor_gender"] = "woman"
    if char.gender == "male":
        desc_table["actor_gender"] = "man"
    desc_table.update(corpora_rules)
    gram = tracery.Grammar(desc_table)
    gram.add_modifiers(base_english)
    description = ""
    excludetags = []
    if char.gender != "male":
        excludetags.append("beard")
    character_desc_table = []
    character_desc_table.extend(character_clothes)
    character_desc_table.extend(character_personality)
    loop_count = 0
    while loop_count < 3:
        valid_desc = [d for d in character_desc_table if len(set(d[0]).intersection(set(excludetags))) <= 0]
        if len(valid_desc) > 0:
            newdesc = random.choice(valid_desc)
            excludetags.extend(newdesc[0])
            description = (description + " " + str(newdesc[1])).strip()
        loop_count += 1
        
    description = re.sub("</\+>", "", description)
    description = re.sub("#prosub", "#full_name", description, count=1)
        
    
    description = gram.flatten(description)
    return description