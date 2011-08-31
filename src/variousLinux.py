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
