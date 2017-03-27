# coding = UTF-8

from pymongo import MongoClient

client = MongoClient('mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
dbase = client['application']['hospital']
record = dbase.collection.find({})

print(record)