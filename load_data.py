import json
def load_data(year):
    name = f'gg{year}.json'
    data = open(name)
    tweets_data = json.load(data)
    tweets = []
    for tweet in tweets_data:
        tweets.append(tweet['text'])
    return tweets