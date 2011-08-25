import re

p = re.compile('\d+')
m = p.match('tempo')
print m.group()