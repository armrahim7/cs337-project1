'''Version 0.35'''
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

nominees_per_award = 5
award_count = 26

# loads the text of tweets given a year into a list
def load_data(year):
    name = f'gg{year}.json'
    data = open(name)
    tweets_data = json.load(data)
    tweets = []
    for tweet in tweets_data:
        tweets.append(tweet['text'])
    return tweets

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

# lst of str -> lst of str
# given a list of str, returns a lst
# of str without any str that were contained
# inside other str of that list
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

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    data = load_data(year)
    possible_candidates = []
    for txt in data:
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
    hosts = join_hosts(final_candidates)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    data = load_data(year)
    award_words = ['movie', 'motion', 'picture', 'series', 'television', 'tv', 'film', 'score', 'song', 'screenplay']
    award_cands = []
    useless_words = [' rt ', 'rt ', ' rt', 'goldenglobes', 'golden', 'globes', 'her', 'his', 'their']
    for txt in data:
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
                    award_cands.append('best ' + cand)
        reg2 = re.search(r'(.*) award',txt)
        if(reg2):
            str2 = reg2.group(1)
            misc = re.search(r'receives? (.*)', str2)
            if(misc):
                misc_award = misc.group(1)
                if(any([x in misc_award for x in useless_words])):
                    continue
                award_cands.append(misc_award + ' award')
    award_set = (set(award_cands))
    awards = []
    for a in award_set:
        if award_cands.count(a) > 4:
            awards.append(a)
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    data = load_data(year)
    for i in data:
        i.lower()
    nominees = {}
    for a in OFFICIAL_AWARDS_1315:
        # remove punctuation from award name
        award_re = re.sub(r'/', ' ', a)
        award_re = re.sub(r'[^\w\s]', '', award_re)
        award_re = award_re.lower()
        award_name = []
        award_name.append(award_re.split())
        # remove unhelpful words from award name
        clean_award_name = []
        for word in award_name[0]:
            if word != "in" and word != "or" and word != "a" and word != "an" and word != "performance" and word != "by" and word != "made" and word != "for" and word != "any":
                clean_award_name.append(word)
        # list of potential nominees
        pot_nominees = []
        for t in data:
            t = re.sub(r'/', ' ', t)
            t = re.sub(r'[^\w\s#]', '', t)
            t = re.sub(r'goldenglobes', '', t)
            t = re.sub(r'golden', '', t)
            t = re.sub(r'globe', '', t)
            t = re.sub(r'[G|g]olden [G|g]lobes', '', t)
            if (t.startswith('rt')):
                continue
            # if name is found with award, append name to list of potential nominees
            if (all([x in t for x in clean_award_name])):
                names = nlp(t)
                for name in names.ents:
                    if name.label_ == 'PERSON':
                        pot_nominees.append(name.text)
        # list of named entities found paired with how many instances of them were found
        counted_nominees = []
        for n in pot_nominees:
            c = pot_nominees.count(n)
            counted_nominees.append([n, c])
        # if named entity was found 250 times, there are 250 instances of ["name", 250] in pot_nominees
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
        nominees[a]= limited_nominees
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    data = load_data(year)
    winners = {}
    for a in OFFICIAL_AWARDS_1315:
        # remove punctuation from award name
        award_re = re.sub(r'/', ' ', a)
        award_re = re.sub(r'[^\w\s]', '', award_re)
        award_re = award_re.lower()
        award_name = []
        award_name.append(award_re.split())
        # remove unhelpful words from award name
        clean_award_name = []
        for word in award_name[0]:
            if word != "in" and word != "or" and word != "a" and word != "an" and word != "performance" and word != "by" and word != "made" and word != "for" and word != "any":
                clean_award_name.append(word)
        # list of potential nominees
        pot_nominees = []
        for t in data:
            t = re.sub(r'/', ' ', t)
            t = re.sub(r'[^\w\s#]', '', t)
            t = re.sub(r'goldenglobes', '', t)
            t = re.sub(r'golden', '', t)
            t = re.sub(r'globe', '', t)
            t = re.sub(r'[G|g]olden [G|g]lobes', '', t)
            if (t.startswith('rt')):
                continue
            # if name is found with award, append name to list of potential nominees
            if (all([x in t for x in clean_award_name])):
                names = nlp(t)
                for name in names.ents:
                    if name.label_ == 'PERSON':
                        pot_nominees.append(name.text)
        # list of named entities found paired with how many instances of them were found
        counted_nominees = []
        for n in pot_nominees:
            c = pot_nominees.count(n)
            counted_nominees.append([n, c])
        # if named entity was found 250 times, there are 250 instances of ["name", 250] in pot_nominees
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
        winners[a]= limited_nominees[0]
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    data = load_data(year)
    cands = dict()
    award_names = []
    useless_words = [' rt ', 'rt ', ' rt']
    for award in OFFICIAL_AWARDS_1315:
        award_names.append(award.split())
        cands[' '.join(award.split())] = []
    for txt in data:
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
    presenters = dict()
    for award in cands:
        presenters[award] = []
        award_set = set(cands[award])
        for a in award_set:
            presenters[award].append(a)
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    output = {}
    output["hosts"] = get_hosts(2013)
    nominees = get_nominees(2013)
    winners = get_winner(2013)
    presenters = get_presenters(2013)
    output["award_data"] = {}
    for a in OFFICIAL_AWARDS_1315:
        output["award_data"][a] = {}
        output["award_data"][a]["presenters"] = presenters[a]
        output["award_data"][a]["nominees"] = nominees[a]
        output["award_data"][a]["winner"] = winners[a]
    with open ('data.json', 'w') as f:
        json.dump(output, f)
    return

if __name__ == '__main__':
    main()
