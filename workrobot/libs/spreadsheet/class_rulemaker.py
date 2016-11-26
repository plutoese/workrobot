# coding = UTF-8

"""
=========================================
表单解析规则类
=========================================

:Author: glen
:Date: 2016.10.29
:Tags: rule
:abstract: 指定解析表单的规则

**类**
==================
RuleMaker
    区域匹配类

**使用方法**
==================

**示范代码**
==================

"""

import re
from libs.datasheet.class_DataSheet import DataSheet
import pandas as pd


class Rule:
    def __init__(self):
        pass

    @staticmethod
    def row_with_specified_first_word(row,specified_word=None,specified_type=float):
        if specified_type is not None:
            if isinstance(row.iloc[0],float):
                return True
            else:
                if specified_word is not None:
                    if re.match(specified_word, str(row.iloc[0])) is not None:
                        return True
                    else:
                        return False

    @staticmethod
    def row_with_only_first_item(row,specified_word=None,specified_type=None):
        if isinstance(row,pd.Series):
            if row.notnull().iloc[0] and row.iloc[1:].isnull().all():
                if specified_word is not None:
                    if re.match(specified_word,row.iloc[0]) is not None:
                        return True
                    else:
                        return False
                return True
            return False
        elif isinstance(row,list):
            pass
        else:
            print('Unkown type: ',type(row))

    @staticmethod
    def row_with_first_item_not_nan_or_numeric(row):
        return not (row.isnull().iloc[0] or Rule.is_numeric(row.iloc[0]))

    @staticmethod
    def row_with_only_first_item_above_length(row,max_length=10):
        if Rule.row_with_only_first_item(row):
            if len(row[0]) >= max_length:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def row_with_identical_item(row,specified_item_content=None):
        if isinstance(row,pd.Series):
            pass
        elif isinstance(row,list):
            if len(row) == len([item for item in row if re.match(specified_item_content,item) is not None]):
                return True
            return False
        else:
            print('Unkown type: ',type(row))

    @staticmethod
    def row_with_missing_value(row):
        if isinstance(row,pd.Series):
            return row.isnull().all()

    @staticmethod
    def row_with_not_all_missing_value(row,no_missing_type='numeric'):
        if isinstance(row,pd.Series):
            if re.match('^numeric$',no_missing_type) is not None:
                if row.notnull().any:
                    return row[row.notnull()].apply(Rule.is_numeric).any()
            else:
                return row.notnull().any()

    @staticmethod
    def row_with_all_numeric_or_nan_in_position(row,position=None):
        if isinstance(row,pd.Series):
            row_with_bool = row.apply(Rule.is_numeric_or_is_na)
            noposition = list(sorted(set(range(row_with_bool.size)) - set(position)))
            if (not row_with_bool.iloc[noposition].any()) and (row_with_bool.iloc[position].all()):
                return True
            return False
        elif isinstance(row,list):
            pass
        else:
            print('Unkown type: ',type(row))

    @staticmethod
    def row_with_any_numeric_or_nan_in_position(row,position=None):
        if isinstance(row,pd.Series):
            row_with_bool = row.apply(Rule.is_numeric_or_is_na)
            noposition = list(sorted(set(range(row_with_bool.size)) - set(position)))
            if (not row_with_bool.iloc[noposition].any()) and (row_with_bool.iloc[position].any()):
                return True
            return False
        elif isinstance(row,list):
            pass
        else:
            print('Unkown type: ',type(row))

    @staticmethod
    def is_numeric(item):
        if re.match('^-?(\d*\.)?\d+$',re.sub('\s+','',str(item))) is not None:
            return True
        return False

    @staticmethod
    def is_numeric_or_is_na(item):
        if Rule.is_numeric(item) or pd.Series(item).isnull().all():
            return True
        return False

if __name__ == '__main__':
    sheet = DataSheet(filename=r'E:\data\popcensus\origin\sample3.xlsx',sheet=0,type=1)
    rdata = sheet._rawdata
    print(rdata)

    rule = Rule()
    print(rule.row_with_identical_item(['','',''],'\s+'))

    '''
    for i in rdata.index:
        print(i,list(rdata.loc[i,]),
              rule.row_with_not_all_missing_value(rdata.loc[i]),
              rule.row_with_only_first_item(rdata.loc[i]),
              rule.row_with_all_numeric_or_nan_in_position(rdata.loc[i]),
              rule.row_with_any_numeric_or_nan_from_position(rdata.loc[i]),
              rule.row_with_not_all_missing_value(rdata.loc[i])
              )'''

    print(rule.row_with_all_numeric_or_nan_in_position(pd.Series(['新疆维吾尔自治区自治州',None,'紫葡萄']),position=[1]))
    print(rule.row_with_first_item_not_nan_or_numeric(pd.Series(['hhh',24,'hello'])))