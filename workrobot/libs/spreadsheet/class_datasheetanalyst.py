# coding = UTF-8

"""
=========================================
表单分析器类
=========================================

:Author: glen
:Date: 2016.11.15
:Tags: sheet analysis
:abstract: 表单分析器类

**类**
==================
DataSheetAnalyst
    表单分析器类

**使用方法**
==================

**示范代码**
==================

"""

import numpy as np
import pandas as pd
from libs.region.class_regionmatcher import RegionMatchingOrderAlgorithm
from dbadmin.admindivision.class_admindivision import AdminDivision
from libs.spreadsheet.class_matcher import BulkMatcher
from libs.spreadsheet.class_rulemaker import *
from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection
from libs.spreadsheet.class_regionmatcher import RegionMatcher


class DataSheetAnalyst:
    pass


class DataSheetTransformer(DataSheetAnalyst):
    def __init__(self):
        DataSheetAnalyst.__init__(self)


class DataSheetLocator(DataSheetAnalyst):
    def __init__(self):
        DataSheetAnalyst.__init__(self)


class DataSheetExtracter(DataSheetAnalyst):
    def __init__(self):
        DataSheetAnalyst.__init__(self)


class TransformToNoBlankRowsDF(DataSheetTransformer):
    def __init__(self,dframe=None):
        DataSheetTransformer.__init__(self)
        self._dframe = dframe

    def __call__(self):
        return self._dframe[self._dframe.notnull().any(axis=1)]


class TransformToNoBlankColumnsDF(DataSheetTransformer):
    def __init__(self,dframe=None):
        DataSheetTransformer.__init__(self)
        self._dframe = dframe

    def __call__(self):
        return self._dframe.loc[:,self._dframe.notnull().any(axis=0)]


class LocateDataTableColumns(DataSheetLocator):
    def __init__(self,dframe=None,algorithm='mostlynumbers',min_percent=0.6):
        DataSheetLocator.__init__(self)
        self._dframe = dframe
        self._algorithm = algorithm
        self._min_percent = min_percent

    def __call__(self):
        if self._algorithm == 'mostlynumbers':
            return self._locate_data_column_by_al()
        else:
            return None

    def _locate_data_column_by_al(self,min_percent=0.6):
        """ 通过'almost data'准则定位数据列，即如果某列数值型或缺失元素超过阈值（阈值有min_percent指定），则判断为数据列

        :param pandas.DataFrame sheet_data: 表单数据
        :param min_percent:
        :return:
        """
        data_column = []
        for i in range(self._dframe.shape[1]):
            if self._dframe.iloc[:, i].apply(Rule.is_numeric_or_is_na).sum() / self._dframe.iloc[:, i].size >= min_percent:
                data_column.append(i)
        return data_column


class LocateDataTableRows(DataSheetLocator):
    def __init__(self,dframe=None,data_columns=None,algorithm='samefive',sequence=5,split_fn=None,**kwargs):
        DataSheetLocator.__init__(self)
        self._dframe = dframe
        self._data_columns = data_columns
        self._algorithm = algorithm
        self._sequence = sequence
        self._split_fn = split_fn
        self._kwargs = kwargs

    def __call__(self):
        if self._algorithm == 'samefive':
            start_number = LocateDataTableRows._same_five_algorithm(self._dframe,self._data_columns,sequence=5)
            end_number = LocateDataTableRows._same_five_algorithm(self._dframe,self._data_columns,reversed=True)

            data_row = [start_number]
            for i in range(start_number+1,end_number+1):
                if not self._split_fn(self._dframe.iloc[i,],**self._kwargs):
                    data_row.append(i)
            return data_row
        else:
            return None

    @staticmethod
    def _same_five_algorithm(sheet_data=None,data_columns=None,sequence=5,reversed=False):
        if reversed:
            _start = sheet_data.index.size - 1
            _end = sequence - 1
            _step = -1
            column_numbers = list(sorted(set(range(sheet_data.shape[1])) - set(data_columns)))
            if len(column_numbers) > 1:
                position = [item for item in data_columns if item < column_numbers[1]]
            else:
                position = data_columns
        else:
            _start = 0
            _end = sheet_data.index.size - sequence
            _step = 1
            position = data_columns

        data_start = None
        for i in range(_start,_end,_step):
            if reversed:
                five_row_data_sheet = sheet_data.iloc[i:i-sequence:-1,position]
            else:
                five_row_data_sheet = sheet_data.iloc[i:i+sequence,position]
            five_rows_rdata_bool = five_row_data_sheet.apply(
                func=Rule.row_with_all_numeric_or_nan_in_position,
                position=range(0,five_row_data_sheet.shape[1]),
                axis=1)

            if five_rows_rdata_bool.all():
                if not Rule.row_with_only_first_item_above_length(sheet_data.iloc[i]):
                    data_start = i
                    break

        return data_start


class LocateTitle(DataSheetLocator):
    def __init__(self,dframe=None,data_start=None,title_pre='^表?\d+'):
        DataSheetLocator.__init__(self)
        if data_start is None:
            self._dframe = dframe
        else:
            self._dframe = dframe.iloc[0:data_start,]
        self._title_pre = title_pre

    def __call__(self):
        count = 0
        row_number = self._dframe.shape[0]
        for i in range(row_number):
            if Rule.row_with_first_item_not_nan_or_numeric(self._dframe.iloc[i,]):
                if i == 0:
                    possible_title = self._dframe.iloc[i,0]
                    possible_title_number = i
                count += 1
        if count >= 1:
            if re.match(self._title_pre,possible_title) is not None:
                return possible_title_number
            else:
                #print('Can not find title!',possible_title)
                return -1
        else:
            #print('Can not find title!')
            return -1


class LocateUnit(DataSheetLocator):
    def __init__(self,dframe=None,data_start=None,unit_matcher='^单位(:|：)'):
        DataSheetLocator.__init__(self)
        if data_start is None:
            self._dframe = dframe
        else:
            self._dframe = dframe.iloc[0:data_start, ]
        self._unit_matcher = unit_matcher

    def __call__(self):
        unit_pdata = self._dframe.applymap(lambda x: re.match(self._unit_matcher, str(x)) is not None)
        possible_unit = self._dframe.loc[unit_pdata.any(axis=1), unit_pdata.any(axis=0)]

        if possible_unit.size > 0:
            return [i for i in range(unit_pdata.any(axis=1).shape[0]) if unit_pdata.any(axis=1).iloc[i]][0]

        return -1


class LocateColumnVariable(DataSheetLocator):
    def __init__(self, dframe=None, data_start=None, title_row=None, unit_row=None):
        DataSheetLocator.__init__(self)
        if data_start is None:
            self._dframe = dframe
        else:
            self._dframe = dframe.iloc[0:data_start, ]
        self._title_row = title_row
        self._unit_row = unit_row

    def __call__(self):
        column_variable_row_numbers = []
        for i in range(self._dframe.shape[0]):
            if i == self._title_row or i == self._unit_row:
                continue
            else:
                if not Rule.row_with_only_first_item(self._dframe.iloc[i]):
                    column_variable_row_numbers.append(i)
        return column_variable_row_numbers


class ExtractColumnVariable(DataSheetExtracter):
    def __init__(self, dframe=None, variable_column=None, variable_row=None):
        DataSheetExtracter.__init__(self)
        self._dframe = dframe
        self._variable_column = variable_column
        self._variable_row = variable_row

    def __call__(self):
        var_rows = self.combine_row_variable(variable_rows=self._dframe.iloc[self._variable_row,self._variable_column])
        variables = []
        for j in range(var_rows.shape[1]):
            raw_var = var_rows.iloc[:,j].str.cat(sep='_')
            variables.append(re.sub('\s+','',raw_var))
        return variables

    def combine_row_variable(self,variable_rows=None):
        if variable_rows.shape[0] == 1:
            return variable_rows

        latest = None
        start = 0
        for i in range(variable_rows.shape[1]):
            if variable_rows.iloc[0,i] is np.nan:
                if latest is not None:
                    variable_rows.values[0,i] = latest
                if i == variable_rows.shape[1] - 1:
                    variable_rows.values[1:,start:i+1] = self.combine_row_variable(variable_rows=variable_rows.iloc[1:,start:i+1])
            else:
                latest = variable_rows.iloc[0,i]
                if i > start:
                    variable_rows.values[1:,start:i] = self.combine_row_variable(variable_rows=variable_rows.iloc[1:,start:i])
                    start = i

        return variable_rows


class ExtractColumnMultiVariable(DataSheetExtracter):
    def __init__(self, column_variable=None, decomposer={'unit':('middle','\(|\)|（|）')}):
        DataSheetExtracter.__init__(self)
        self._column_variable = column_variable
        self._decomposer = decomposer

    def __call__(self):
        multi_variable = dict()
        multi_variable['variable'] = []
        if self._decomposer is None:
            return {'variable':self._column_variable}
        else:
            rest_vars = self._column_variable
            for key in self._decomposer:
                item = self._decomposer[key]
                if item[0] == 'middle':
                    mid_vars = []
                    new_rest_vars = []
                    for var in rest_vars:
                        result = ExtractColumnMultiVariable.in_the_middle(var,*item[1:])
                        if result is not None:
                            mid, rest = result
                        else:
                            mid = None
                            rest = var
                        mid_vars.append(mid)
                        new_rest_vars.append(rest)
                    multi_variable[key] = mid_vars
                    rest_vars = new_rest_vars
                if item[0] == 'theone':
                    theone_vars = []
                    new_rest_vars = []
                    for var in rest_vars:
                        result = ExtractColumnMultiVariable.is_the_one(var,*item[1:])
                        if result is not None:
                            the_one, rest = result
                        else:
                            the_one = None
                            rest = var
                        theone_vars.append(the_one)
                        new_rest_vars.append(rest)
                    multi_variable[key] = theone_vars
                    rest_vars = new_rest_vars
            # 去除变量名后不必要的_符号
            for rvar in rest_vars:
                if re.search('\_$', rvar) is not None:
                    multi_variable['variable'].append(rvar[0:-1])
                else:
                    multi_variable['variable'].append(rvar)
            # 去除multi_variable中所有值为None的键
            for to_be_deleted in [key for key in multi_variable if len(set(multi_variable[key])) == 1 and set(multi_variable[key]).pop() is None]:
                multi_variable.pop(to_be_deleted)
            return multi_variable

    @staticmethod
    def in_the_middle(var_str=None, border='\(|\)|（|）'):
        vars = re.split(border, var_str)
        if len(vars) > 1:
            punit = set(vars[slice(1,len(vars),2)])
            if len(punit) < 2:
                middle_value = punit.pop()
                rest_value = ''.join(vars[slice(0,len(vars),2)])
                return middle_value, rest_value
            else:
                print('Two many borders!')
                raise Exception
        else:
            return None

    @staticmethod
    def is_the_one(var_str=None, the_one=None):
        if re.search(the_one,var_str) is not None:
            found = re.search(the_one,var_str).group()
            rest = re.sub(found,'',var_str)
            return found, rest
        else:
            return None


if __name__ == '__main__':
    rdata = pd.read_excel(r'E:\data\citystat\transform\3_1_人口_地级市_2000.xls',sheetname=0,header=None)
    rdata = TransformToNoBlankRowsDF(dframe=rdata)()
    rdata = TransformToNoBlankColumnsDF(dframe=rdata)()
    print(rdata)
    #rdata.to_excel(r'E:\data\popcensus\origin\output1.xls')
    data_columns = LocateDataTableColumns(rdata)()
    print(data_columns)
    data_rows = LocateDataTableRows(dframe=rdata,data_columns=data_columns,
                                       split_fn=Rule.row_with_specified_first_word,specified_word='^(\d-\d)|(\d—\d)|(城市)')()
    print(data_rows)
    print(rdata.iloc[data_rows,])
    title_row = LocateTitle(dframe=rdata,data_start=data_rows[0])()
    #rdata.iloc[data_rows,].to_excel(r'E:\data\popcensus\origin\output2.xls')
    unit = LocateUnit(dframe=rdata,data_start=data_rows[0])()
    variable_rows = LocateColumnVariable(dframe=rdata,data_start=data_rows[0],title_row=title_row,unit_row=unit)()
    print(title_row,rdata.iloc[title_row,])
    print(unit)
    print(variable_rows,rdata.iloc[variable_rows,])

    column_variable = ExtractColumnVariable(dframe=rdata,variable_column=data_columns,variable_row=variable_rows)()
    print(column_variable)

    multi_variable = ExtractColumnMultiVariable(column_variable=column_variable,
                                                decomposer={'unit':('middle','\(|\)|（|）'),
                                                            'boundary':('theone','地区|市区')})()
    variable = multi_variable.get('variable')
    units = multi_variable.get('unit')
    boundary = multi_variable.get('boundary')
    print(variable,units,boundary)

    collection_variable = MonCollection(database=MonDatabase(mongodb=MongoDB(),
                                                             database_name='variable'),
                                        collection_name='referencevariable')
    refer_variables = collection_variable.find().distinct('variable')
    bmatcher = BulkMatcher(variable)
    print(bmatcher.matching(refer_variables,type='fuzzy'))

    region_columns = sorted(set(range(rdata.shape[1]))-set(data_columns))
    the_start = data_rows[0]
    the_end = None
    the_region = []
    for i in range(data_rows[0],data_rows[-1]+2):
        if i not in data_rows and the_end is None:
            the_end = i
            the_region.append(rdata.iloc[the_start:the_end,range(0,3)])
            p2 = rdata.iloc[the_start:the_end, range(3, 6)].rename(columns=dict(zip(range(3,6),range(0,3))))
            the_region.append(p2)
            the_start = None
            print(rdata.iloc[the_start:the_end,range(3,6)])
        if i in data_rows and the_start is None:
            the_start = i
            the_end = None

    m_region = pd.concat(the_region)
    m_region.to_excel(r'E:\data\citystat\transform\double.xlsx')

    origin_region = rdata.iloc[data_rows,0]

    regions = pd.DataFrame(origin_region.values, columns=['region'])
    print(regions)
    regions.to_excel(r'E:\data\citystat\transform\test.xls')


    region_matcher = RegionMatcher(regions, year=2000)
    region_matcher.place_anchor(type='match')
    region_matcher.matching_using_region_set()
    result2 = region_matcher.output_of_region_set_mapping
    result2.to_excel(r'E:\data\citystat\transform\test3.xls')
    print('Accuracy Rate: {:.2f}%.'.format(region_matcher.accuracy))
    region_matcher.matching_using_correction(r'E:\data\citystat\transform\replace.xls')
    result = region_matcher.matched_region
    print(result)
    result.to_excel(r'E:\data\citystat\transform\test6.xlsx')


