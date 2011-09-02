import re

p = re.compile('\d+')
m = p.match('0123tempo')
print m.group()

def check_mode():
    if mode == "standard": print "mode is standard"
    else: print "mode is not standard"

mode = "standard"

check_mode()

mode = "other"

check_mode()



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

ll = [1, 2, 3]
print ll
ll.remove(1)
print ll
