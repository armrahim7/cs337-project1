import re
import requests
from bs4 import BeautifulSoup as BS
import json
import spacy
from spacy import displacy
import pandas as pd




#name
# actor_df = pd.read_csv('actor.basics.tsv',sep = '\t')
# actor_df = actor_df.drop(actor_df.colums[0,2,3,5], axis=1)

# movie_df= pd.read_csv('movie.basics.tsv',sep = '\t')
# movie_df = movie_df.drop(movie_df.colums[0,1,3,4,7], axis=1)

Genres=['Hey','Cany','You','Stop']
Movie_Descriptors=[]
Roles=[]

def create_award_re():
    #change these lits to a a set after populating them
    prev = ''
    gen= ''
    #for key in move_relation:
    for word in Genres:
        if gen != '':
            #if key == 'Genre':
            gen =  prev+f'|{word}'
            prev= gen
        else:
            gen =  prev+f'{word}'
            prev= gen
    
    print(f'({gen})')


#create_award_re()

def merge_award(pot_award):
    for awrd in awards:
        if len(awrd) > len(pot_award):
            if pot_award in awrd:
                awards[awrd][1]+=1   
                return     
        else:
            if awrd in pot_award:
                awards[awrd]= pot_award
                return
     
    awards[pot_award]= [None,0]
                
        
            





NER = spacy.load("en_core_web_sm")

test= ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

random= ['Sound','Writing (Original ScreenPlay','Makeup and Hairstyling']
# for str in random:
#    alpha= NER(str)
#    for ent in alpha:
#        for ent1 in alpha.ents:
#         print(ent.text,ent.pos_,ent1.label_)



#print(type_checker(test,['person']))



# API key = a97a455f

z = open('gg2013.json')
tweets = json.load(z)





x=0
awards={}
def find_awards():
    for tweet in tweets:
        twt1= re.split('[!.?]',tweet['text'])
        twt=twt1[0]
        win_re =re.search(r'(.*) (wins|won) (.*)', twt.lower())
        nominee_re= re.search(r'(.*) (nominee|nominated) (.*)', twt.lower())
        award_re = re.findall(r'Best (Performance By An )?(Actor|Actress|Motion Picture|Song|Film|Director|Producer|Screenplay|Score|Movie) (In A)?(Motion Picture|Television|Series|T.V.|Series)?(Drama|Musical or Comedy)?', twt.title())
        eval= [win_re,nominee_re]
        #filtering for a tweet that meets one of the regular expression
        if award_re != []:
            names=[]
            #award_re[0][1]
            text= NER(twt.title())
            for awrd in award_re:
                awrd = "Best "+" ".join(awrd)
                if awrd in awards:
                    awards[awrd][1] += 1
                else:
                    awards[awrd] = [None,0]
    #finding any mention of people within the texts matching reg_ex
                for str in text.ents:
                    #modify to get part of speech tagging
                    if str.label_ == 'PERSON' :
                        #type checker here, based on the current award in place
                        names.append(str.text)

                        if awards[awrd][0] == None:
                            #
                            awards[awrd][0] = set(names)
                        else:
                            awards[awrd][0].update(names)
  
    #finding any mention of people within the texts matching reg_ex
        if any(eval):
            pass
        # text= NER(twt)

        # for str in text.ents:
        #     if str.label_ == 'PERSON' :
        #         if str.text not in 
        #         names.append(str.text)
        
        # if awards[awrd][0] == None:
        #     awards[awrd][0] = names
        # else:



#find_awards():     
awards = {k:v for k,v in awards.items() if v[1]>10}
print(awards)

#movie = GetMovie(api_key='your api key')

#flags=re.IGNORECASE
