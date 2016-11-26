# coding=UTF-8

# -----------------------------------------------------------------------------------------
# @author: plutoese
# @date: 2016.10.24
# @class: PopCensusDatabase
# @introduction: 类PopCensusDatabase表示人口普查数据库
# @property:
# - period: 数据库覆盖的年份
# @method:
# - find(self,**conds)：查询数据，参数conds是一系列参数。返回值是pymongo.cursor。
# - version(year)：数据库行政区划的版本，参数year是年份，默认参数None，表示所有年份。返回值
#                  是版本的列表。
# -----------------------------------------------------------------------------------------

from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection
from bson.objectid import ObjectId
from dbadmin.admincode.class_admindatabase import AdminDatabase


class PopCensusDatabase():
    """ 类PopCensusDatabase表示人口普查数据库

    """
    def __init__(self):
        # 连接PopCensus集合
        mongo = MongoDB()
        mdb = MonDatabase(mongodb=mongo, database_name='region')
        self.collection = MonCollection(database=mdb, collection_name='popcensus')

    # 年份
    @property
    def period(self):
        return sorted(self.collection.find().distinct('year'))

    # 年份
    @property
    def variables(self):
        return sorted(self.collection.find().distinct('variable'))


if __name__ == '__main__':
    popdb = PopCensusDatabase()
    #print(popdb.period)
    #print(popdb.variables)

    acode_db = AdminDatabase()

    for record in popdb.collection.find():
        found = acode_db.collection.collection.find_one({'_id':record.get('regionid')},projection={'_id':0,'region':1,'acode':1})
        if found is not None:
            if record.get('acode') != found.get('acode'):
                print(record.get('region'),record.get('acode'),found.get('acode'))
                raise Exception
        else:
            print(record.get('region'),record.get('acode'),record.get('regionid'))

    '''
    for year in popdb.collection.find().distinct('year'):
        for acode in popdb.collection.find({'year':year}).distinct('acode'):
            record = list(acode_db.collection.find({'acode':acode,'year':'2010'},projection={'acode':1,'year':1}))
            if len(record) < 1:
                print(acode,popdb.collection.collection.find_one({'year':year,'acode':acode}))
                #popdb.collection.collection.update_many({'year':year,'acode':acode},{'$set': {'regionid': ''}})
            elif len(record) > 1:
                print('Too many',acode,record)
                raise Exception
            else:
                #print(record[0].get('_id'))
                popdb.collection.collection.update_many({'year':year,'acode':acode},
                                                        {'$set': {'regionid': ObjectId(record[0].get('_id'))}})
    '''

















