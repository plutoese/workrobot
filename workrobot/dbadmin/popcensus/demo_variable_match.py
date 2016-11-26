# coding = UTF-8

from libs.datasheet.class_sheetanalyst import SheetAnalyst
from libs.datasheet.class_DataSheet import DataSheet
from os import path, listdir
import pandas as pd
from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection


file_path = r'E:\data\popcensus\origin'
print(listdir(file_path))

mongo = MongoDB()
mdb = MonDatabase(mongodb=mongo, database_name='region')
collection_variable = MonCollection(database=mdb, collection_name='storedvariable')

for i in range(1,9):
    variable_file = path.join(file_path, ''.join(['popcensus_2000_variable',str(i),'.xls']))
    rdata = pd.read_excel(io=variable_file, type=1, sheet='Sheet1')
    print(rdata)

    variable_dict = {}
    for ind in rdata.index:
        record = {'origin':rdata.loc[ind,'origin_var'],'variable':rdata.loc[ind,'matched_var'],'source':'中国人口普查','year':'2000'}
        print(record)
        collection_variable.collection.insert_one(record)