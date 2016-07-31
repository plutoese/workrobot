# coding=UTF-8

"""
=========================================
数据集处理类
=========================================

:Author: glen
:Date: 2016.7.30
:Tags: dataset
:abstract: 对数据集进行合并、转换等基本处理

**类**
==================
BalancePanelConverter
    转换数据集格式为平衡面板

**使用方法**
==================


**示范代码**
==================
::

    >>># 创建BalancePanelConverter对象
    >>>bconverter = BalancePanelConverter(data=data)
    >>># 调用回调函数
    >>>print(bconverter())
"""

import numpy as np
import pandas as pd
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection
from libs.utils.class_formatconverter import MongoDBToPandasFormat

class BalancePanelConverter:
    """ 转换数据集格式为平衡面板

    :param pd.DataFrame data: 数据
    :param str func_name: 方法名称
    :param str 固定索引: 变量名表
    :return: 无返回值
    """
    def __init__(self, data=None, name='balanced panel', keep_index = None, *args, **kwargs):
        self._data = data
        self._name = name
        self._args = args
        self._kwargs = kwargs
        # 设置index是否置换
        self._sweeped = False

        self._index = self._data.index
        self._to_be_deleted_index = self._index
        index_names = list(self._data.index.names)
        if keep_index is not None:
            self._keep_index = keep_index
            keep_index_pos = index_names.index(self._keep_index)
            if keep_index_pos > 0:
                self._data = self._data.swaplevel()
                self._index = self._data.index
                index_names = list(self._data.index.names)
                self._sweeped = True

        self._keep_index = index_names[0]
        self._drop_index = index_names[1]

    def __call__(self):
        """ 回调函数

        :return: 返回变换后的数据
        :rtype: pandas.DataFrame
        """
        # 获取灵活索引上的所有特异值
        # 调用index.get_level_values()获取索引的所有值，并调用index.drop_duplicates()删除重复值
        to_keep_index = self._index.get_level_values(self._drop_index).drop_duplicates()
        # 对每个固定索引的值循环
        for row_label in sorted(set(result.index.get_level_values(self._keep_index))):
            # 获得单个固定索引值的DataFrame，删除包含NA值的列，并获取其索引值
            # 与上一轮循环获得的索引值to_keep_index做交集，作为下一轮循环的索引值
            to_keep_index = to_keep_index.intersection(self._data.loc[row_label].dropna().index)
            # 如果保留索引列表的长度小于1，则跳出循环
            if len(to_keep_index) < 1:
                break
            #print('------',to_keep_index)

        self._keep_fixed_index = to_keep_index
        # 取保留索引值的补集作为待删除索引值
        to_be_deleted_index = self._index.get_level_values(self._drop_index).drop_duplicates().difference(to_keep_index)
        # 删除标记的索引值，获得新的数据集
        self._data = self._data.drop(to_be_deleted_index, level=self._drop_index)

        if self._sweeped:
            return self._data.swaplevel()
        else:
            return self._data

    def __repr__(self):
        """ 打印对象

        :return: 返回对象信息
        :rtype: str
        """
        fmt_str = 'Balanced Panel: {}\n'.format(self.name)
        fmt_str = ''.join([fmt_str, 'Keeped index: {}\nKeeped index values: {}'.format(self._keep_index, ','.join(self._keep_fixed_index))])
        return fmt_str

    @property
    def name(self):
        """ 返回对象的名称

        :return: 返回对象的名称
        """
        return self._name


if __name__ == '__main__':
    mcollection = MonCollection(database=MonDatabase(mongodb=MongoDB(), database_name='region'),
                                collection_name='provincestat')
    cursor = mcollection.find({'variable':{'$in':['人均地区生产总值','私人控股企业法人单位数','城镇居民消费','城镇单位就业人员平均工资']}},
                              projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1,'year':1})
    #cursor = mcollection.find({'year':'2010', 'variable':{'$in':['人均地区生产总值','私人控股企业法人单位数','城镇居民消费','城镇单位就业人员平均工资']}},
    #                          projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1})
    #cursor = mcollection.find({'variable':'人均地区生产总值','acode':'110000'},
    #                          projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1,'year':1})
    mongoconverter = MongoDBToPandasFormat(cursor)

    # Test first
    #result = mongoconverter(values='value', index=['year'], columns='variable',dropna=True)
    result = mongoconverter(values='value', index=['acode','year'], columns='variable',dropna=True)
    #result = mongoconverter(values='value', index=['acode','year'], columns='variable',
    #                        dropna=False, balanced=True)
    #print(result)

    bconverter = BalancePanelConverter(data=result,keep_index='acode')
    print(bconverter())
    print(bconverter)




