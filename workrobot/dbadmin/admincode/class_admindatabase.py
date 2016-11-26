# coding=UTF-8

# -----------------------------------------------------------------------------------------
# @author: plutoese
# @date: 2015.10.10
# @class: AdminDatabase
# @introduction: 类AdminDatabase表示行政区划数据库。
# @property:
# - period: 数据库覆盖的年份
# @method:
# - find(self,**conds)：查询数据，参数conds是一系列参数。返回值是pymongo.cursor。
# - version(year)：数据库行政区划的版本，参数year是年份，默认参数None，表示所有年份。返回值
#                  是版本的列表。
# -----------------------------------------------------------------------------------------

from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection
from pymongo import ASCENDING
from bson import ObjectId


class AdminDatabase():
    """ 类AdminDatabase用来连接行政区划数据库

    """
    def __init__(self):
        # 连接AdminDatabase集合
        mongo = MongoDB()
        mdb = MonDatabase(mongodb=mongo, database_name='region')
        self.collection = MonCollection(database=mdb, collection_name='admincode')

    # 查询
    def find(self,**conds):
        # 设置projection
        projection = conds.get('projection')
        if projection is None:
            projection = {'region':1,'version':1,'adminlevel':1,'acode':1,'_id':1,'parent':1}
        else:
            conds.pop('projection')
        # 设置sorts
        sorts = conds.get('sorts')
        if sorts is None:
            sorts= [('year',ASCENDING),('acode',ASCENDING)]
        else:
            conds.pop('sorts')

        # 设置查询条件
        condition = dict()
        for key in conds:
            if isinstance(conds[key],list):
                condition[key] = {'$in':conds[key]}
            else:
                condition[key] = conds[key]

        # 返回查询结果
        return self.collection.find(condition,projection).sort(sorts)

    # 年份
    @property
    def period(self):
        return sorted(self.find().distinct('year'))

    # 版本号
    def version(self,year=None):
        if year is None:
            return sorted(self.find().distinct('version'))
        else:
            return sorted(self.find(year=str(year)).distinct('version'))

if __name__ == '__main__':
    db = AdminDatabase()
    print(db.period)
    print(db.version(year=2004))
    print(db.version())
    print(list(db.find(year='2010',projection={'region':1,'_id':0})))
    print(list(db.find(adminlevel=2,version='2004_12_31',projection={'region':1,'_id':0,'acode':1})))

    result = db.collection.collection.find_one({'year':'2000','region':'北京市'}).get('_id')
    print(result)
    print(list(db.collection.collection.find({'region':'西城区','year':'2000'})))



















