import pandas as pd
import re
import json
import spacy
from spacy import displacy
import nltk
#nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()



z = open('gg2013.json')
tweets = json.load(z)
NER = spacy.load("en_core_web_sm")

x=0
parties={}


def find_parties(twt):
    party_re= re.search(r'(.*)(party|parties)(.*)',twt.lower())
    if party_re != None: 
        ppl=NER(twt)
        pos_rating=sia.polarity_scores(twt)['compound']
        for i in ppl.ents:
            if i.label_ == 'PERSON' or i.label_ == 'ORG':
                if 'Globes' not in i.text :
                    if i.text not in parties:
                        parties[i.text]=[1,pos_rating]
                    else:
                        parties[i.text][0]+= 1
                        parties[i.text][1] = (parties[i.text][1] +pos_rating)/parties[i.text][0]

for tweet in tweets:
    find_parties(tweet['text'])     

def best_party():
    best=max(parties, key=parties.get)

    if parties[best][1]> 0:
        sentiment= 'loved it!'
    else:
        sentiment= 'hated it!'

    print((f'Most Talked About party was thrown by {best} and people {sentiment}'))

best_party()







