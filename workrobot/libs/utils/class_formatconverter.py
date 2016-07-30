# coding=UTF-8

"""
=========================================
格式转换类
=========================================

:Author: glen
:Date: 2016.7.21
:Tags: format conversion
:abstract: 格式转换

**类**
==================
MongoDBFormatConverter
    MongoDB数据格式转换基类
MongoDBToPandasFormat
    MongoDB数据格式转换为Pandas支持的格式
PandasDataStructureTransformer
    Pandas支持的数据格式相互转换，无须实例化


**使用方法**
==================
转换MongoDB数据格式到Pandas支持的数据格式（pymongo.cursor.Cursor -> pandas.DataFrame)
    创建MongoDBToPandasFormat对象，调用__call__()

**示范代码**
==================
::

    >>># 创建MongoDBToPandasFormat对象
    >>>mongoconverter = MongoDBToPandasFormat(cursor)
    >>># 连接MongoDB中的数据库
    >>>result = mongoconverter(values='value', index=['year'], columns='variable',dropna=True)
"""

import pandas as pd
from pymongo.cursor import Cursor
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection


class MongoDBToPandasFormat:
    """ MongoDB数据格式转换为Pandas的数据格式
    :param pymongo.cursor.Cursor cursor: MongoDB数据库返回结果
    :return: 无返回值
    """
    def __init__(self, cursor=None):
        if isinstance(cursor,Cursor):
            self._cursor = cursor
        else:
            print('Unsupported type: ',type(cursor))
            raise TypeError

    def __call__(self, values=None, index=None, columns=None, dropna=True, fill_value=None, balanced=False):
        # 把MongoDB数据库返回结果转换为单纯字典列表
        self._pure_data_dict_list = self.__to_atom_value()

        # 把单纯字典列表转换为pandas的DataFrame数据格式
        self._raw_data_dataframe = pd.DataFrame(self._pure_data_dict_list)
        return PandasDataStructureTransformer.long_table_to_wide_table(self._raw_data_dataframe,
                                                                       index=index, columns=columns, values=values,
                                                                       dropna=dropna, fill_value=fill_value,
                                                                       balanced=balanced)

    def __to_atom_value(self):
        """ 辅助函数，使得返回的字典中key对应的value是基本类型，例如int,float或str。我们称其为单纯字典列表。

        :return: 返回转换后的字典列表
        """
        result = []
        for item in self._cursor:
            row_item = dict()
            for key in item:
                if isinstance(item[key],(int,float,str)):
                    row_item[key] = item[key]
                elif isinstance(item[key],(list,tuple)):
                    row_item.update({''.join([key,str(i)]):item[key][i] for i in range(len(item[key]))})
                elif isinstance(item[key],dict):
                    row_item.update({'_'.join([key,in_key]):item[key][in_key] for in_key in item[key]})
                else:
                    print('Unhandled Type: ',type(item[key]))
                    raise Exception
            result.append(row_item)
        return result


class PandasDataStructureTransformer:
    """ 用于对Pandas的各种数据格式进行相互转换，只有classmethod，无须实例化

    :return: 无返回值
    """
    def __init__(self):
        pass

    @classmethod
    def long_table_to_wide_table(cls, dataframe=None,
                                 values=None, index=None, columns=None,
                                 dropna=True, fill_value=None,
                                 balanced=False, keep=None):
        """ 把长格式表格转换为宽格式表格

        :param pandas.DataFrame dataframe: 长格式数据表格
        :param values: 详见pandas.pivot_table()函数参数说明
        :param index: 详见pandas.pivot_table()函数参数说明
        :param columns: 详见pandas.pivot_table()函数参数说明
        :param dropna: 详见pandas.pivot_table()函数参数说明
        :param fill_value: 详见pandas.pivot_table()函数参数说明
        :return: 返回转换后的宽格式表格
        :rtype: pandas.DataFrame
        """
        result = pd.pivot_table(data=dataframe, values=values, index=index, columns=columns,
                                dropna=dropna,fill_value=fill_value)
        if len(index) > 1 and balanced:

            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            keep_index = result.index.get_level_values(index[1]).drop_duplicates()
            for row_label in sorted(set(result.index.get_level_values(index[0]))):
                tmp_result = result.loc[row_label].dropna()
                keep_index = keep_index.intersection(tmp_result.index)
                if len(keep_index) < 1:
                    break
                print('------',keep_index.intersection(result.loc[row_label].index))

            to_be_deleted_index = result.index.get_level_values(index[1]).drop_duplicates().difference(keep_index)
            result = result.drop(to_be_deleted_index,level=index[1])

        return result


if __name__ == '__main__':
    mcollection = MonCollection(database=MonDatabase(mongodb=MongoDB(), database_name='region'),
                                collection_name='provincestat')
    #cursor = mcollection.find({'variable':{'$in':['人均地区生产总值','私人控股企业法人单位数','城镇居民消费','城镇单位就业人员平均工资']}},
    #                          projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1,'year':1})
    #cursor = mcollection.find({'year':'2010', 'variable':{'$in':['人均地区生产总值','私人控股企业法人单位数','城镇居民消费','城镇单位就业人员平均工资']}},
    #                          projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1})
    cursor = mcollection.find({'variable':'人均地区生产总值','acode':'110000'},
                              projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1,'year':1})
    mongoconverter = MongoDBToPandasFormat(cursor)

    # Test first
    result = mongoconverter(values='value', index=['year'], columns='variable',dropna=True)
    #result = mongoconverter(values='value', index=['acode','year'], columns='variable',dropna=True)
    #result = mongoconverter(values='value', index=['acode','year'], columns='variable',
    #                        dropna=False, balanced=True)
    print(result)
    result.to_excel('e:/backup/result.xlsx')


