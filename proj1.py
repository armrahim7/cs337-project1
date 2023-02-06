import re
import json
import nltk
nltk.download('vader_lexicon')
import spacy
nlp = spacy.load('en_core_web_lg')
from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
from load_data import load_data

def get_host(tweets):
    possible_candidates = []
    for txt in tweets:
        #clean tweet
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        #regex to get part of sentence before the words host/hosts/hosted
        win = re.search(r'(.*) host[s|ed]?', txt)
        #if there is a match, separate the part that becomes before the 'host' word
        if (win != None):
            str = win.group(1)
            #use spacy named-entity recognition
            doc = nlp(str)
            for i in doc.ents:
                if (i.label_ == 'PERSON'):
                    possible_candidates.append(i.text)
    possible_set = set(possible_candidates)
    final_candidates = []
    for c in possible_set:
        if((possible_candidates.count(c)/len(possible_candidates)) >= 0.1):
            final_candidates.append(c)
    return join_hosts(final_candidates)
def best_and_worst_dressed(tweets):
    #Look for tweets using these words
    fashion_words = ["outfit", "dress", "suit", "fit", "style", "clothes", "shirt", "pants", "dressed", "fashion"]
    best = []
    worst = []
    fashion_tweets = []
    for txt in tweets:
        #Clean up tweets
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        txt = re.sub(r'goldenglobes', '', txt)
        txt = re.sub(r'[G|g]olden [G|g]lobes', '', txt)
        #Filters tweets based on if tweet uses fashion words
        for f in fashion_words:
            if (f in txt):
                fashion_tweets.append(txt)
    #Some more cleaning up (remove retweets)
    fashion_tweets = [x for x in fashion_tweets if not (x.startswith('rt'))]
    #Check sentiments on fashion tweets
    for ftweet in fashion_tweets:
        sents = sia.polarity_scores(ftweet)
        if (sents['compound'] > 0):
            doc = nlp(ftweet)
            for i in doc.ents:
                #Filters only people strings out
                if (i.label_ == 'PERSON'):
                    best.append(i.text)
        elif (sents['compound'] < 0):
            doc = nlp(ftweet)
            for i in doc.ents:
                #Filters only people strings out
                if (i.label_ == 'PERSON'):
                    worst.append(i.text)
    #Returns the person with the most positive-leaning fashion-related tweets and person
    #with most negative-leaning fashion-related tweets
    return ['best dressed: ' + max(set(best), key = best.count), 'worst dressed: ' + max(set(worst), key = worst.count)]
def host_sentiment(hosts, tweets):
    compound_score = 0
    for txt in tweets:
        for h in hosts:
            if h in txt:
                sents = sia.polarity_scores(txt)
                compound_score += sents['compound']
    if (compound_score > 0):
        sentiment = 'Positive'
    elif (compound_score < 0):
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return 'Overall Host(s) Sentiment: ' + sentiment + "\n" + 'Overall Compound Score: ' + str(compound_score)
def join_hosts(hosts):
    output = []
    for i in hosts:
        curr = i
        for j in hosts:
            if curr in j and curr is not j:
                curr = "none"
        if curr != "none":
            output.append(curr)
    return output

data = load_data(2013)
print(best_and_worst_dressed(data))
hosts = get_host(data)
print(hosts)
print(host_sentiment(hosts,data))


