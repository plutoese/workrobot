# coding = UTF-8

import re
from libs.database.class_mondbprovincestat import MonDBProvinceStat
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection

mongo = MongoDB()
mdb = MonDatabase(mongodb=mongo, database_name='region')
prostat = MonDBProvinceStat(database=mdb)

# 1. 修正变量名重合的问题
variables_origin = set(prostat.variables)
variables_no_space = set([re.sub('\s+','',var) for var in prostat.variables])

i = 1
for item in sorted(prostat.variables):
    print(i,': ',item,' -- ',len(item))
    i += 1