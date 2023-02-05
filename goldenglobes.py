import json

f = open('C:\Files\Northwestern\"CS 337"\gg2013.json')
data = json.load(f)

print('Tweet count:', len(data))
