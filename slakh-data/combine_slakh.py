import requests


with open("D:\\Slakh\\new-slakh\\slakh2100.part.1", 'rb') as r:
    x1 = r.read()

with open("D:\\Slakh\\new-slakh\\slakh2100.part.2", 'rb') as r:
    x2 = r.read()

with open("D:\\Slakh\\new-slakh\\slakh2100.tar.gz", 'wb') as r:
    r.write(x1)
    r.write(x2)
