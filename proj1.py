import re
import json
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')

def load_data():
    data = open('gg2013.json')
    tweets = json.load(data)
    return tweets

#ignore, still broken
def get_winners(tweets):
    banned_words = ['golden', 'globes', 'rt', 'goldenglobes']
    res = []
    dict = {}
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        win = re.search(r'(.*) (wins|won) best (.*)', txt)
        if (win != None):
            str = win.group(1)
            split_str = str.split()
            str2 = win.group(3)
            split_str2 = str2.split()
            prev = split_str2[0]
            if prev not in banned_words:
                res.append(prev)
            for i in range(1, len(split_str2)):
                if((prev not in banned_words) and (split_str2[i] not in banned_words)):
                    res.append(prev + ' ' + split_str2[i])
                    prev = prev + ' ' + split_str2[i]
    win_set = set(res)
    return sorted(win_set, key = res.count)

def get_host(tweets):
    possible_candidates = []
    for tweet in tweets:
        #clean tweet
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        #regex to get part of sentence before the words host/hosts/hosted
        win = re.search(r'(.*) host[s|ed]?', txt)
        #if there is a match, separate the part that becomes before the 'host' word
        if (win != None):
            str = win.group(1)
            #skip rt phrases
            if("rt" in str):
                continue
            #use spacy named-entity recognition
            doc = nlp(str)
            for i in doc.ents:
                if (i.label_ == 'PERSON'):
                    possible_candidates.append(i.text)
    possible_set = set(possible_candidates)
    final_candidates = []
    for c in possible_set:
        if((possible_candidates.count(c)/len(possible_candidates)) >= 0.15):
            final_candidates.append(c)
    return final_candidates
data = load_data()
print(get_host(data))


