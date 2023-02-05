import re
import json
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')
from awards import get_awards

def load_data():
    data = open('gg2013.json')
    tweets = json.load(data)
    return tweets

def list_of_presenters(tweets):
    cands = []
    useless_words = [' rt ', 'rt ', ' rt']
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        txt = re.sub(r'goldenglobes', '', txt)
        txt = re.sub(r'golden', '', txt)
        txt = re.sub(r'globe', '', txt)
        txt = re.sub(r'[Gg]olden [Gg]lobes', '', txt)
        pre = re.search(r'(.*)\spresent(s|ed|er|ers|ing)?', txt)
        if(pre):
            phrase = pre.group(1)
            doc = nlp(phrase)
            for i in doc.ents:
                if (any([x in i.text for x in useless_words])):
                    continue
                if (i.label_ == 'PERSON'):
                    cands.append(i.text)
    print(set(cands))
    return set(cands)
def get_presenters(awards, presenters, tweets):
    cands = dict()
    award_names = []
    for award in awards:
        award_names.append(award.split())
        cands['best ' + ' '.join(award.split())] = []
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        for award in award_names:
            if(all([x in txt for x in award])):
                doc = nlp(txt)
                for i in doc.ents:
                    if (i.label_ == 'PERSON') and (i.text in presenters):
                        cands['best ' + ' '.join(award)].append(i.text)
    final_award_cands = dict()
    for award in cands:
        award_set = set(cands[award])
        if (len(award_set) > 0):
            final_award_cands[award] = award_set
        else:
            final_award_cands[award] = []
    return final_award_cands


data = load_data()
awards = get_awards(data)
presenters = list_of_presenters(data)
print(get_presenters(awards,presenters,data))

    