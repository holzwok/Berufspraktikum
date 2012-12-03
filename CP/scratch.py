
x = (None, 3)
y = (None, 4)
fetch = [x, y]

print fetch

x = [x[0] if x[0] else 0 for x in fetch]
print x

x = [x[1] if x[1] else 0 for x in fetch]
print x
