# -*- coding: utf-8 -*-

class Character:
    def __init__(self, char_name, char_gender="female"):
        self._id = char_name
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
        return "sword"
        
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
        
        
