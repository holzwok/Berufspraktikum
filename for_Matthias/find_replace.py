
text = "Ihr naht euch wieder, schwankende Gestalten,\
Die frueh sich einst dem trueben Blick gezeigt.\
Versuch ich wohl, euch diesmal festzuhalten?\
Fuehl ich mein Herz noch jenem Wahn geneigt?\
Ihr draengt euch zu! nun gut, so moegt ihr walten,\
Wie ihr aus Dunst und Nebel um mich steigt;\
Mein Busen fuehlt sich jugendlich erschuettert\
Vom Zauberhauch, der euren Zug umwittert."

itemlist = ["Herz", "Wahn"]

for item in itemlist:
    text = text.replace(item, "{"+item+"}")
    
print text