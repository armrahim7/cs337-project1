import re
import json
import spacy
nlp = spacy.load('en_core_web_lg')
from awards import get_awards

def load_data(year):
    name = f'gg{year}.json'
    data = open(name)
    tweets_data = json.load(data)
    tweets = []
    for tweet in tweets_data:
        tweets.append(tweet['text'])
    return tweets

def get_presenters(awards, tweets):
    cands = dict()
    award_names = []
    useless_words = [' rt ', 'rt ', ' rt']
    for award in awards:
        award_names.append(award.split())
        cands[' '.join(award.split())] = []
    for txt in tweets:
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        for award in award_names:
            if(all([x in txt for x in award])):
                pre = re.search(r'(.*)\spresent(s|ed|er|ers|ing)?', txt)
                if(pre):
                    phrase = pre.group(1)
                    doc = nlp(phrase)
                    for i in doc.ents:
                        if (any([x in i.text for x in useless_words])):
                            continue
                        if (i.label_ == 'PERSON'):
                            cands[' '.join(award)].append(i.text)
    final_award_cands = dict()
    for award in cands:
        final_award_cands[award] = []
        award_set = set(cands[award])
        for a in award_set:
            final_award_cands[award].append(a)
    return final_award_cands

data = load_data(2013)
awards = get_awards(data)
print(get_presenters(awards,data))

    