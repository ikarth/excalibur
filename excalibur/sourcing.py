# -*- coding: utf-8 -*-

import settings
import nltk
import logging
import gutenberg.cleanup
import gutenberg.acquire
import re
import spacy
import textacy
import pycorpora

from enum import Enum

from gutenberg.query import get_etexts
from gutenberg.query import get_metadata

from gutenberg.acquire import get_metadata_cache

# Much of this might be better spun off into its own separate library, but
# I always favor implementing the specific uses first and wait to do the 
# architecture until you know what it actually needs to look like.


if not 'cache' in globals():
    cache = gutenberg.acquire.metadata.SleepycatMetadataCache('./data/gutenberg/metadata/cache.sqlite')
    gutenberg.acquire.set_metadata_cache(cache)

corpus_guten = nltk.corpus.reader.plaintext.PlaintextCorpusReader(settings.GUTENBERG_CORPUS, fileids = r'.*\.txt', encoding="utf-8")

def countWords(filename):
    return len(list(corpus_guten.words(filename)))

def unwrapText(unwrapped):
    unwrapped = unwrapped.replace("\r\n", "\n")
    unwrapped = unwrapped.replace("\r", "\n")
    unwrapped = re.sub(" *?\n\n", "#END_OF_PARAGRAPH#", unwrapped)
    unwrapped = re.sub("\n(?=[A-Za-z\"\'])"," #END_OF_LINE#", unwrapped)
    unwrapped = re.sub(" *#END_OF_LINE# *"," ", unwrapped)
    unwrapped = re.sub("\n\n\n*","\n\n", unwrapped)
    unwrapped = re.sub("#END_OF_PARAGRAPH# *", "\n", unwrapped)
    unwrapped = re.sub("\n (?=[A-Za-z\"\'])","\n", unwrapped)
    return unwrapped

def checkForBritishQuoteMarks(text):
    doublequotes = text.count("\"")
    singlequotes = text.count("'")
    if (doublequotes > singlequotes) or (doublequotes > 24):
        return False
    return True
    
def removeDialogue(text):
    """
    Remove paragraphs in the text that have direct quotations.
    """
    #double = checkForBritishQuoteMarks(text)
    #if double:
    text = re.sub("(?m)^.*[\"].*$", "", text) # Remove all paragraphs with double quotes...
    # TODO: Handle British single quotes
    return text

def filterAndCleanText(text):
    """
    Make some simple alterations to the text, to make it easier to parse
    """
    text = text.replace(". . .","…") ## ellipsis
    text = text.replace("Mlle.","Mlle·") # French abbreviations trip up the parser
    text = text.replace("Sir Andrew Ffoulkes, Bart.", "Sir Andrew Ffoulkes, Bart·")
    return text

def stripGutenberg(filenumber):
    # TODO: add a check to see if the stripped file already exists
    textfile = gutenberg.acquire.load_etext(filenumber)
    text = gutenberg.cleanup.strip_headers(textfile).strip()
    text = unwrapText(text)
    text = removeDialogue(text)
    text = filterAndCleanText(text)
    with open("./data/corpora/gutenberg/strip/{}.txt".format(filenumber), mode="w", encoding="utf_8", newline="\r\n") as outfile:
        outfile.write(text)
    #print(corpus_guten.sents("strip/{}.txt".format(filenumber)))
    return str("strip/{}.txt".format(filenumber))

def getGutenberg(filenumber):
    stripGutenberg(filenumber) # make sure the data is on disk
    return open("./data/corpora/gutenberg/strip/{}.txt".format(filenumber), mode="r", encoding="utf_8").read()

def getGutenbergFilename(filenumber):
    stripGutenberg(filenumber) # make sure the data is on disk
    return "./data/corpora/gutenberg/strip/{}.txt".format(filenumber)

##############

#logger.info("Get metadata...")

#print(get_metadata('title', 2701))
#print(get_metadata('author', 2701))
#print(get_metadata('rights', 2701))
#print(get_metadata('subject', 2701))
#print(get_metadata('language', 2701))
#print(get_etexts('subject', "Sea stories"))

#val = get_metadata('language', 2701)

##############

#en_nlp = spacy.load('en')
#doc = en_nlp(getGutenberg(60))

from spacy.symbols import nsubj, VERB

def makeVerbList(doc):
    verbs = set()
    verblist = {}
    for possible_subject in doc:
        if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
            verbs.add(possible_subject.head)
            prevsen = verblist.get(possible_subject.head.text, [])
            spen = doc[possible_subject.head.left_edge.i : possible_subject.head.right_edge.i + 1]
            prevsen.extend([spen])
            verblist.update({str(possible_subject.head): prevsen})
    return verblist
    
def makeSenList(doc):
    verblist = {}
    for sen in doc.sents:
        prev = verblist.get(sen.root.text, [])
        parse = [sen]
        parse.extend(prev)
        verblist.update({sen.root.text : parse})
    return verblist
    
    
def getGutenbergMetadata(textno):
    meta = {
        'title': list(get_metadata('title', textno))[0],
        'author': get_metadata('author', textno),
        'rights': get_metadata('rights', textno),
        'subject': get_metadata('subject', textno),
        'language': list(get_metadata('language', textno))[0],
        'guten_no': textno}
    return meta

def acquireGutenbergText(textno):
    meta = getGutenbergMetadata(textno)
    return [getGutenberg(textno), meta]
    

#virgil_books = [22456, 228, 29358, 18466]
#vtext = acquireGutenbergText(228)
#vtext = acquireGutenbergText(18466)

#tt = acquireGutenbergText(60)
#d = textacy.Doc(tt[0], tt[1], tt[1]['language'])

#vdoc = textacy.Doc(vtext[0], vtext[1], vtext[1]['language'])

def buildSentData(doc):
    for s in doc.sents:
        sentmeta = {"sent": s, "doc_number": doc.metadata["guten_no"]}
        sentmeta.update({"mainverbs": textacy.spacy_utils.get_main_verbs_of_sent(s)})
        sentmeta.update({"svo": list(textacy.extract.subject_verb_object_triples(s))})
        print(sentmeta)
        
#bsd = buildSentData(d)

#svolist = textacy.extract.subject_verb_object_triples(d)

#list(svolist[1249][1].root.subtree)

def buildVerbData(docu):
    svolist = textacy.extract.subject_verb_object_triples(docu)
    svodata = []
    for svo in svolist:
        svo_entry = {"verb": svo[1].text}
        svo_entry.update({"svo": svo})        
        svo_entry.update({"subtree": list(svo[1].root.subtree)})
        svodata.append(svo_entry)
    return svodata 
        
#bvd = buildVerbData(d)
#
#bvd[726]
#
#testbvd = bvd[725]
#testbvd["subtree"]

class TokenAnnotation(Enum):
    none = 0
    verb = 1
    subject = 2
    object = 3
    

class SourceAction(object):
    def __init__(self, sentence_data, doc_number=0):
        self.sentence = sentence_data
        self.gutenberg_number = doc_number
        self.action = sentence_data
        self._annotation = None
                
    @property
    def root_verb(self):
        for possible_subject in self.sentence:
            if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
                return possible_subject.head
    
    @property
    def noun_subject_phrases(self):
        noun_phrases = []
        for possible_subject in self.sentence:
            if possible_subject.dep == nsubj:
                noun_phrases.append(possible_subject.subtree)
        return noun_phrases
    
    @property
    def main_verbs(self):
        return textacy.spacy_utils.get_main_verbs_of_sent(self.sentence)
        
    @property
    def svo_list(self):
        return textacy.extract.subject_verb_object_triples(self.sentence)
    
    @property
    def object_list(self):
        ol = []
        for svo in self.svo_list:
            ol.extend([svo[2]])
        return ol
    
    def replaceSubject(self, new_subject="#SUBJECT#"):
        newsen = []
        noun_subj = self.noun_subject_phrases
        if not noun_subj:
            return self.sentence
        for tok in self.sentence:
            if tok in noun_subj[0]:
                newsen.append(new_subject)
            else:
                newsen.append(tok)
        return newsen
    
    @property    
    def annotation(self):
        if self._annotation:
            return self._annotation
        noun_subj = self.noun_subject_phrases
        anno = []
        for tok in self.sentence:
            tok_index = tok.i - self.sentence.start
            anno.append(TokenAnnotation.none)
            if noun_subj:
                if tok in noun_subj[0]:
                    anno[tok_index] = TokenAnnotation.subject
            if tok in self.main_verbs:
                anno[tok_index] = TokenAnnotation.verb
            #print(self.object_list)
            #if tok in self.object_list:
            #    anno[tok_index] = TokenAnnotation.object
        self._annotation = anno                
        return anno
        
def filterSentence(sent):
    """
    Return false if the sentence contains a word on the bad-word-filter list.
    """
    return True # TODO: implement

    
def buildSourceActionsFromDoc(docu):
    action_list = []
    for s in docu.sents:
        if filterSentence:
            action_list.append(SourceAction(s, docu.metadata["guten_no"]))
    return action_list
        
#action_list = buildSourceActionsFromDoc(vdoc)
#
#act1 = action_list[58]
#act1.sentence
#act1.root_verb
#list(act1.noun_subject_phrases[0])
#
#act2 = action_list[569]
#act2.sentence
#act2.root_verb
#list(act2.noun_subject_phrases[0])
#
#for a in action_list:
#    print(a.annotation)

   
#    
#    
##rs = replaceSubject(act1)
##list(rs[0])
#
#act1.main_verbs
#
#list(rs.subtree)
#
#[t.text for t in act1.sentence]
#test = act1.sentence
#
#newsen = []
#for tok in test:
#    if tok in act1.noun_subject_phrases[0]:
#        print(tok.text)
#        newsen.append("#SUBJECT#")
#    else:
#        newsen.append(tok)
#newsen    
#
#for tok in test:
#    if tok in act1.noun_subject_phrases[0]:
#        tok.annotate = "SUBJECT"
#        

def getTextCorpus(acttext):
    actdocs = []
    actmeta = []
    for i in acttext:
        am = getGutenbergMetadata(i)
        ad = textacy.Doc(getGutenberg(i), am, "en")
        actdocs.append(ad)        
        actmeta.append(am)
    return textacy.corpus.Corpus('en', docs=actdocs, metadatas=actmeta)
    
def getActionCorpus(textcorpus):
    action_list = []
    for d in textcorpus:
        action_list.extend(buildSourceActionsFromDoc(d))
    return action_list
    
def makeVerbDictionary(actions):
    """
    Given an action list, return a dictionary of the lemma-ized verbs
    and their associated actions
    """
    verb_dict = {}
    for a in actions:
        lem = a.sentence.root.lemma_
        if a.main_verbs:
            if 1 == len(a.main_verbs) > 1:
                lem = a.main_verbs[0].lemma_
        else:
            if a.sentence.root.pos == VERB:
                lem = a.sentence.root.lemma_
            else:
                lem = None
        preva = verb_dict.get(lem, [])            
        preva.extend([a.sentence.text])
        verb_dict.update({lem: preva})
    return verb_dict
    
