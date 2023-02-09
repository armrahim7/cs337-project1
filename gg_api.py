'''Version 0.35'''
import re
import json
import nltk
import spacy
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
nlp = spacy.load('en_core_web_lg')
NER = spacy.load("en_core_web_sm")
import time
import imdb
ia = imdb.IMDb()

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
            if "rt" not in j and "eonline" not in j and "http" not in j and "rteonline" not in j and "goldenglobes" not in j:
                output.append(i)
    return output

# given a list of [str, int], returns a list of str
def remove_count(ele):
    output = []
    for i in ele:
        output.append(i[0])
    return output

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

def find_parties(tweets):
    parties={}
    for twt in tweets:
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
    return parties


def best_party():
    parties = find_parties(load_data(2013))
    best=max(parties, key=parties.get)
    if parties[best][1]> 0:
        sentiment= 'loved it!'
    else:
        sentiment= 'hated it!'

    return f'Most Talked About party was thrown by {best} and people {sentiment}'

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
        txt = re.sub(r'/', ' or ', txt)
        txt = re.sub(r'[^\w\s.-]', '', txt)
        txt = re.sub(r'tv', 'television', txt)
        txt = re.sub(r't.v.', 'television', txt)
        txt = re.sub(r'movie', 'motion picture', txt)
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
    nominees = {}
    ppl_lst= ['actor','actress','director','producer','cecile','award']
    nouns= ['NN','NNS','NNP','NNPS']
    assigned=set()
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
        awrd= set(clean_award_name)
        # list of potential nominees
        pot_nominees = []
        for t in data:
            og_t=t
            t = t.lower()
            t = re.sub(r'/', ' ', t)
            t = re.sub(r'[^\w\s#]', '', t)
            t = re.sub(r'goldenglobes', '', t)
            t = re.sub(r'golden', '', t)
            t = re.sub(r'globe', '', t)
            t = re.sub(r'[G|g]olden [G|g]lobes', '', t)
            if (t.startswith('rt')):
                continue
            # if name is found with award, append name to list of potential nominees
            if any([ppl in a for ppl in ppl_lst]):
                if (all([x in t for x in clean_award_name])):
                    names = nlp(t)
                    for name in names.ents:
                        if name.label_ == 'PERSON':
                            pot_nominees.append(name.text)
            else:
                if (all([x in t for x in clean_award_name])):
                    pot = nlp(og_t)
                    for word in pot:
                        for ent in pot.ents:
                            if word.text == ent.text:
                                if word.tag_ in nouns  and ent.label_ != 'PERSON':
                                    pot_nominees.append(word.text)
                else:
                    t1=t.split(' ')
                    t_s= set(t1)
                    matches=len(t_s.intersection(awrd))
                    if matches > 0 and matches/len(awrd) > .7:
                        pot = nlp(og_t)
                        for word in pot:
                            for ent in pot.ents:
                                if word.text == ent.text:
                                    if word.tag_ in nouns  and ent.label_ != 'PERSON':
                                        pot_nominees.append(word.text)

   
    


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
        if not any(ppl in a for ppl in ppl_lst):
            good_nominees = []
            joined_nominees=sorted(joined_nominees, key = lambda x: x[1],reverse = True)
            done={}
            for mov in joined_nominees:
                if mov[1] != 1 :
                #if not'@'on mo and mov and 'RT' in mov and '#' not in mov:
                    items = ia.search_movie(mov[0])
                    id=items[0].movieID
                    if items != []:
                        title= items[0]['title'].lower()
                        mov_year = items[0].get('year')
                        genres= ia.get_movie(id).get('genres')
                        if clean_award_name[-1] in ['drama','musical']:
                            if genres != None and clean_award_name[-1].title() in genres:

                                #can check genre
                                if mov_year == (int(year)-1) or mov_year == (int(year)-2):
                                    if title not in done:
                                        good_nominees.append([title,mov[1]])
                                        done[title]= len(good_nominees)-1
                                    else:
                                        good_nominees[done[title]][1] += mov[1]
                        else:
                            if mov_year == (int(year)-1) or mov_year == (int(year)-2):
                                if title not in done:
                                    good_nominees.append([title,mov[1]])
                                    done[title]= len(good_nominees)-1
                                else:
                                    good_nominees[done[title]][1] += mov[1]
            good_nominees= remove_count(good_nominees)
            nominees[a]= good_nominees
        else:
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
    cands = {}
    useless_words = [' rt ', 'rt ', ' rt', 'http']
    stop_words = ['wish', 'hope', 'deserves', 'yay', 'woah', 'wow']
    people_words = ['actor', 'actress', 'director', 'award']
    #array of words not commonly used (or provides no semantic value) in tweets when discussing awards
    award_useless_words = ['performance', 'by', 'in', 'made', 'for', 'role', 'original', 'an']
    for a in OFFICIAL_AWARDS_1315:
        winners[a] = []
        cands[a] = []
        # remove punctuation from award name
        award_re = re.sub(r'/', ' ', a)
        award_re = re.sub(r'[^\w\s]', '', award_re)
        award_re = award_re.lower()
        award_re = re.sub(r'television', 'tv', award_re)
        award_split = award_re.split()
        clean_award_name = [x for x in award_split if x not in award_useless_words]
        # the words 'motion picture' were barely used when discussing tv awards
        if (('tv' in clean_award_name or 'score' in clean_award_name) and 'motion' in clean_award_name and 'picture' in clean_award_name):
            clean_award_name.remove('motion')
            clean_award_name.remove('picture')
        # list of potential nominees
        for t in data:
            t = t.lower()
            t = re.sub(r'/', ' ', t)
            t = re.sub(r'[^\w\s]', '', t)
            t = re.sub(r'goldenglobes', '', t)
            t = re.sub(r'golden', '', t)
            t = re.sub(r'globe', '', t)
            t = re.sub(r'[G|g]olden [G|g]lobes', '', t)
            if (t.startswith('rt')) or (any([x in t for x in stop_words])):
                continue
            # if name is found with award, append name to list of potential nominees
            if (all([x in t for x in clean_award_name])):
                if('supporting' in t and 'supporting' not in clean_award_name):
                    continue
                win = re.search(r'(.*) (wins|receive(s|d))', t)
                if(win):
                    phrase = win.group(1)
                    if (any([x in t for x in people_words])):
                        names = nlp(phrase)
                        for name in names.ents:
                            if(any([x in name.text for x in useless_words])):
                                continue
                            if name.label_ == 'PERSON':
                                cands[a].append(name.text)
                    else:
                        tokens = nlp(phrase)
                        for token in tokens.noun_chunks:
                            if(any([x in token.text for x in useless_words])):
                                continue
                            #weighs this weak strategy a little bit more for non-people awards
                            cands[a].append(token.text)
                            cands[a].append(token.text)
                win2 = re.search(r'goes to (.*)', t)
                if(win2):
                    phrase2 = win2.group(1)
                    if (any([x in t for x in people_words])):
                        names2 = nlp(phrase2)
                        for name in names2.ents:
                            if(any([x in name.text for x in useless_words])):
                                continue
                            if name.label_ == 'PERSON':
                                cands[a].append(name.text)
                    else:
                        tokens = nlp(phrase2)
                        for token in tokens.noun_chunks:
                            if(any([x in token.text for x in useless_words])):
                                continue
                            if(any([x in token.text for x in clean_award_name])):
                                continue
                            cands[a].append(token.text)
    for award in cands:
        cands_set = set(cands[award])
        if len(cands_set) > 0:
            winners[award] = max(cands_set, key = cands[award].count)
        else:
            winners[award] = ""
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    data = load_data(year)
    cands = dict()
    useless_words = [' rt ', 'rt ', ' rt']
    award_useless_words = ['performance', 'by', 'in', 'made', 'for', 'role', 'original']
    awards = OFFICIAL_AWARDS_1315
    for award in awards:
        cands[award] = []
    for txt in data:
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        for award in awards:
            award_re = award.lower()
            award_re = re.sub(r'/', ' ', award_re)
            award_re = re.sub(r'[^\w\s]', '', award_re)
            award_re = re.sub(r'television', 'tv', award_re)
            award_split = award_re.split()
            award_split = [x for x in award_split if x not in award_useless_words]
            if (('tv' in award_split or 'score' in award_split) and 'motion' in award_split and 'picture' in award_split):
                award_split.remove('motion')
                award_split.remove('picture')
            if(all([x in txt for x in award_split])):
                pre = re.search(r'(.*) (present(s|ed|er|ers|ing)?|introduc(e|ed|es|ing))', txt)
                if(pre):
                    phrase = pre.group(1)
                    doc = nlp(phrase)
                    for i in doc.ents:
                        if (any([x in i.text for x in useless_words])):
                            continue
                        if (i.label_ == 'PERSON'):
                            cands[award].append(i.text)
    presenters = dict()
    for award in cands:
        presenters[award] = []
        award_set = sorted(set(cands[award]), key = cands[award].count)
        if len(award_set) < 2:
            for a in award_set:
                presenters[award].append(a)
        else:
            presenters[award] = award_set[-2:]
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
    t1 = time.time()
    tweets = load_data(2013)
    output = {}
    hosts = get_hosts(2013)
    output["hosts"] = hosts
    nominees = get_nominees(2013)
    winners = get_winner(2013)
    presenters = get_presenters(2013)
    our_awards = get_awards(2013)
    output["award_data"] = {}
    for a in OFFICIAL_AWARDS_1315:
        output["award_data"][a] = {}
        output["award_data"][a]["presenters"] = presenters[a]
        output["award_data"][a]["nominees"] = nominees[a]
        output["award_data"][a]["winner"] = winners[a]
    with open ('data.json', 'w') as f:
        json.dump(output, f)
    host_sent = host_sentiment(hosts, tweets)
    dressed = best_and_worst_dressed(tweets)
    parties = best_party()
    with open ('readable_data.txt', 'w') as g:
        g.write(host_sent + "\n")
        for i in dressed:
            g.write(i + "\n")
        g.write(parties + "\n")
        g.write("Hosts: \n")
        for i in hosts:
            g.write(i + "\n")
        g.write("Our Extracted Award Names: \n")
        for i in our_awards:
            g.write(i + '\n')
        g.write('\n')
        g.write("Award Data: \n")
        for a in OFFICIAL_AWARDS_1315:
            g.write(a + "\n")
            g.write("Presenter(s):" + "\n")
            g.write(', '.join(output["award_data"][a]["presenters"])  + "\n")
            g.write("Nominees:" + "\n")
            g.write(', '.join(output["award_data"][a]["nominees"]) + "\n")
            g.write("Winner:" + "\n")
            g.write(output["award_data"][a]["winner"] + "\n")
            g.write('\n')
    print(time.time()-t1)
    return

if __name__ == '__main__':
    main()
