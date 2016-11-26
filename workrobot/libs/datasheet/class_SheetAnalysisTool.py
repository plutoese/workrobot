# coding = UTF-8

"""
=========================================
表单分析工具类
=========================================

:Author: glen
:Date: 2016.11.10
:Tags: sheet analysis
:abstract: 为表单分析提供工具

**类**
==================
SheetAnalysisTool
    为表单分析提供工具

**使用方法**
==================

**示范代码**
==================

"""

from libs.datasheet.class_DataSheet import DataSheet
from libs.spreadsheet.class_rulemaker import Rule


class SheetLocator:
    def __init__(self):
        self._rule = Rule()

    def locate_title(self):
        pass

    @staticmethod
    def locate_data_column(sheet_data=None,rule='almost_data'):
        if rule == 'almost_data':
            return SheetLocator._locate_data_column_by_al(sheet_data=sheet_data)

    @staticmethod
    def locate_data_row_starter(sheet_data=None,rule='same_five'):
        if rule == 'same_five':
            return SheetLocator._locate_data_row_starter_by_sf(sheet_data=sheet_data)

    @staticmethod
    def _locate_data_column_by_al(sheet_data=None,min_percent=0.6):
        """ 通过'almost data'准则定位数据列，即如果某列数值型或缺失元素超过阈值（阈值有min_percent指定），则判断为数据列

        :param pandas.DataFrame sheet_data: 表单数据
        :param min_percent:
        :return:
        """
        data_column = []
        for i in range(sheet_data.shape[1]):
            if sheet_data.iloc[:, i].apply(Rule.is_numeric_or_is_na).sum() / sheet_data.iloc[:, i].size >= min_percent:
                data_column.append(i)
        return data_column

    @staticmethod
    def _locate_data_row_starter_by_sf(sheet_data=None,sequence=5):
        """ 定位数据行起始位置
        思想：连续行规则，即连续多行都是同样的格式，那么起始行就是第一行

        :param sequence: 连续行数
        :return:
        """
        data_start = None
        for i in range(sheet_data.index.size - sequence):
            five_rows_rdata_bool = sheet_data.iloc[i:i + sequence, ].apply(
                func=Rule.row_with_all_numeric_or_nan_in_position,
                position=SheetLocator.locate_data_column(sheet_data=sheet_data),
                axis=1)
            if five_rows_rdata_bool.all():
                if not Rule.row_with_only_first_item_above_length(sheet_data.iloc[i]):
                    data_start = i
                    break
        return data_start

if __name__ == '__main__':
    sheet = DataSheet(filename=r'E:\data\popcensus\origin\sample1.xls', sheet=0, type=1)
    rdata = sheet._rawdata
    rdata = rdata[rdata.notnull().any(axis=1)]

    print(SheetLocator.locate_data_column(rdata))
    print(SheetLocator.locate_data_row_starter(rdata))







