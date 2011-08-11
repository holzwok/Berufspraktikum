import os

print os.name

d = {666:1000, 777:2000, -1:3000}

if d.has_key(-1):
    not_found = d.pop(-1)
else:
    not_found = 0
    
print not_found
print d
 
# this sets not_found = number of pixels outside of cells AND removes the key:value pair from the dict d!  