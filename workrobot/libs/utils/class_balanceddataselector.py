# coding=UTF-8

"""
=========================================
数据集析出类
=========================================

:Author: glen
:Date: 2016.8.13
:Tags: DataFrame DataSet Select
:abstract: 解析数据集，析出平衡数据集

**类**
==================
BalancedDataSelector
    数据集析出器


**使用方法**
==================


**示范代码**
==================
"""

import re
import numpy as np
import pickle
import random
import pandas as pd
from collections import defaultdict
from copy import deepcopy
from collections import OrderedDict
from itertools import combinations, product
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection


class BalancedDataSelector:
    """ 创建实例

    :param pandas.DataFrame data: 数据框
    """
    def __init__(self, data):
        self._data = data

        # 生成True or False矩阵，缺失数据的元素为False，否则为True
        self._bool_data = self._data.notnull()
        # 缺失数据的元素为True，否则为False
        self._bool_false_data = self._data.isnull()

        # 所有元素都为True的子矩阵
        self.data_without_na = self._bool_false_data.loc[:,  self._bool_data.all()]
        # 并非所有元素都为True的子矩阵
        self.data_with_na = self._bool_false_data.loc[:, ~(self._bool_data.all())]

        # 数据框的行数和列数
        self._nrows, self._ncols = self._data.shape

    @classmethod
    def assembly(cls, single_variable_false_position_dict=None, max_na_number_per_variable=None):
        """ 按照最多NA的标准装配数据框

        :param single_variable_false_position_dict:
        :param max_na_number_per_variable:
        :return:
        """
        # 装配完成储存结果到selected_dataframe
        selected_dataframe = dict()
        selected_dataframe[1] = single_variable_false_position_dict

        for round in range(2, len(selected_dataframe[1])+1):
            # 上一轮储存的结果
            variable_dict_each_round_kept = selected_dataframe[round-1]

            # 用单个变量拓展上一轮得到的结果
            # 得到union_key_list列表，其值是tuple，第一个元素是单个变量和上一轮得到结果变量的并的frozenset
            # 第二个元素是上述变量所指向的缺失数据行的并
            union_key_list = [(frozenset(set(extend_key) | set(round_key)),single_variable_false_position_dict[extend_key].union(variable_dict_each_round_kept[round_key]))
                              for extend_key in single_variable_false_position_dict
                              for round_key in variable_dict_each_round_kept]

            # --------此处测试打印--------
            # print('---------------round{}------------'.format(round))
            # print(union_key_list)
            # --------此处测试打印--------

            # 转换union_key_list为字典union_key_dict
            union_key_dict = dict(union_key_list)
            # 把合并后缺失数据的数量小于规定数目，并且变量的数量等于round的union_key_dict的项保留
            # 保存结果到union_key_dict_deleted
            union_key_dict_deleted = {key:union_key_dict[key] for key in union_key_dict
                                  if (len(union_key_dict[key]) <= max_na_number_per_variable) and (len(key) == round)}

            # --------此处测试打印--------
            print('round: {}, length: {}'.format(round, len(union_key_dict_deleted)))
            # --------此处测试打印--------

            # 如果删除了所有的项，那么就停止循环
            if len(union_key_dict_deleted) < 1:
                break

            # 把这一轮的结果存储到selected_dataframe中
            selected_dataframe[round] = union_key_dict_deleted

        return selected_dataframe

    def select(self, max_na_number_per_variable = None):
        """ 选择器，选择平衡数据框

        :param int max_na_number_per_variable: 一个变量最多的缺失数据数
        :return: 选择的结果
        :rtype: dict
        """
        # 选择缺失数据中，缺失数据数量小于等于最大缺失数据数的数据框
        _data = self.data_with_na.loc[:,lambda df: df.sum() <= max_na_number_per_variable]

        # 重新设置行变量和列变量
        # 设置行变量
        indexes = range(_data.shape[0])
        # indexes_mapping字典（映射）：新行变量 -> 旧行变量
        indexes_mapping = dict(zip(indexes, _data.index))
        _data.index = indexes

        # 设置列变量，即变量
        # column_index字典：行变量 -> 缺失数据行变量的frozenset
        column_index = {col:frozenset(_data[col][_data[col]].index) for col in _data.columns}
        # column_index_reverse列表：（缺失数据行变量的frozenset，行变量）
        column_index_reverse = [(column_index[col],col) for col in column_index]

        # --------此处测试打印--------
        # print(len(column_index))
        # print(column_index_reverse)
        # --------此处测试打印--------

        # index_columns_dict字典：缺失数据行变量的frozenset -> 行变量列表
        index_columns_dict = defaultdict(set)
        for k, v in column_index_reverse:
            index_columns_dict[k].add(v)

        # --------此处测试打印--------
        # print(index_columns_dict.items())
        # print(len(index_columns_dict))
        # --------此处测试打印--------

        # col_variables_dict字典：行变量中的一个变量 -> 行变量列表
        col_variables_dict = {list(index_columns_dict[key])[0]:index_columns_dict[key] for key in index_columns_dict}

        # --------此处测试打印--------
        # print(col_variables_dict)
        # --------此处测试打印--------

        # 进行行变量变换
        _data = _data.loc[:, col_variables_dict.keys()]
        columns = [str(i) for i in range(_data.shape[1])]
        columns_mapping = dict(zip(columns, _data.columns))
        # columns_mapping字典（映射）：新行变量 -> 行变量列表
        columns_mapping = {key:col_variables_dict[columns_mapping[key]] for key in columns_mapping}
        _data.columns = columns

        # --------此处测试打印--------
        # print(len(_data.columns))
        # print(_data.columns)
        # print(columns_mapping)
        # --------此处测试打印--------

        # 此处测试数据输出，用于后期测试
        self.test_data = _data

        # --------此处测试打印--------
        # print(_data.columns)
        # --------此处测试打印--------

        # single_variable_false_position_dict字典：单个变量的frozenset -> 缺失数据行索引集合
        single_variable_false_position_dict = {frozenset([col]):set(_data[col][_data[col]].index)
                                               for col in _data.columns}

        # --------此处测试打印--------
        # for key in single_variable_false_position_dict:
        #     print('LETTTTTTTTTTTTTTTTTT')
        #     print(key,set(key))
        #     print(columns_mapping[set(key).pop()], [indexes_mapping[cc] for cc in single_variable_false_position_dict[key]])
        # --------此处测试打印--------

        # --------此处测试打印--------
        # print(single_variable_false_position_dict)
        # --------此处测试打印--------

        # 调用assembly方法
        selected_dataframe = BalancedDataSelector.assembly(single_variable_false_position_dict, max_na_number_per_variable)

        # 把返回的结果重新关联到原有的数据框
        _dataframe = dict()
        for i in selected_dataframe:
            _dataframe[i] = dict()
            for j in selected_dataframe[i]:
                _key = []
                for key in j:
                    _key.extend(columns_mapping[key])
                _key = frozenset(_key)
                _dataframe[i][_key] = [indexes_mapping[key] for key in selected_dataframe[i][j]]

        return _dataframe

if __name__ == '__main__':
    '''
    # data
    df = pd.DataFrame(np.random.randn(8, 6), index=range(1,9), columns=['AA', 'BB', 'CC', 'DD', 'EE', 'FF'])
    df.loc[2:6,'AA'] = None
    df.loc[7:9,'CC'] = None
    df.loc[4,'DD'] = None
    df.loc[1,'EE'] = None
    df.loc[5,'FF'] = None

    df_false = df.isnull()
    df_with_na = df_false.loc[:,df_false.any()]
    df_without_na = df_false.loc[:,~df_false.any()]

    print(df_with_na)

    '''
    F = open(r'E:\github\workrobot\workrobot\files\ceic_raw_data_year.pkl', 'rb')
    raw_data = pickle.load(F)
    df = raw_data.loc[2010]
    #df = df.iloc[0:500,0:80]
    #df = df.loc[:, ['互联网宽帶接入用户','从业人数_制造业','人口数','从业人员']]
    df_bool = df.isnull()
    #print(df_bool)

    # 创建对象
    bselector= BalancedDataSelector(data=df)

    # 调用函数
    max_na_number_per_variable = 5
    result = bselector.select(max_na_number_per_variable=max_na_number_per_variable)

    # 输出结果打印
    print('\n\n=======================result=====================')
    for i in sorted(result):
        print('Variable Numbers: {}'.format(i))
        for key in result[i]:
            print(key,' --> ',result[i][key])
        print('\n')


    #df = bselector.test_data
    # 检验
    CHECK_TIMES = 1000
    # check value
    MIN_NUMBER = len(df.index) - max_na_number_per_variable
    # variable numbers
    for i in range(CHECK_TIMES):
        # variable numbers
        number_variable_choice = random.choice(list(result.keys()))
        # 随机选择其中一项
        item_choice = random.choice(list(result[number_variable_choice]))
        print('first line\n', item_choice, result[number_variable_choice][item_choice])
        print('second line\n', df.loc[result[number_variable_choice][item_choice],list(item_choice)])
        #print(df_bool.loc[result[number_variable_choice][item_choice],list(item_choice)])
        mdata = df.loc[:,list(item_choice)]
        #mdata = df.loc[:,['互联网宽帶接入用户','从业人数_制造业','人口数','从业人员']]
        if len(mdata.dropna().index) < MIN_NUMBER:
            print(len(mdata.index),len(mdata.dropna().index),len(mdata.index)-len(mdata.dropna().index))
            print(mdata[mdata.isnull().any(axis=1)])
            print('WRONG!!!!!!')
            break

