# -*- coding: utf-8 -*-

import sourcing
import textacy
import numpy


action_texts = [60, 1184, 2741, 53125, 2681, 259, 2759, 1257  ]
virgil_and_homer = [2199, 22382, 16452, 6150, 3059, 6130, 1727, 3160, 51355, 48895, 7959, 7524, 16927, 228, 18466, 22456, 29358 ]
arthurian = [12753, 831, 1251, 1252, 1949, 1972, 8601, 610, 12753, 10745, 22053, 25654, 45514, 7098, 13674, 22396, 36462, 15551, 82, 6582, 4926, 3011, 14244, 14305, 2414, 46923, 26646, 36540, 41108, 46176, 39591]
howard_pyle = [10148, 964, 1557, 10745, 2865, 26862, 33702, 47723, 47564]
cabell = [22463]
medieval_town_series = [38559,46552,44314,43764,46662,41391,37793,46618,46510,46401,46274,24519,46732,46533,24519,38009,46301,41209,46384]

pirates = [25982,21072,21073,21072,21813,21692,21062,24783,17563,10727,24914,10765,19589,11399,17863,21071,6422,12216,19564,21027,25088,19139,17168,13073,7346,7870,19273,10966,17415,24907,21104,21087,21086,24882,24439,26960,22903,21403,18469,22169,17741,24035,21580,19396,26612,16921,25472,10210,26514,973,10394,22033,22215,22752,1965,3294,421,20025,17188,17053,20774,33318,26958,28418]

pirate_corpus = sourcing.getTextCorpus(pirates)
pirate_actions = sourcing.getActionCorpus(pirate_corpus)
#pirate_verbs = sourcing.makeVerbDictionary(pirate_actions)

arthur_corpus = sourcing.getTextCorpus(arthurian)
arthur_actions = sourcing.getActionCorpus(arthur_corpus)

medieval_corpus = sourcing.getTextCorpus(medieval_town_series)
mediveal_actions = sourcing.getActionCorpus(medieval_corpus)

virgil_corpus = sourcing.getTextCorpus(virgil_and_homer)
virgil_actions = sourcing.getActionCorpus(virgil_corpus)


current_actions = pirate_actions

def getSentences(word):
    return sourcing.findNearbyVerbs(word, current_actions)

def sampleSentences(word):
    #sents = getSentences(word)
    prob = sourcing.findNearbyVerbs(word, current_actions)
    if len(prob) > 100:
        prob = prob[:100]
    probsum = sum([p[1] for p in prob])
    pl = [ (p[1] / probsum) for p in prob]
    #sl = zip(range(len(prob)), [p[0] for p in prob])
    #slo = [p[0] for p in sl]
    sp = [p[0] for p in prob]
    select = numpy.random.choice(sp, p=pl, replace=False)
    return select #prob[select][0]
    #return sourcing.findVerbCloseness(word, current_actions)
    
def nounChunks(corpus):
    chunks = set()
    for d in corpus:
        chunks = chunks.union(set([n.text for n in textacy.extract.noun_chunks(d)]))
    return chunks
    
def writeNouns(corpus):
    nouns = list(nounChunks(corpus))
    textacy.fileio.write_file_lines(nouns, "noun_list.txt", encoding="utf8")

def writeVerbs(actions):
    verbs = set()
    for a in actions:
        if a.primeverb:
            verbs = verbs.union(set([a.primeverb.lemma_]))
    textacy.fileio.write_file_lines(verbs, "verb_list.txt", encoding="utf8")

def writeSentences(actions):
    sents = [a.sentence.text for a in actions]
    textacy.fileio.write_file_lines(sents, "sent_list.txt", encoding="utf8")

    
#def replaceNouns(sent):
#    for tok in sent:
        # find nsubj and replace it (or its phrase) with #SUBJECT#
        # look for NNPS, categorize it as appropreate...