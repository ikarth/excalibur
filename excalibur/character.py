# -*- coding: utf-8 -*-

import tracery
import random

class Character:
    def __init__(self, char_name, char_gender="female"):
        self._id = char_name
        self._full_name = char_name
        self._nickname = ""
        self._given_name = char_name
        self._family_name = ""
        self._name_style = "western_family_name"
        self._gender = char_gender
    
    @property
    def id(self):
        return str.upper(self._id).replace(" ", "_")
        
    @property
    def name(self):
        return self._id
    
    @name.setter
    def name(self, value):
        self._id = value
        
    @property
    def gender(self):
        return self._gender
    
    @gender.setter
    def gender(self, value):
        self._gender = value
    
    # Kennings = alternate ways to refer to the character
    @property
    def kennings(self):
        return self._kennings
    
    @kennings.setter
    def kennings(self, value):
        self._kennings = value
        
        
    @property
    def possessive(self):
        return str(self._id) + "'s"
        
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
        

        
    # Pronoun Object
    @property
    def him(self):
        if self.gender is "female":
            return "her"
        if self.gender is "first_plural":
            return "us"
        if self.gender is "first":
            return "me"
        return "him"
    
    # Possessive Pronoun
    @property
    def his(self):
        if self.gender is "female":
            return "hers"
        if self.gender is "first_plural":
            return "ours"
        if self.gender is "first":
            return "mine"
        return "his"
    
    # Pronoun Subject
    @property
    def she(self):
        if self.gender is "female":
            return "she"
        if self.gender is "first_plural":
            return "we"
        if self.gender is "first":
            return "I"
        return "he"
    
    # Possessive Adjective
    @property
    def her(self):
        if self.gender is "female":
            return "her"
        if self.gender is "first_plural":
            return "our"
        if self.gender is "first":
            return "my"
        return "his"
    
    # Reflexive Pronouns
    @property
    def herself(self):
        if self.gender is "female":
            return "herself"
        if self.gender is "first_plural":
            return "ourselves"
        if self.gender is "first":
            return "myself"
        return "himself"
        
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
"Hornigold","Mason","Every","Braziliano","Marks","Marley","Hill","Silver"],
"eastern_family_name":["Shirahama","Lim","Chui","Gan","Liang","Wang","Zheng",
"Zheng","Cai","Cheung","Ching","Shap","Chui","Lai","Fuma"],
"pirate_titles":["Calico Jack","Calico","Caesar","Blackbeard","Reis",
"Barbarossa","Redbeard","Patch","Sealegs","Firebrand","Tarpit","Drowner",
"Baba","Black Caesar","Diabolito","Dieu-le-Veut","Corsair","Deepwater",
"Captain Blood","Bloody","Bones","Skull","Hammer","One-Eye","Mercy",
"Gunpowder","Jolly Roger","Irish","BlackJack","Diamonds","Lucky","Honorable",
"Right Hon'ble","Jonah","Scar","Wrath","Gibbering","The Lost","Ahab","Raja",
"King","Duke","Squire","Halfhand","Back from the Dead","Red","No Quarter",
"Cutlass","Undefeated","Big Bear","Deadeye","Surefoot","Lackland","Long",
"Rags and Bones","Mizzenmast","Mizzenmast Hill's Daughter","Bart","Blind","Able"],
"female_given_names":["Anne","Mary","Grace","Jeanne","Awilda","Sayyida",
"Christina","Christina Anna","Maria","Ingela","Flora","Rachel","Charlotte",
"Bess","Sao","Shih","Choi San","Elane","Elizabetha","Jacquotte","Mizzenmast",
"Verse","Chorus","Dancer","Lubber","Ballast","Weevil","Hardtack","Bilge",
"Baggywrinkle","Bowline","Scupper","Gallant","Kill-'em-All","Last Survivor",
"Fish-Eye","Sailfish","Cog","Crow","Gull","Raven","Jib","Fourth Rate","Slush",
"Topsail","Windlass","Keelhaul","Castaway"
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
    pirate_title = random.choice(pirate_name_rules["pirate_titles"])
    westeast = random.choice(["western_family_name","eastern_family_name"])
    gender = random.choice(["male","female"])
    name_gender = "{0}_given_names".format(gender)
    given_name = random.choice(pirate_name_rules[name_gender])
    family_name = random.choice(pirate_name_rules[westeast])
    namestring = random.choice(["{0} \"{1}\" {2}","{0} \"{1}\" {2}","{0} {2}","{0} \"{1}\" {2}","{0} {2}","{0}","{2}","{1}","\"{1}\"", "\"{1}\" {0}", "\"{1}\" {2}"])
    fullname = namestring.format(family_name, pirate_title, given_name)
    if westeast is "western_family_name":
        fullname = namestring.format(given_name, pirate_title, family_name)
    
    pirate = Character(fullname, gender)
    pirate._nickname = pirate_title
    pirate._given_name = given_name
    pirate._family_name = family_name
    pirate._name_style = westeast
    pirate.weapon_name = random.choice(melee_weapons_swords)
    pirate.weapon_tags = ["weapon_type_sword"]
    return pirate    