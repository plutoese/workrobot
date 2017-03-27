# coding=UTF-8

"""
=========================================
MongoDB数据库具体集合类
=========================================

:Author: glen
:Date: 2016.7.24
:Tags: mongodb database
:abstract: 连接MongoDB数据库，并进行基本操作。

**类**
==================
MongoDB
    连接MongoDB数据库
MonDatabase
    连接MongoDB数据库中的database
MonCollection
    连接MongoDB数据库中的collection

**使用方法**
==================
连接MongoDB数据库
    创建MongoDB实例就可以建立数据库连接，可以通过两种方式创建数据库实例：其一是连接字符串，例如'mongodb://plutoese:z1Yh29@139.196.189.191:3717/'，其二是指定主机和端口。
连接MongoDB数据库中的Database
    创建MonDatabase实例就可以建立Database连接。
连接MongoDB数据库中的colletion
    创建MonCollection实例就可以建立collection连接。
MongoDB中的数据库列表
    调用MongoDB类中的database_names属性
关闭MongoDB数据库连接
    无论是MongoDB、MonDatabase及MonCollection类中，都有close()来关闭MongoDB数据库连接

**示范代码**
==================
::

    >>># 连接MongoDB
    >>>mongo = MongoDB(conn_str='mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
    >>># 连接MongoDB中的数据库
    >>>mdb = MonDatabase(mongodb=mongo, database_name='region')
    >>># 返回MongoDB中的数据库列表
    >>>print(mongo.client.database_names())
    >>># 返回MongoDB数据库中数据集合列表
    >>>print(mdb.collection_names)
    >>># 创建一个新的数据集合
    >>>mdb.create_collection('cities')
    >>># 删除一个数据集合
    >>>mdb.drop_collection('cities')
    >>># 连接数据库中的collection
    >>>mcollection = MonCollection(database=mdb, collection_name='cities')
    >>># 插入数据到collection中
    >>>mcollection.insert([{'name':'Andy'}])
    >>># 在collection中查询数据
    >>>print(list(mcollection.find({'name':'Tom'})))
    >>>#关闭MongoDB连接
    >>>mcollection.close()
"""

from pymongo import MongoClient
import pandas as pd

class MongoDB:
    """ 连接MongoDB数据库

    :param str host: 数据库主机，默认是'localhost'
    :param int port: 数据库端口，默认是27017
    :param str conn_str: 数据库连接字符串，例如'mongodb://plutoese:z1Yh29@139.196.189.191:3717/'
    :return: 无返回值
    """
    def __init__(self, host='localhost', port=27017, conn_str=None):
        # Client for a MongoDB instance
        # The clent object is thread-safe and has connection-pooling built in.
        if conn_str is not None:
            self._client = MongoClient(conn_str)
        else:
            self._client = MongoClient(host, port)

    def close(self):
        """ 关闭数据库连接

        :return: 无返回值
        """
        self._client.close()

    @property
    def client(self):
        """ 返回数据库连接

        :return: 返回数据库连接client
        :rtype: pymongo.MongoClient
        """
        return self._client

    @property
    def database_names(self):
        """ 返回数据库中Database的列表

        :return: 返回database列表
        :rtype: list
        """
        return self._client.database_names()


class MonDatabase:
    """ 连接MongoDB中的Database

    :param MongoDB mongodb: MongoDB连接
    :param str database_name: Database名称
    :return: 无返回值
    """
    def __init__(self,mongodb=None, database_name=None):
        self._mongodb = mongodb
        if database_name in self._mongodb.database_names:
            self._database = self._mongodb.client[database_name]
        else:
            print('No database named {}'.format(database_name))
            raise Exception

    def create_collection(self, collection_name=None):
        """ 创建一个数据集合

        :param str collection_name: 新集合的名称
        :return: 无返回值
        """
        if collection_name not in self.collection_names:
            self._database.create_collection(name=collection_name)
        else:
            print('The collection {} is already exist!'.format(collection_name))
            raise Exception

    def drop_collection(self, collection_name=None):
        """ 删除一个数据集合

        :param str collection_name: 待删除的数据集合的名称
        :return: 无返回值
        """
        if collection_name in self.collection_names:
            self._database.drop_collection(collection_name)
        else:
            print('No such collection: ',collection_name)
            raise Exception

    @property
    def collection_names(self):
        """ 返回MongoDB数据库中Database下属的collection列表

        :return: 返回collection列表
        :rtype: list
        """
        return self._database.collection_names(include_system_collections=False)

    @property
    def database(self):
        """ 返回MongoDB中的Database实例

        :return:
        """
        return self._database

    def close(self):
        """ 关闭数据库连接

        :return: 无返回值
        """
        self._mongodb.close()


class MonCollection:
    """ 连接MongoDB中Database下的数据集合Collection

    :param MonDatabase database: Database连接
    :param str collection_name: 数据集合collection名称
    :return: 无返回值
    """
    def __init__(self, database=None, collection_name=None):
        self._database = database
        if collection_name in self._database.collection_names:
            self._collection = self._database.database[collection_name]
        else:
            print('No such collection named {}'.format(collection_name))
            raise Exception

    def find(self, *args, **kwargs):
        """ 查询数据

        :param args:
        :param kwargs:
        :return:
        """
        return self._collection.find(*args, **kwargs)

    def create_index(self,keys):
        """ 建立索引

        :param str list keys: 索引，例如[("mike", pymongo.DESCENDING),("eliot", pymongo.ASCENDING)]
        :return: 无返回值
        """
        self._collection.create_index(keys=keys)

    def distinct(self, key=None, filter=None):
        """ 返回某个关键词下的所有特异值

        :param str key: 关键词
        :param dict filter: 过滤项
        :return: 返回某个关键词下的所有特异值
        :rtype: list
        """
        return self._collection.distinct(key, filter)

    def insert(self,documents):
        """ 插入数据到当前collection

        :param dict tuple list documents: 待插入的数据
        :return: 无返回值
        """
        if isinstance(documents,dict):
            self._collection.insert_one(documents)
        elif isinstance(documents,(tuple,list)):
            self._collection.insert_many(documents)
        else:
            print('Unsupported type: ',type(documents))
            raise Exception

    def close(self):
        """ 关闭数据库连接

        :return: 无返回值
        """
        self._database.close()

    @property
    def collection(self):
        """ 返回数据集合

        :return: 返回collection对象
        :rtype: pymongo.collection.Collection
        """
        return self._collection

if __name__ == '__main__':
    mongo = MongoDB(conn_str='mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
    mdb = MonDatabase(mongodb=mongo, database_name='region')
    print(mongo.database_names)
    print(mdb.collection_names)
    #mdb.create_collection('cities')
    #mdb.drop_collection('cities')
    mcollection = MonCollection(database=mdb, collection_name='provincestat')
    #mcollection.insert([{'name':'Andy'}])
    #print(list(mcollection.find({'name':'Tom'})))
    #mcollection.close()

    query_str = {
        'province': '上海',
        'variable': {'$in':['第一产业增加值', '第二产业增加值','第三产业增加值']}
    }
    found = mcollection.find(query_str,
                             projection={'_id':0,'province':1,'variable':1,'value':1,'year':1},
                             sort=[('year',1)])
    rdata = [item for item in found]
    mdata = pd.DataFrame(rdata)
    print(mdata)

    print(pd.pivot_table(mdata,values='value',index=['year'],columns=['variable']))