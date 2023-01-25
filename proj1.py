import re
import json
def get_winners():
    awards = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
    data = open('gg2013.json')
    tweets = json.load(data)
    res = []
    dict = {}
    for tweet in tweets:
        txt = tweet['text']
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', '', txt)
        win = re.search(r'(.*) (wins|won) (.*)', txt)
        if (win != None):
            str = win.group(1)
            split_str = str.split()
            str2 = win.group(3)
            for a in awards:
                a = a.lower()
                a = re.sub(r'[^\w\s]', '', a)
                award = re.search(a, str2)
                if (award):
                    award_str = award.group()
                    res.append((' '.join(split_str[-2:]), award_str))
    win_set = set(res)
    for winner in win_set:
        dict[winner] = res.count(winner)
    dict = sorted(dict.items(), key = lambda x: x[1])
    #winners = list(filter(lambda x: x[1] >= 10, dict))
    return dict

print(get_winners())


