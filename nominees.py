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
def get_nominees(awards, tweets):
    award_cands = dict()
    award_names = []
    for a in awards:
        award_names.append(a.split())
        award_cands['best ' + ' '.join(a.split())] = []
    retweet_combinations = [' rt ', 'rt ', ' rt']
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        txt = re.sub(r'goldenglobes', '', txt)
        txt = re.sub(r'golden', '', txt)
        txt = re.sub(r'globe', '', txt)
        txt = re.sub(r'[G|g]olden [G|g]lobes', '', txt)
        if (txt.startswith('rt')):
            continue
        for a in award_names:
            if (all([x in txt for x in a])):
                    doc = nlp(txt)
                    for i in doc.ents:
                        if(i.text.startswith('http') or any([x in i.text for x in retweet_combinations])):
                            continue
                        if (i.label_ == 'PERSON'):
                            award_cands['best ' + ' '.join(a)].append(i.text)
    final_award_cands = dict()
    for award in award_cands:
        final_award_cands[award] = max(set(award_cands[award]), key = award_cands[award].count)
    return final_award_cands
data = load_data()
awards = get_awards(data)
print(get_nominees(awards, data))
