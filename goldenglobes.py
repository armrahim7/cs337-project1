import re
import requests
from bs4 import BeautifulSoup as BS
import json
import nltk
import spacy
from spacy import displacy
import pandas as pd
nlp = spacy.load('en_core_web_lg')
NER = spacy.load("en_core_web_sm")

f = open('gg2013.json')
tweet_data = json.load(f)

nominees_per_award = 5
award_count = 26

data = []

for i in tweet_data:
    data.append(i["text"].lower())

# old experimentation, please ignore
#awards = [
#    {
#    "award": "Best Drama",
#    "award-re": "[Bb]est [Dd]rama",
#    "nominees": ["Django Unchained", "Life of Pi", "Zero Dark Thirty", "Lincoln", "Argo"],
#    "nominees-re": ["[Dd]jango Unchained", "[Ll]ife of Pi", 
#    "[Zz]ero Dark Thirty", "[Ll]incoln", "[Aa]rgo"],
#    "winner": ""
#    },
#    {
#    "award": "Best Music",
#    "award-re": "[Bb]est [Mm]usic",
#    "nominees": ["Les Miserables", "The Best Exotic Marigold Hotel", "Moonrise Kingdom", 
#    "Salmon Fishing in the Yemen", "Silver Linings Playbook"],
#    "nominees-re": ["[Ll]es [Mm]iserables", "[Tt]he [Bb]est [Ee]xotic [Mm]arigold [Hh]otel", 
#    "[Mm]oonrise [Kk]ingdom", "[Ss]almon [Ff]ishing [Ii]n [Tt]he [Yy]emen", 
#    "[Ss]ilver [Ll]inings [Pp]laybook"],
#    "winner": ""
#    },
#    {
#    "award": "Best Actress - Drama",
#    "award-re": "[Bb]est [Aa]ctress - [Dd]rama",
#    "nominees": ["Jessica Chastain", "Marion Cotillard", "Helen Mirren", "Naomi Watts",
#    "Rachel Weisz"],
#    "nominees-re": ["[Jj]essica [Cc]hastain", "[Mm]arion [Cc]otillard", "[Hh]elen [Mm]irren",
#    "[Nn]aomi Watts", "[Rr]achel Weisz"],
#    "winner": ""
#    }
#]


# finds winners given nominees, works, not important
#for a in awards:
#    current = 0
#    most = 0
#    guess = ""
#    ind = -1
#    for b in a["nominees-re"]:
#        ind = ind + 1
#        for i in texts:
#            if re.findall(a["award-re"], i):
#                if re.findall(b, i):
#                    current = current + 1
#        if current > most:
#            guess = a["nominees"][ind]
#            most = current
#            current = 0
#    a["winner"] = guess
#    print("The winner of", a["award"], "is", a["winner"], "!")

# old attempt at nominees function, please ignore
#def get_winners(tweets):
#    for a in awards:
#        possible_nominees = []
#        obj = "(.*) nomina(.*)" + a["award-re"] + "(.*)"
#        for t in tweets:
#            pt = re.search(obj, t)
#            if pt:
#                pt = pt.group()
#                found = False
#                for i in possible_nominees:
#                    if pt == i[0]:
#                        i[1] = i[1] + 1
#                        found = True
#                        break
#                if not found:
#                    possible_nominees.append([pt, 1])
#        nominees_guess = []
#        for pn in possible_nominees:
#            if len(nominees_guess) < nominees_per_award:
#                nominees_guess.append(pn)
#            else:
#                least_ind = 0
#                i = -1
#                for v in nominees_guess:
#                    i = i + 1
#                    if v[1] < nominees_guess[least_ind][1]:
#                        least_ind = i
#                if pn[1] > nominees_guess[least_ind][1]:
#                    nominees_guess[least_ind] = pn
#        for ng in nominees_guess:
#            a["nominees"].append(ng[0])
#        print("The nominees of ", a["award"], " are ", a["nominees"], "!")

# sample of awards
awards = ["best actress - motion picture - drama", "best actor - motion picture - drama", "best actress - motion picture - musical/comedy", 
"best actor - motion picture - musical/comedy", "best supporting actress", "best supporting actor", "best director"]

# sorts list of ["name", count] by lowest count first
def min_appearances(ele):
    return ele[1]

# assumes input of the form (list of ["name", count])
# will merge "will" with "will smith", and so on
# keeps the one with the higher count
# the other is changed to ["none", 0]
def join_names(ele):
    for i in ele:
        for j in ele:
            if i[0] in j[0] and i[0] is not j[0]:
                if i[1] < j[1]:
                    j[1] = j[1] + i[1]
                    i[0] = "none"
                    i[1] = 0
                else:
                    i[1] = i[1] + j[1]
                    j[0] = "none"
                    j[1] = 0
    return ele     

# removes all instances of ["none", 0] from the list of lists ele
# also checks if "rt" appears in the name and removes those elements
def remove_misses(ele):
    output = []
    for i in ele:
        if i[0] != "none":
            j = i[0].split()
            if "rt" not in j and "eonline" not in j and "http" not in j and "rteonline" not in j:
                output.append(i)
    return output

# given a list of [str, int], returns a list of str
def remove_count(ele):
    output = []
    for i in ele:
        output.append(i[0])
    return output

# attempts to find nominees of an award
# does not work with movies yet
nominees = []
def get_nominees(tweets):
    output = []
    for a in awards:
        award_re = re.sub(r'/', ' ', a)
        award_re = re.sub(r'[^\w\s]', '', award_re)
        award_re = award_re.lower()
        award_name = []
        award_name.append(award_re.split())
        # list of potential nominees
        pot_nominees = []
        for t in tweets:
            t = re.sub(r'/', ' ', t)
            t = re.sub(r'[^\w\s#]', '', t)
            t = re.sub(r'goldenglobes', '', t)
            t = re.sub(r'golden', '', t)
            t = re.sub(r'globe', '', t)
            t = re.sub(r'[G|g]olden [G|g]lobes', '', t)
            if (t.startswith('rt')):
                continue
            # if name is found with award, append name to list of potential nominees
            if (all([x in t for x in award_name[0]])):
                names = nlp(t)
                for name in names.ents:
                    if name.label_ == 'PERSON':
                        pot_nominees.append(name.text)
        # list of named entities found paired with how many instances of them were found
        counted_nominees = []
        for n in pot_nominees:
            c = pot_nominees.count(n)
            counted_nominees.append([n, c])
        # if named entity were found 250 times, there are 250 instances of ["name", 250] in pot_nominees
        # remove duplicates
        single_nominees = []
        for ele in counted_nominees:
            if ele not in single_nominees:
                single_nominees.append(ele)
        # join same people with slightly different named entity recognition
        # for example, "tina", "tina fey", "tina f" all same person -- create one entry for all 3
        joined_nominees = join_names(single_nominees)
        joined_nominees = remove_misses(joined_nominees)
        # get the 5 most mentioned people
        limited_nominees = []
        for n in joined_nominees:
            if len(limited_nominees) < nominees_per_award:
                limited_nominees.append(n)
            else:
                limited_nominees.sort(key=min_appearances)
                if limited_nominees[0][1] < n[1]:
                    limited_nominees[0] = n
        # list is in increasing order of most mentioned, so reverse list
        limited_nominees.reverse()
        # remove count (not necessary during testing)
        limited_nominees = remove_count(limited_nominees)
        # append pair of award and nominees to the output
        output.append([a, limited_nominees])
    # eventually will have to change the form of the output to fit the dictionary requested
    return output

print(get_nominees(data))

# a test to see if the join_names, remove_misses, and remove_count functions work
# lst = [["tina", 1], ["tina fey", 5], ["alexander", 6], ["alexander hamilton", 12], ["tina f", 4], ["rt cinema21", 21]]
# print(remove_misses(join_names(lst)))
# print(remove_count(lst))
