# -*- coding: utf-8 -*-

import re
from wordfilter.wordfilter import Wordfilter

def removeNone(none_list):
    return [i for i in none_list if i != None]

    
badwordfilter = Wordfilter()

def filterBadWords(text):
    """
    Return text, redacting the slurs and other words we don't want...
    """
    if not isinstance(text, str):
        if hasattr(text, "__iter__"):
            return removeNone([filterBadWords(nw) for nw in text])
    for nw in badwordfilter.blacklist:
        if nw == text:
            text = ""
        else:
            matching = "[ \"\^\s]?({0})[ \s,.\":;\$]?".format(nw) # isolated
            matching = "({0})".format(nw)
            text = re.sub(matching, "REDACTED", text)
        if "" == text:
            text = None
    #text.replace()
    return text # TODO

naughty_words_list = ["shit","crap"]

def filterNaughtyWords(text):
    if not isinstance(text, str):
        if hasattr(text, "__iter__"):
            return removeNone([filterNaughtyWords(nw) for nw in text])
    text = filterBadWords(text)
    for nw in naughty_words_list:
        if nw == text:
            text = ""
        else:
            matching = "[ \"\^\s]?({0})[ \s,.\":;\$]?".format(nw)
            text = re.sub(matching, "", text)
    if "" == text:
        text = None
    return text
    
    
    