import re
import json
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')

def load_data():
    data = open('gg2013.json')
    tweets = json.load(data)
    return tweets
def get_nominees(tweets):
    candidates = dict()
    people_words = ['actor', 'actress']
    awards = [['supporting'],['motion', 'drama'], ['motion', 'musical', 'comedy']]
    award_cands = dict()
    for p in people_words:
        for a in awards:
            award_cands[p + ' ' + ' '.join(a)] = []
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
        for a in awards:
            if (all([x in txt for x in a])):
                for p in people_words:
                    if p in txt:
                        doc = nlp(txt)
                        for i in doc.ents:
                            if (i.label_ == 'PERSON'):
                                award_cands[p + ' ' + ' '.join(a)].append(i.text)
    final_award_cands = dict()
    for award in award_cands:
        merge_set(award_cands[award])
        award_set = set(award_cands[award])
        sort_set = sorted(award_set, key = award_cands[award].count, reverse=True)
        final_award_cands[award] = sort_set[:7]
    return final_award_cands
def merge_set(candidates):
    top_candidate = max(set(candidates), key = candidates.count)
    for cand in candidates:
        if (any([x in cand for x in top_candidate])):
            candidates[candidates.index(cand)] = top_candidate

data = load_data()
print(get_nominees(data))
