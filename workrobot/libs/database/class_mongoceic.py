# coding=UTF-8

"""
=========================================
MongoDB数据库的ceic集合
=========================================

:Author: glen
:Date: 2016.7.26
:Tags: mongodb database collection ceic
:abstract: 对ceic集合进行具体操作

**类**
==================
MonDBCEIC
    对CEIC集合进行具体操作

**使用方法**
==================
MonDBCEIC提供变量列表打印，变量查询等功能

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

from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection


class MonDBCEIC(MonCollection):
    """ 对ceic集合进行具体操作

    :param MonDatabase database: MongoDB数据库中的database实例
    :param str collection_name: MongoDB数据库中的collection名称
    :return: 无返回值
    """
    def __init__(self, database=MonDatabase(mongodb=MongoDB(), database_name='region'),
                 collection_name='ceic'):
        super().__init__(database=database, collection_name=collection_name)

    @property
    def variables(self):
        """ 返回所有变量列表

        :return: 返回所有变量列表
        :rtype: list
        """
        return self.distinct('variable')

    @property
    def period(self):
        """ 返回所有时期列表

        :return: 返回所有时期列表
        :rtype: list
        """
        return sorted(self.distinct('year'))

    @property
    def acode(self):
        """ 返回所有地区代码

        :return: 返回所有地区代码
        :rtype: list
        """
        return sorted(self.distinct('acode'))

    @property
    def acode_and_region(self):
        return dict(set([(item['acode'],item['region'])
                         for item in self.find({},projection={'_id':0,'acode':1,'region':1})]))

    def search_variable(self, var=None, exact=False):
        """ 查询变量

        :param str var: 待查询的变量关键词
        :param bool exact: 是否完全匹配
        :return: 返回变量查询结果
        :rtype: list
        """
        if exact:
            return self.find({'variable':var})
        else:
            return self.find({'variable':{'$regex':var}})

    def info(self):
        """ 打印数据库基本信息

        :return: 无返回值
        """
        print('='*80)
        print('Collection ceic infomation')
        print('Variables: ')
        i = 1
        for item in sorted(self.variables):
            print(i,': ',item)
            i += 1
        print('-'*80)
        print('Period: ')
        print(self.period)
        print('-'*80)
        print('Region: ')
        acode_to_region_dict = self.acode_and_region
        for code in self.acode:
            print(code,': ',acode_to_region_dict[code])
        print('='*80)


if __name__ == '__main__':
    mongo = MongoDB()
    mdb = MonDatabase(mongodb=mongo, database_name='region')
    prostat = MonDBCEIC(database=mdb)
    print(len(prostat.variables))
    for item in prostat.search_variable('生产').distinct('variable'):
        print(item)

    print(prostat.period)
    print(prostat.acode)
    #print(len(prostat.acode_and_region))
    prostat.info()




