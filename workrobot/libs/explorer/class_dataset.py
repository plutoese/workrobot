# coding=UTF-8

"""
=========================================
数据集类
=========================================

:Author: glen
:Date: 2016.7.29
:Tags: dataset
:abstract: 对数据集进行封装，工作流设计

**类**
==================
DataSet
    数据集类


**使用方法**
==================
通过数据（pandas的DataFrame类型）创建DataSet对象，添加方法到DataSet的工作流程中，然后通过run方法对数据进行操作。


**示范代码**
==================
::

    >>># 创建示范数据
    >>>d = pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    >>># 创建DataSet对象
    >>>my_data_set = DataSet(d,'my data')
    >>># 添加方法到工作流程中
    >>>my_data_set.add_data_method(LogVariable(d,['one','two']),method_name='log',method_type=1)
    >>># 运行工作流程
    >>>my_data_set.run()
"""

from libs.utils.class_variable import VariableCreator, DelVariables
from libs.utils.class_basicmodel import Describe
import pandas as pd
import numpy as np
from copy import deepcopy
from collections import OrderedDict, namedtuple
from libs.utils.class_formatconverter import MonCollection, MongoDB, MonDatabase, MongoDBToPandasFormat

class DataSet:
    """ 对数据集进行封装

    :param pandas.DataFrame,list data: 数据
    :param str name: 数据集名称
    :param str type: 数据集类型
    :return: 无返回值
    """
    def __init__(self, data=None, name='', type='unknown'):
        # 数据集的名称
        self._name = name
        # 数据集类型
        self._type = type

        if isinstance(data, pd.DataFrame):
            self._raw_data = data
        elif isinstance(data,list):
            self._raw_data = pd.DataFrame(data)
        else:
            print('Unsupported type!')
            raise TypeError

        # 数据集数据
        self._work_data = deepcopy(self._raw_data)
        # 数据集工作流程
        self._work_flow = OrderedDict()
        # 分析结果
        self._analysis_result = OrderedDict()

    def add_data_method(self, method=None, method_name=None, method_type=1):
        """ 添加工作流程操作方法

        :param method: 操作方法
        :param method_name: 操作名称
        :param method_type: 方法类型，1-变量方法, 2-分析方法
        :return: 无返回值
        """
        Method = namedtuple('Method',['type','method'])

        if method_name is None:
            method_name = str(len(self._work_flow))
            if method_name in self._work_flow:
                print('The name is already in!')
                raise Exception

        # 加入方法到流程中
        self._work_flow[method_name] = Method(type=method_type, method=method)

    def run(self, methods=None):
        """ 运行工作流中的方法对数据进行分析

        :param methods: 方法名称的列表，缺省值为None
        :return: 无返回值
        """
        if methods is None:
            methods_list = self._work_flow
        else:
            for method_name in methods:
                if method_name not in self._work_flow:
                    print('The method is not existed!')
                    raise Exception
            methods_list = methods

        # 运行工作流中的所有方法或指定的方法
        for method_name in methods_list:
            if self._work_flow[method_name].type == 1:
                self._work_data = self._work_flow[method_name].method()
            else:
                self._analysis_result[method_name] = self._work_flow[method_name].method()

    def __repr__(self):
        """ 打印对象的信息

        :return: 返回对象的信息
        :rtype: str
        """
        fmt_str = '='*80
        fmt_str = ''.join(['\n',fmt_str,'\n'])
        fmt_str = ''.join([fmt_str,'DataSet: {}'.format(self._name),'\n'])
        fmt_str = ''.join([fmt_str,'-'*80,'\n'])
        fmt_str = ''.join([fmt_str,self._raw_data.__repr__(),'\n'])
        fmt_str = ''.join([fmt_str,'-'*80,'\n'])
        for key in self._work_flow:
            fmt_str = ''.join([fmt_str,self._work_flow[key].method.__repr__(),'\n'])
            fmt_str = ''.join([fmt_str,'~'*80,'\n'])
        return ''.join([fmt_str,'='*80,'\n'])

    @property
    def data(self):
        return self._work_data

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

if __name__ == '__main__':
    d = pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    my_data_set = DataSet(d,'my data')
    my_data_set.add_data_method(VariableCreator(data=my_data_set._work_data, func=np.log, name='log',
                                                  variable_names='one',mode='append'),
                                method_name='log',method_type=1)
    print(my_data_set._work_data)
    my_data_set.add_data_method(DelVariables(data=my_data_set._work_data, name='del', variable_names=['one']),
                                method_name='del',method_type=1)
    my_data_set.run()
    print(my_data_set)
    print(my_data_set.data)

    print('------------------Test Real World Example----------------')
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
    real_world_dataset = DataSet(result,'region data')

    real_world_dataset.add_data_method(VariableCreator(data=real_world_dataset.data, func=np.log,
                                                       name='log',variable_names=['人均地区生产总值'],
                                                       mode='append'),
                                method_name='log',method_type=1)
    real_world_dataset.add_data_method(Describe(data=real_world_dataset.data),
                                       method_name='describe',method_type=2)
    real_world_dataset.run()
    print(real_world_dataset.data)
    print(real_world_dataset)


