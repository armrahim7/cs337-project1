import re
import json
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')

def load_data():
    data = open('gg2013.json')
    tweets = json.load(data)
    return tweets

def get_awards(tweets):
    award_words = ['movie', 'motion', 'picture', 'series', 'television', 'tv', 'film', 'score', 'song']
    award_cands = []
    useless_words = [' rt ', 'rt ', ' rt', 'goldenglobes', 'golden', 'globes']
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'/', ' ', txt)
        txt = re.sub(r'[^\w\s]', '', txt)
        reg = re.search(r'best (.*)', txt)
        if(reg):
            str = reg.group(1)
            award = re.search(r'(.*) goes', str)
            if(award):
                cand = award.group(1)
                if(any([x in cand for x in useless_words])):
                    continue
                if(any([x in cand for x in award_words])):
                    award_cands.append(cand)
    award_set = (set(award_cands))
    final_award_cands = []
    for a in award_set:
        if award_cands.count(a) > 4:
            # final_award_cands.append('best ' + a)
            final_award_cands.append(a)
    return final_award_cands


# data = load_data()
# awards = get_awards(data)
# print(awards)