# coding = UTF-8

from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection

# 0. 连接数据库
collection_variable = MonCollection(database=MonDatabase(mongodb=MongoDB(),
                                                         database_name='variable'),
                                    collection_name='referencevariable')


# 1. 参数设置
CEIC_VARIABLE = False
CHINASTAT_VARIABLE = True

# 2. 导入CEIC变量
if CEIC_VARIABLE:
    ceic_collection = MonCollection(database=MonDatabase(mongodb=MongoDB(),
                                                         database_name='region'),
                                    collection_name='ceic')
    refer_variables = ceic_collection.collection.find().distinct('variable')
    source = 'CEIC'

# 3. 导入中国统计年鉴变量
if CHINASTAT_VARIABLE:
    Chinastat_collection = MonCollection(database=MonDatabase(mongodb=MongoDB(),
                                                              database_name='region'),
                                         collection_name='provincestat')
    refer_variables = Chinastat_collection.collection.find().distinct('variable')
    source = '中国统计年鉴'

if isinstance(refer_variables,list):
    for var in refer_variables:
        record = {'variable':var,'source':source}
        collection_variable.collection.insert_one(record)
