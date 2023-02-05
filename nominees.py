import re
import json
import nltk
import spacy
import imdb
nlp = spacy.load('en_core_web_lg')
nltk.download('stopwords')
from awards import get_awards
ia = imdb.IMDb()
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

def load_data(year):
    name = f'gg{year}.json'
    data = open(name)
    tweets = json.load(data)
    return tweets
def list_of_nominees(tweets):
    nom_words = ["nominated", "nominee", "contention", "nominate", "nomination"]
    cands = []
    useless_words = [' rt ', 'rt ', ' rt', 'goldenglobes', 'golden', 'globes']
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        txt = re.sub(r'goldenglobes', '', txt)
        txt = re.sub(r'golden', '', txt)
        txt = re.sub(r'globe', '', txt)
        txt = re.sub(r'[G|g]olden [G|g]lobes', '', txt)
        if (any([x in txt for x in nom_words])):
            doc = nlp(txt)
            for i in doc.ents:
                if(any([x in i.text for x in useless_words])) or ('http' in i.text):
                    continue
                if (i.label_ == 'PERSON'):
                    cands.append(i.text)
    return set(cands)

def get_nominees(awards, nominees, tweets):
    award_cands = dict()
    award_names = []
    people_words = ['actor', 'actress', 'director','score', 'screenplay']
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
                if(any([x in ' '.join(a) for x in people_words])):
                    doc = nlp(txt)
                    for i in doc.ents:
                        if (i.label_ == 'PERSON') and (i.text in nominees):
                            award_cands['best ' + ' '.join(a)].append(i.text)
                else:
                    award_cands['best ' + ' '.join(a)].append('movie')
                    
                        
    final_award_cands = dict()
    for award in award_cands:
        final_award_cands[award] = []
        award_set = set(award_cands[award])
        for a in award_set:
            if award_cands[award].count(a) > 1:
                final_award_cands[award].append(a)
    return final_award_cands

def check_if_movie(word):
    word = word.split()
    phrase = [x for x in word if not x in stop_words]
    #print(phrase)
    if (len(phrase) > 0):
        res = ia.search_movie(' '.join(phrase))
        for r in res:
            title = r['title']
            title = title.lower()
            title = re.sub(r'[^\w\s]', '', title)
            if (all(x in title for x in phrase)):
                return True
    return False

data = load_data(2013)
awards = get_awards(data)
nominees = list_of_nominees(data)
print(get_nominees(awards, nominees, data))

