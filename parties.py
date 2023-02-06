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









# actor_df = pd.read_csv('actor.basics.tsv',sep = '\t')
# #actor_df = actor_df[actor_df['deathYear'].notnull()]

# actor_df['deathYear'] = actor_df['deathYear'].apply(pd.to_numeric, errors='coerce').fillna(0.0)

# actor_df= actor_df[actor_df['deathYear']>= 2013]
# actor_df.to_csv('modified_actor.basics.tsv', sep="\t")

#actor_df = actor_df.drop(actor_df.columns[0,2,3,5], axis=1)


#actor_df= pd.read_csv('modified_actor.basics.tsv',sep = '\t')
#print(len(actor_df.index))

# actor_df= actor_df[actor_df['birthYear']>= 2010]
# actor_df.to_csv('modified_actor_2.basics.tsv', sep="\t")



# movie_df= pd.read_csv('modified_movie.basics.tsv',sep = '\t')

# movie_df['primaryTitle'] = movie_df['primaryTitle'].to_string()
# print(movie_df)
# movie_df = movie_df[movie_df["primaryTitle"].str.contains("Episode") == False]
# print(movie_df)

# movie_df.to_csv('final_movie.basics.tsv', sep="\t")

# movie_df['startYear'] = movie_df['startYear'].apply(pd.to_numeric, errors='coerce').fillna(0.0)

# movie_df= movie_df[movie_df['startYear']>= 2012]
# movie_df= movie_df[movie_df['startYear']<= 2015]

# movie_df.to_csv('modified_movie.basics.tsv', sep="\t")

#second movie cleaning

#movie_df= pd.read_csv('modified_movie.basics.tsv',sep = '\t')
# print(len(movie_df.index))

# movie_df= movie_df[movie_df['startYear']<= 2019]
# movie_df.to_csv('modified_movie_2.basics.tsv', sep="\t")

