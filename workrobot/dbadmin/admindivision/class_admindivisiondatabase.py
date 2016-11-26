# coding=UTF-8

"""
=========================================
Region数据库中admindivision集合接口
=========================================

:Author: glen
:Date: 2016.11.17
:Tags: mongodb database collection admindivision
:abstract: admindivision集合接口

**类**
==================
AdminDivisionDatabase
    admindivision集合接口

**使用方法**
==================
admindivision集合接口

**示范代码**
==================
::

    >>># 连接MongoDB中的ProvinceStat集合
    >>>mongo = MongoDB()
    >>>mdb = MonDatabase(mongodb=mongo, database_name='region')
    >>>prostat = MonDBProvinceStat(database=mdb)
    >>># 返回集合中所有变量列表
    >>>print(prostat.variables)
    >>># 查询变量名
    >>>for item in prostat.search_variable('法人单位数',exact=True).distinct('variable'): print(item)
"""


from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection
from pymongo import ASCENDING
from bson import ObjectId


class AdminDivisionDatabase():
    """ 类AdminDivisionDatabase连接admindivision集合

    """
    def __init__(self):
        # 连接admindivision集合
        mongo = MongoDB()
        mdb = MonDatabase(mongodb=mongo, database_name='region')
        self.collection = MonCollection(database=mdb, collection_name='admindivision')

    # 查询
    def find(self,**conds):
        # 设置projection
        projection = conds.get('projection')
        if projection is None:
            projection = {'region':1,'year':1,'adminlevel':1,'acode':1,'_id':1,'parent':1,'uid':1}
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


if __name__ == '__main__':
    db = AdminDivisionDatabase()
    print(db.period)
    print(list(db.find(year='2010',projection={'region':1,'_id':0})))
    result = db.collection.collection.find_one({'year':'2000','region':'北京市'}).get('_id')
    print(result)
    print(list(db.collection.collection.find({'region':'西城区','year':'2000'})))



















