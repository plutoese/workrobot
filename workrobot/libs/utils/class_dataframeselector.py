# coding=UTF-8

"""
=========================================
数据库选择器类
=========================================

:Author: glen
:Date: 2016.8.6
:Tags: Database Selector
:abstract: 根据不同的标准选择数据框

**类**
==================
DataFrameSelector
    数据框选择器



**使用方法**
==================


**示范代码**
==================

"""

import pickle
import pandas as pd
from libs.imexport.class_mongodb import MongoDB, MonDatabase
from libs.database.class_mondbprovincestat import MonDBProvinceStat
from libs.database.class_mongoceic import MonDBCEIC
from libs.utils.class_formatconverter import MongoDBToPandasFormat


class DataFrameSelector:
    """ MongoDB数据格式转换为Pandas的数据格式

    :param pandas dataframe: 数据框
    :return: 无返回值
    """
    def __init__(self, dataframe=None):
        self._origin_dataframe = dataframe


if __name__ == '__main__':
    DATABASES = {1: 'region'}
    COLLECTIONS = {1: MonDBProvinceStat, 2: MonDBCEIC}

    DATABASE_CHOICE = 1
    COLLECTION_CHOICE = 2
    user_database = MonDatabase(mongodb=MongoDB(), database_name=DATABASES.get(DATABASE_CHOICE))
    user_colllection = COLLECTIONS.get(COLLECTION_CHOICE)(database=user_database)

    USER_PROJECTION = {'_id':0,'variable':1,'value':1,'acode':1,'year':1}
    USER_SORT = [('acode',1),('year',1)]

    USER_FILTER =  {}
    cursor = user_colllection.find(filter=USER_FILTER, projection=USER_PROJECTION, sort=USER_SORT)

    USER_DATAFRAME_INDEXES = ['year','acode']

    mongoconverter = MongoDBToPandasFormat(cursor)
    raw_data = mongoconverter(values='value', index=USER_DATAFRAME_INDEXES, columns='variable',dropna=True)

    print(raw_data.loc[2011])
    '''
    dselector = DataFrameSelector(dataframe=raw_data)

    F = open(r'E:\github\workrobot\workrobot\files\ceic_raw_data_year.pkl', 'wb')
    pickle.dump(raw_data, F)
    F.close()'''
