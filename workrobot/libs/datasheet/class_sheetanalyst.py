# coding = UTF-8

"""
=========================================
表单分析者类
=========================================

:Author: glen
:Date: 2016.10.29
:Tags: sheet analysis
:abstract: 对表单进行自动分析

**类**
==================
SheetAnalyst
    对表单进行自动分析

**使用方法**
==================

**示范代码**
==================

"""

import re

from libs.datasheet.class_DataSheet import DataSheet
from libs.region.class_variablematcher import VariableMatcher
from libs.spreadsheet.class_rulemaker import Rule


class SheetAnalyst:
    def __init__(self, pdata=None, source=None):
        # 表单数据的原始数据
        self._data = pdata
        # Rule对象
        self._rule = Rule()
        # 表单数据的来源，例如中国统计年鉴
        self._source = source
        # 变量匹配类
        self._variablematcher = VariableMatcher()

        # 表单的数据列位置
        self.data_column_position = None
        # 表单是否是双栏的指示变量
        self.is_double_column = False
        # 数据行起始位置
        self.data_row_start_position = None
        # 数据行终止位置
        self.data_row_end_position = None

        # 表单的标题
        self.title = None
        # 表单的单位
        self.unit = None
        self.undefind = None
        # 表单的变量列表
        self.variables = None
        # 变量相对应的单位列表
        self.units = None

    def setup(self,config_file=None):
        pass

    def run(self,info=False):
        # 第一步，分析数据列的位置
        self.data_column_position =  self.locate_data_column()
        if self._data.shape[1] - len(self.data_column_position) == 2:
            self.is_double_column = True

        # 第二步，分析数据行的位置
        self.data_row_start_position = self.locate_data_row_start()
        self.data_row_end_position = self.locate_data_row_end()

        # 第三步，根据数据行位置分拆表单
        self.pre_data_table = self._data.iloc[0:self.data_row_start_position,:]
        self.data_table = self._data.iloc[self.data_row_start_position:self.data_row_end_position+1]
        self.post_data_table = self._data.iloc[self.data_row_end_position+1:self._data.shape[0],:]

        # 第四步，解析pre_data_table
        self.pre_data_table_parser()
        
        # 第五步，解析data_table
        self.data_table_parser()

        if info:
            self.print_info()

    def print_info(self):
        start_line = '='*80
        sep_line = '-'*80

        print(start_line)
        print('表单信息初步分析结果:')
        print(sep_line)
        print('数据起始行: {}\n{}'.format(
                self.data_row_start_position,list(self._data.iloc[self.data_row_start_position])))
        print(sep_line)
        print('数据终止行: {}\n{}'.format(
                self.data_row_end_position,list(self._data.iloc[self.data_row_end_position])))
        print(sep_line)
        print(self.pre_data_table)
        print(sep_line)
        print(self.post_data_table)
        print(start_line)
        print(self.variables)
        print(start_line)
        print(self.units)
        print(start_line)

    def pre_data_table_parser(self,title_pre='^表?\d+'):
        count = 0
        row_number = self.pre_data_table.shape[0]
        unit_row_number = None
        title_row_number = None

        # 寻找title
        for i in range(row_number):
            if Rule.row_with_first_item_not_nan_or_numeric(self.pre_data_table.iloc[i,]):
                if i == 0:
                    possible_title = self.pre_data_table.iloc[i,0]
                    possible_title_number = i
                count += 1
        if count > 1:
            if re.match(title_pre,possible_title):
                self.title = possible_title
                title_row_number = possible_title_number
            else:
                print('Can not find title!',possible_title)
        else:
            print('Can not find title!')

        # 寻找单位计量
        unit_pdata = self.pre_data_table.applymap(lambda x: re.match('^单位(:|：)',str(x)) is not None)
        possible_unit = self.pre_data_table.loc[unit_pdata.any(axis=1),unit_pdata.any(axis=0)]

        if possible_unit.size > 0:
            self.unit = re.split(':|：',possible_unit.iloc[0,0])[1]
            unit_row_number = [i for i in range(unit_pdata.any(axis=1).shape[0]) if unit_pdata.any(axis=1).iloc[i]][0]

        # 寻找变量行
        undefined = []
        variable_row_numbers = []
        for i in range(self.pre_data_table.shape[0]):
            if i == title_row_number or i == unit_row_number:
                continue
            else:
                if Rule.row_with_only_first_item(self.pre_data_table.iloc[i]):
                    undefined.append(i)
                else:
                    variable_row_numbers.append(i)

        variable_rows = self.pre_data_table.iloc[variable_row_numbers]
        pd_variable = self._variablematcher.matching(variable_rows.iloc[:,self.data_column_position],unit=self.unit,
                                                     query_dict={'source':'中国人口普查'},file=r'E:\data\popcensus\origin\variable_matcher.xls')
        self.variables = list(pd_variable['matched_variable'])
        self.units = list(pd_variable['unit'])

        if len(set(self.variables)) < len(self.variables):
            if len(self.variables) == 2*len(set(self.variables)):
                self.variables = self.variables[0:len(set(self.variables))]
                self.units = self.units[0:len(set(self.units))]
            else:
                print('Not balanced variable columns!')
                raise Exception

    def data_table_parser(self):
        print(self.data_table[0:52])

    def locate_data_column(self,min_percent=0.6):
        """ 定位数据列

        :param min_percent: 数据列最低数据或NaN的比例
        :return: 返回数据列的列号
        """
        data_column = []
        for i in range(self._data.shape[1]):
            if self._data.iloc[:,i].apply(Rule.is_numeric_or_is_na).sum()/self._data.iloc[:,i].size >= min_percent:
                data_column.append(i)
        return data_column

    def locate_data_row_start(self,sequence=5):
        """ 定位数据行起始位置
        思想：连续5行规则，即连续5行都是同样的格式，那么起始行就是第一行

        :param sequence:
        :return:
        """
        data_start = None
        for i in range(self._data.index.size-sequence):
            five_rows_rdata_bool = self._data.iloc[i:i+sequence,].apply(func=Rule.row_with_all_numeric_or_nan_in_position,position=self.data_column_position,axis=1)
            if five_rows_rdata_bool.all():
                if not Rule.row_with_only_first_item_above_length(self._data.iloc[i]):
                    data_start = i
                    break
        return data_start

    def locate_data_row_end(self):
        data_end = None
        column_numbers = list(sorted(set(range(self._data.shape[1]))-set(self.data_column_position)))
        if len(column_numbers) > 1:
            position = [item for item in self.data_column_position if item < column_numbers[1]]
            last = column_numbers[1]
        else:
            position = self.data_column_position
            last = self._data.shape[1]

        for i in range(self._data.index.size-1,0,-1):
            if Rule.row_with_all_numeric_or_nan_in_position(self._data.iloc[i,0:last],position=position):
                if not Rule.row_with_only_first_item_above_length(self._data.iloc[i]):
                    data_end = i
                    break
        return data_end

if __name__ == '__main__':
    sheet = DataSheet(filename=r'E:\data\popcensus\origin\sample1.xls',sheet=0,type=1)
    rdata = sheet._rawdata
    rdata = rdata[rdata.notnull().any(axis=1)]
    #print(rdata)
    #print(rdata[rdata.notnull().any(axis=1)])
    analyst = SheetAnalyst(rdata)
    analyst.run(info=True)



