# -*- coding: utf-8 -*-

import tracery
import random

class Character:
    def __init__(self, char_name, char_gender="female"):
        self._id = char_name.upper().replace(" ", "_")
        self._full_name = char_name
        self._nickname = ""
        self._given_name = char_name
        self._family_name = ""
        self._name_style = "western_family_name"
        self._gender = char_gender
        self._crew_title = ""
        self._ship_id = ""
    
    @property
    def id(self):
        return str.upper(self._id).replace(" ", "_")
        
    @property
    def ship_id(self):
        return self._ship_id
    
    @ship_id.setter
    def ship_id(self, value):
        self._ship_id = value
        
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
        
    def Display(self):
        print("{0}, {1}, who carries a {2}".format(self._full_name, self._crew_title, self._weapon_name))
        

        
    # Pronoun Object
    @property
    def him(self):
        if self.gender is "female" or self.gender is "ship":
            return "her"
        if self.gender is "first_plural":
            return "us"
        if self.gender is "third_plural":
            return "them"
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
        if self.gender is "first":
            return "myself"
        return "himself"
        
class Crew(Character):
    def __init__(self, crew_id):
        self._crew_id = crew_id
        self._gender = "third_plural"
        self._gang = []
        
    def addCrew(self, crew_member):
        self._gang.append(crew_member)
        
    def Display(self):
        for c in self._gang:
            c.Display()
    
class Ship(Character):
    def __init__(self, ship_name, ship_characteristics):
        self._ship_id = ship_name.upper().replace(" ", "_")
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
    westeast = random.choice(["western_family_name","eastern_family_name"])
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
    
    pirate = Character(fullname, gender)
    pirate._nickname = pirate_title
    pirate._given_name = given_name
    pirate._family_name = family_name
    pirate._name_style = westeast
    pirate.weapon_name = random.choice(melee_weapons_swords)
    pirate.weapon_tags = ["weapon_type_sword"]
    pirate._crew_title = "pirate"
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
    return pirate_ship
    