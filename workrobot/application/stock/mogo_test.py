from pymongo import MongoClient

client = MongoClient('mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
dbase = client['region']['provincestat']
record = dbase.collection.find({'province':'北京'})

for item in record:
    print(item)