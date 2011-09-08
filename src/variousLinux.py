import re

p = re.compile('\d+')
m = p.match('0123tempo')
print m.group()

print float("")


from itertools import groupby

things = [["animal", "bear"], ["animal", "duck"], ["plant", "cactus"], ["vehicle", "speed boat"], ["vehicle", "school bus"]]

categories = []

for key, group in groupby(things, lambda x: x[0]):
    print "new group:"
    categories.append(key)
    print group
    for thing in group:
        print (thing[0], thing[1], key)

print categories

categories2 = [key[0] for key in groupby(things, lambda x: x[0])]
print categories2

animals = [thing[1] for thing in things if thing[0]=='animal']

print animals

print '{:04}'.format(21)