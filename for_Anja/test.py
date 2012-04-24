
halfwindow = 3
mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

def moving_average(data, win):
    if not win%2: # even
        return [sum(data[x-win/2:x+win/2])/win for x in range(win/2, len(data)-win/2+1)]
    else:         # odd
        return [sum(data[x-(win-1)/2:x+(win+1)/2])/win for x in range((win-1)/2, len(data)-(win+1)/2+1)]

win = 3
print moving_average(mylist, win)
