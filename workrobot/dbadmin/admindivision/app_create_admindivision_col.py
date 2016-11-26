# coding = UTF-8

import re
import numpy as np
import pandas as pd
import pickle
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection
from bson import ObjectId

# 0. 参数
FROM_FILE = False
IMPORT_NATION = False
IMPORT_REGION = True

# 1. 导入行政区划文献
if FROM_FILE:
    admin_division_file = r'E:\data\admindivision\admin.xlsx'
    admin_division_data = pd.read_excel(admin_division_file,sheetname=0,header=0)

    F = open(r'E:\data\admindivision\admin.pkl', 'wb')
    pickle.dump(admin_division_data, F)
    F.close()
else:
    F = open(r'E:\data\admindivision\admin.pkl', 'rb')
    admin_division_data = pickle.load(F)

# 2. 连接数据库
mcollection = MonCollection(database=MonDatabase(mongodb=MongoDB(), database_name='region'), collection_name='admindivision')

# 3. 导入中国这个特别的行政区划
if IMPORT_NATION:
    year = range(1985,2015)
    for y in year:
        China_record = {
            "year" : str(y),
            "region" : "中国",
            "adminlevel" : 1,
            "towletter" : "CN",
            "threeletter" : "CHN",
            "threenumber" : "156"
        }
        mcollection.collection.insert_one(China_record)

# 4. 分解导入中国行政区划
if IMPORT_REGION:
    for year, admin_division_grouped_by_year in admin_division_data.groupby('year'):
        for ind in admin_division_grouped_by_year.index:
            acode = str(admin_division_grouped_by_year.loc[ind,'a_code'])
            region = admin_division_grouped_by_year.loc[ind,'a_name']
            uid = str(admin_division_grouped_by_year.loc[ind,'uniq_ID'])
            aa = str(admin_division_grouped_by_year.loc[ind,'aa'])
            al = str(admin_division_grouped_by_year.loc[ind, 'al'])
            an = str(admin_division_grouped_by_year.loc[ind, 'an'])

            former = admin_division_grouped_by_year.loc[ind, 'father']
            if isinstance(former,float):
                if np.isnan(former):
                    former = None

            statement = admin_division_grouped_by_year.loc[ind, 'ADA_i']
            if isinstance(statement, float):
                if np.isnan(statement):
                    statement = None

            record = {"year" : str(year), "acode" : acode, "region" : region, "uid" : uid,
                      "aa" : aa, "al" : al, "an" : an, "former" : former, "statement" : statement}

            if re.match('^\d{2}0000',acode) is not None:
                admin_level = 2
                parent = mcollection.collection.find_one({'region':'中国','year':str(year)})['_id']
                if parent is None:
                    print('No parent!')
                    raise Exception
                record.update({'adminlevel':admin_level, 'parent':ObjectId(parent)})

                found = mcollection.collection.find_one({'uid':uid})
                if found is None:
                    mcollection.collection.insert_one(record)
                else:
                    print('Not insert --- ',record)

            elif re.match('^\d{4}00',acode) is not None:
                admin_level = 3
                parent_code = ''.join([acode[0:2],'0000'])
                parent = mcollection.collection.find_one({'acode':parent_code,'year':str(year)})['_id']

                if parent is None:
                    print('No parent!')
                    raise Exception

                record.update({'adminlevel': admin_level, 'parent': ObjectId(parent)})

                found = mcollection.collection.find_one({'uid': uid})
                if found is None:
                    mcollection.collection.insert_one(record)
                else:
                    print('Not insert --- ',record)

            else:
                admin_level = 4
                parent_code = ''.join([acode[0:4],'00'])
                grandpa_code = ''.join([acode[0:2],'0000'])
                parent = mcollection.collection.find_one({'acode':parent_code,'year':str(year)})
                grandpa = mcollection.collection.find_one({'acode':grandpa_code,'year':str(year)})

                if parent is None:
                    parent_id = None
                    if grandpa is None:
                        print('No parent or grandpa!')
                        raise Exception
                else:
                    parent_id = ObjectId(parent['_id'])

                record.update({'adminlevel': admin_level, 'parent': parent_id,'grandpa':ObjectId(grandpa['_id'])})

                found = mcollection.collection.find_one({'uid': uid})
                if found is None:
                    mcollection.collection.insert_one(record)
                else:
                    print('Not insert --- ',record)