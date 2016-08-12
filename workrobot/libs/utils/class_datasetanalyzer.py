# coding=UTF-8

"""
=========================================
数据集析出类
=========================================

:Author: glen
:Date: 2016.8.6
:Tags: format conversion
:abstract: 解析数据集，析出平衡数据集

**类**
==================
DataSetAnalyzer
    数据集析出器


**使用方法**
==================


**示范代码**
==================
"""

import re
import numpy as np
import pickle
import pandas as pd
from collections import defaultdict
from copy import deepcopy
from collections import OrderedDict
from itertools import combinations, product
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection


class DataSetAnalyzer:
    """ 数据集析出类

    :param pandas.DataFrame dataframe: 数据框
    :return: 无返回值
    """
    def __init__(self, data=None, id=None, time=None):
        self._data = data
        index_name = self._data.index.names

        #if id == index_name[1]:
        #    self._data = self._data.swaplevel()

        self._id = id
        self._time = time

        self._id_values = self._data.index.get_level_values(self._id).unique()
        self._time_values = self._data.index.get_level_values(self._time).unique()
        self._variables = self._data.columns

        self._time_series_data = defaultdict()
        self._cross_section_data = defaultdict()
        self._panel_data = defaultdict()

    def generate_time_series_data(self, export_file='E:/github/workrobot/workrobot/data/ceic/timeseries/',
                                  MIN_DATA_NUM_PER_VAR=10):
        for acode in self._id_values:
            self._time_series_data = defaultdict()
            print('acode: ', acode)

            valid_variable_keys = set()
            valid_single_variables = set()
            single_variable_values = dict()

            for variable in self._variables:
                dict_key = frozenset({acode, variable})
                mdata = pd.DataFrame(raw_data.loc[acode][variable].dropna())

                if mdata.size >= MIN_DATA_NUM_PER_VAR:
                    self._time_series_data[dict_key] = mdata
                    valid_variable_keys.add(dict_key)
                    valid_single_variables.add(variable)
                    single_variable_values[variable] = mdata

            for i in range(1, len(valid_single_variables)):
                if len(valid_variable_keys) < 1:
                    break

                extend_valid_variable_keys = set()
                for valid_var in sorted(valid_single_variables):
                    for valid_key in sorted(valid_variable_keys):
                        if valid_var in valid_key:
                            continue

                        merge_data = self._time_series_data[valid_key].join(single_variable_values[valid_var]).dropna()
                        if merge_data.size >= (i+1) * MIN_DATA_NUM_PER_VAR:
                            extend_valid_key = valid_key.union({valid_var})
                            extend_valid_variable_keys.add(extend_valid_key)
                            self._time_series_data[extend_valid_key] = merge_data

                valid_variable_keys = extend_valid_variable_keys

            print(self._time_series_data)
            F = open(''.join([export_file, acode, '.pkl']),'wb')
            pickle.dump(self._time_series_data, F)

    def generate_cross_section_data(self, export_file='E:/github/workrobot/workrobot/data/ceic/crosssection/',
                                    MIN_DATA_NUM_PER_VAR=200):
        for year in self._time_values:
            self._cross_section_data = defaultdict()

            valid_variable_keys = set()
            valid_single_variables = set()
            single_variable_values = dict()

            for variable in self._variables:
                dict_key = frozenset({year, variable})
                mdata = pd.DataFrame(self._data.loc[year][variable].dropna())

                if mdata.size >= MIN_DATA_NUM_PER_VAR:
                    self._cross_section_data[dict_key] = mdata
                    valid_variable_keys.add(dict_key)
                    valid_single_variables.add(variable)
                    single_variable_values[variable] = mdata

            for i in range(1, len(valid_single_variables)):
                if len(valid_variable_keys) < 1:
                    break

                extend_valid_variable_keys = set()
                for valid_var in sorted(valid_single_variables):
                    print('year: {}, variable: {}'.format(year,valid_var))
                    for valid_key in sorted(valid_variable_keys):
                        print(valid_key )
                        if valid_var in valid_key:
                            continue

                        merge_data = self._cross_section_data[valid_key].join(single_variable_values[valid_var]).dropna()
                        if merge_data.size >= (i+1) * MIN_DATA_NUM_PER_VAR:
                            extend_valid_key = valid_key.union({valid_var})
                            extend_valid_variable_keys.add(extend_valid_key)
                            self._cross_section_data[extend_valid_key] = merge_data

                valid_variable_keys = extend_valid_variable_keys

            print(self._cross_section_data)
            F = open(''.join([export_file, str(year), '.pkl']),'wb')
            pickle.dump(self._cross_section_data, F)

    def generate_data_statistics(self, groupby=None, MIN_DATA_NUM_PER_VAR=200):
        # 分组类别：如果根据时间分组则得到横截面数据统计，如果根据横截面单位分组，则得到时间序列统计
        groupby = self._time_values

        # 数据统计变量
        _data_statistics = defaultdict()

        # group_variable是分组变量，例如时间或地区
        for group_variable in groupby[51:52]:
            # 有效的变量关键词，存储满足基本要求的组名+变量名
            valid_variable_keys = set()
            # 有效的单个变量，用来防止满足基本要求的单个变量名
            valid_single_variables = set()
            # 单个变量的值，实际放置的是它的索引
            single_variable_values = dict()

            # 首先根据变量拆分为数据集为单个变量的数据集，计算有效的数据集合
            for variable in self._variables:
                # 生成键值，包括分组变量加上变量名
                dict_key = frozenset({group_variable, variable})
                # 根据分组变量及变量名
                mdata = pd.DataFrame(self._data.loc[group_variable][variable].dropna())

                if mdata.size >= MIN_DATA_NUM_PER_VAR:
                    # 数据统计集
                    _data_statistics[dict_key] = {'select':(group_variable, tuple([variable])), 'shape':mdata.shape}
                    valid_variable_keys.add(dict_key)
                    valid_single_variables.add(variable)
                    single_variable_values[variable] = (group_variable, tuple([variable]))

            print('The number of single variable dataset is {}'.format(len(valid_single_variables)))

            # 开始进行数据集的统计
            # 最外层的循环次数是有效变量的个数-1，每次都合并原有的数据框和新的变量
            for i in range(1, len(valid_single_variables)):
                if len(valid_variable_keys) < 1:
                    break

                extend_valid_variable_keys = set()

                # 中间层的循环是有效的单个变量
                for valid_var in sorted(valid_single_variables):
                    # 最内层的循环是基于有效的变量集，每次加新变量是要更新有效的变量集
                    for valid_key in sorted(valid_variable_keys):
                        print('times: {}, group by: {}, variable: {}, valid_key: {}'.
                              format(i, group_variable, valid_var, valid_key))
                        # 如果新变量已经在有效的变量key中，那么跳过。
                        if valid_var in valid_key:
                            continue
                        print('key1: {}, key{}'.format(_data_statistics[valid_key]['select'],single_variable_values[valid_var]))
                        merge_data = pd.DataFrame(self._data.loc[_data_statistics[valid_key]['select']]).join(self._data.loc[single_variable_values[valid_var]]).dropna()

                        # 判断条件，数据集的数量
                        if merge_data.size >= (i+1) * MIN_DATA_NUM_PER_VAR:
                            extend_valid_key = valid_key.union({valid_var})
                            extend_valid_variable_keys.add(extend_valid_key)

                            select = list(_data_statistics[valid_key]['select'][1])
                            select.append(valid_var)
                            _data_statistics[extend_valid_key] = {'select':(group_variable, tuple(select)), 'shape':merge_data.shape}

                valid_variable_keys = extend_valid_variable_keys

            return _data_statistics

    def generate_data_stat(self, groupby=None, MIN_DATA_NUM_PER_VAR=200):
        # 分组类别：如果根据时间分组则得到横截面数据统计，如果根据横截面单位分组，则得到时间序列统计
        groupby = self._time_values

        # 数据统计变量
        _data_statistics = defaultdict()

        # group_variable是分组变量，例如时间或地区
        for group_variable in groupby[51:52]:
            print(self._data.loc[group_variable])


        return _data_statistics


class BalancedDataSelector:
    def __init__(self, data):
        self._data = data

        # 生成True or False矩阵，缺失数据的元素为0，其他为1
        self._bool_data = self._data.notnull()
        self._bool_false_data = self._data.isnull()

        # 所有元素都为True的子矩阵
        self._all_true_data = self._bool_data.loc[:,  self._bool_data.all()]
        # 并非所有元素都为True的子矩阵
        self._not_all_true_data = self._bool_data.loc[:, ~(self._bool_data.all())]

        self._nrows, self._ncols = self._data.shape

    def create_balanced_dataset_selector(self, min_number_per_variable=285):

        not_all_true_data = self._not_all_true_data.loc[:,lambda df: df.sum() >= min_number_per_variable]
        print('Shape of not all true data: ', not_all_true_data.shape)
        not_all_true_data_index = self._not_all_true_data.index
        last_time_dataframe = not_all_true_data
        data_stat_dict = {1: not_all_true_data.columns}
        for round in range(2, len(not_all_true_data.columns)+1):
            for row_number in range(len(not_all_true_data_index)):
                print('Round: {}, Row Number: {}'.format(round, row_number))
                origin_data = last_time_dataframe.loc[not_all_true_data_index[row_number]]
                extend_data = not_all_true_data.loc[not_all_true_data_index[row_number]]

                row_extend_data = BalancedDataSelector.variable_extends(origin_data,extend_data)
                row_extend_data.name = not_all_true_data_index[row_number]

                if row_number == 0:
                    _dataframe = pd.DataFrame(row_extend_data).T
                else:
                    _dataframe = _dataframe.append(pd.DataFrame(row_extend_data).T)

            extend_dataframe = _dataframe.loc[:,lambda df: df.sum() >= min_number_per_variable]

            columns_unique = BalancedDataSelector.unique_indexes(extend_dataframe.columns, min_number=round)
            step_dataframe = extend_dataframe.loc[:, columns_unique]
            if step_dataframe.shape[1] < 1:
                break
            last_time_dataframe = step_dataframe
            data_stat_dict[round] = step_dataframe.columns
            print('Round: {} --- The shape of new dataframe is {}.'.format(round, step_dataframe.shape))

        data_stat_dict[0] = self._all_true_data.columns

        return data_stat_dict

    @classmethod
    def variable_extends(cls, origin_data=None, extend_data=None):
        origin_index = origin_data.index
        extend_index = extend_data.index

        extends_data = np.outer(origin_data, extend_data).flatten()

        extends_data_index = ['|'.join([o_index, e_index]) for o_index in origin_index for e_index in extend_index]

        result = pd.Series(extends_data,index=extends_data_index)

        return result

    def select_more(self, min_number_per_variable=285):
        data = self._not_all_true_data.loc[:,lambda df: df.sum() >= min_number_per_variable]
        outer_columns = [frozenset([item]) for item in data.columns]
        inner_columns = [frozenset([item]) for item in data.columns]
        selected_dataframe = dict()
        selected_dataframe[0] = [frozenset(item) for item in self._all_true_data.columns]
        if len(outer_columns) > 0:
            selected_dataframe[1] = outer_columns
        for round in range(2, len(data.columns)+1):
            round_dataframe = []
            out_number = len(outer_columns)
            for out_var in outer_columns:
                inner_number = len(inner_columns)
                for inner_var in inner_columns:
                    print('Round: {} --- Outer: {} to Inner: {} # inner: {}'.format(round,out_number,inner_number,inner_var))
                    inner_number -= 1
                    _columns = deepcopy(set(out_var))
                    _columns.update(inner_var)
                    if data[list(_columns)].all(axis=1).sum() >= min_number_per_variable:
                        if len(_columns) < round:
                            continue
                        if frozenset(_columns) in set(round_dataframe):
                            continue
                        round_dataframe.append(frozenset(_columns))
                out_number -=  1
            if len(round_dataframe) < 1:
                break
            inner_columns = round_dataframe
            print('Next cycle number: {}'.format(len(inner_columns)*len(out_var)))
            selected_dataframe[round] = round_dataframe

        return selected_dataframe

    def select_more_more(self, min_number_per_variable=285):

        data = self._not_all_true_data.loc[:,lambda df: df.sum() >= min_number_per_variable]
        selected_dataframe = dict()
        if len(data.columns) > 0:
            selected_dataframe[1] = [frozenset([item]) for item in data.columns]
        dataframe_cols = [[item] for item in data.columns]
        #for round in range(1, len(data.columns)+1):
        for round in range(2, 4):
            print('number: {}'.format(round))
            round_dataframe = []
            for comb in product(dataframe_cols, data.columns):
                #print('hehehehe:', comb, set(comb), len(set(comb)), round)
                if comb[1] in comb[0]:
                    continue
                #print('comb: ', set(list(comb[0])),comb[1])
                cols = set(list(comb[0]))
                cols.add(comb[1])
                #print(cols)
                #print('66666666666666',frozenset(cols), set(round_dataframe))
                if frozenset(cols) in set(round_dataframe):
                    continue
                print(list(cols))
                if data[list(cols)].all(axis=1).sum() >= min_number_per_variable:
                    round_dataframe.append(frozenset(cols))
            if len(round_dataframe) < 1:
                break
            dataframe_cols = round_dataframe
            selected_dataframe[round] = round_dataframe

        return selected_dataframe

    def select(self, min_number_per_variable=285):
        print(self._nrows, self._ncols)
        # 设置数据框
        df_false = self._bool_false_data[self._not_all_true_data.columns]

        # 设置索引
        indexes = range(df_false.shape[0])
        indexes_mapping = dict(zip(indexes,df_false.index))
        df_false.index = indexes

        # 设置变量
        columns = [str(i) for i in range(df_false.shape[1])]
        columns_mapping = dict(zip(columns,df_false.columns))
        df_false.columns = columns


        # 容许一个变量缺失数据的数量
        max_na_number_per_variable = self._nrows - min_number_per_variable

        # 单个变量的索引表（变量：单个变量缺失值的位置）
        single_variable_false_position_dict = {frozenset(col):set(df_false[col][df_false[col]].index)
                                               for col in df_false.columns}
        print(single_variable_false_position_dict)
        selected_dataframe = dict()
        selected_dataframe[1] = single_variable_false_position_dict
        #for round in range(2, self._ncols):
        for round in range(2, 20):
            variable_dict_each_round_kept = selected_dataframe[round-1]

            union_key_list = [(frozenset(set(extend_key) | set(round_key)),single_variable_false_position_dict[extend_key].union(variable_dict_each_round_kept[round_key]))
                              for extend_key in single_variable_false_position_dict
                              for round_key in variable_dict_each_round_kept]
            print('777',len(union_key_list))

            union_key_dict = dict(union_key_list)
            print('888', len(union_key_dict))
            union_key_dict_deleted = {key:union_key_dict[key] for key in union_key_dict
                                  if (len(union_key_dict[key]) <= max_na_number_per_variable) and (len(key) == round)}
            print('999', len(union_key_dict_deleted))
            print('round: {}, length: {}'.format(round, len(union_key_dict_deleted)))
            if len(union_key_dict_deleted) < 1:
                break
            selected_dataframe[round] = union_key_dict_deleted

        return selected_dataframe


    @classmethod
    def unique_indexes(cls, indexes=None, min_number=None, split_char='\|'):
        result_indexes = []
        crititation_indexes = set()

        for item in indexes:
            if len(set(re.split(split_char,item))) < min_number:
                continue
            if not frozenset(item) in crititation_indexes:
                crititation_indexes.add(frozenset(item))
                result_indexes.append(item)

        return result_indexes


if __name__ == '__main__':
    '''
    F = open(r'E:\github\workrobot\workrobot\files\ceic_raw_data_year.pkl', 'rb')
    raw_data = pickle.load(F)
    #print(raw_data.loc[2010])

    dataset_selector = BalancedDataSelector(data=raw_data.loc[2010])
    print(dataset_selector._rowname)
    print(dataset_selector._colname)
    var_dict = dataset_selector.create_balanced_dataset_selector()

    F = open(r'E:\github\workrobot\workrobot\data\ceic\cross_section_data.pkl', 'wb')
    pickle.dump(var_dict, F)
    F.close()


    df = pd.DataFrame(np.random.randn(8, 4), index=range(1,9), columns=['A', 'B', 'C', 'D'])
    df.loc[2:6,'A'] = None
    df.loc[7:9,'C'] = None
    df.loc[4,'D'] = None
    '''
    F = open(r'E:\github\workrobot\workrobot\files\ceic_raw_data_year.pkl', 'rb')
    raw_data = pickle.load(F)
    df = raw_data.loc[2010]
    #print(raw_data.loc[2010])


    d_selector = BalancedDataSelector(data=df)
    '''
    df_true = df.notnull()
    df_false = df.isnull()
    print(df_true)
    print(df_false)
    mdict = {frozenset(col):set(df_false[col][df_false[col]].index) for col in df_false.columns}
    for key_out in mdict:
        for key_in in mdict:
            print(frozenset(set(key_out) | set(key_in)))
    new_list = [(frozenset(set(key_out) | set(key_in)),mdict[key_out].union(mdict[key_in])) for key_out in mdict for key_in in mdict]
    new_dict = dict(new_list)
    new_dict_len = {key:new_dict[key] for key in new_dict if (len(new_dict[key]) < 2) and (len(key) == 2)}
    print(len(new_list))
    print(new_dict)
    print(new_dict_len)
    '''
    print('-------------Start------------')
    result = d_selector.select(min_number_per_variable=10)
    print(len(result[1]))

    '''
    F = open(r'E:\github\workrobot\workrobot\data\ceic\cross_section_data_2010.pkl', 'wb')
    pickle.dump(result, F)
    F.close()
    '''
    '''
    pindex = result[3].columns
    lastindex = []
    newindex = set()
    for item in pindex:
        if len(set(re.split('\|',item))) < 3:
            continue
        if not frozenset(item) in newindex:
            newindex.add(frozenset(item))
            lastindex.append(item)
        print(newindex)
    print(lastindex)
    print(result[3].loc[:,lastindex])'''
