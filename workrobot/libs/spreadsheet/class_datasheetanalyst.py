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


class DataSheetReplacer(DataSheetAnalyst):
    def __init__(self):
        DataSheetAnalyst.__init__(self)


class DataSheetCorrector(DataSheetAnalyst):
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
            #print(five_row_data_sheet,five_rows_rdata_bool)
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
            if re.match(self._title_pre,possible_title.lstrip()) is not None:
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
        unit_pdata = self._dframe.applymap(lambda x: re.match(self._unit_matcher, re.sub('\s+','',str(x))) is not None)
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


class LocateOtherRows(DataSheetLocator):
    def __init__(self,dframe=None, title_row=None, unit_row=None, variable_row=None, data_row=None):
        DataSheetLocator.__init__(self)
        self._dframe = dframe
        self._title_row = title_row
        self._unit_row = unit_row
        self._variable_row = variable_row
        self._data_row = data_row

    def __call__(self):
        ind = set(range(self._dframe.shape[0]))
        if self._title_row > -1:
            ind = ind - set([self._title_row])
        if self._unit_row > -1:
            ind = ind - set([self._unit_row])

        ind = ind - set(self._variable_row)
        ind = ind - set(self._data_row)

        return sorted(list(ind))


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
    def __init__(self, column_variable=None, decomposer={'unit':('middle','\(|\)|（|）')}, double_column=False):
        DataSheetExtracter.__init__(self)
        self._column_variable = column_variable
        self._decomposer = decomposer
        self._double_column = double_column

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
                    #print('res',rest_vars)
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
                    multi_variable['variable'].append('_'.join([item for item in re.split('\_+',rvar) if len(item) > 0]))
                else:
                    multi_variable['variable'].append(rvar)
            # 去除multi_variable中所有值为None的键
            for to_be_deleted in [key for key in multi_variable if len(set(multi_variable[key])) == 1 and set(multi_variable[key]).pop() is None]:
                multi_variable.pop(to_be_deleted)
            if self._double_column:
                for key in multi_variable:
                    multi_variable[key] = multi_variable[key][0:int(len(multi_variable[key])/2)]
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
            elif len(punit) < 3:
                state = None
                for item in punit:
                    if re.search('不变价$',re.sub('\s+','',str(item))) is not None:
                        state = re.sub('\s+','',str(item))
                    else:
                        start_unit = re.sub('\s+','',str(item))
                if state is None:
                    print('Two many borders!')
                    raise Exception
                else:
                    middle_value = start_unit
                    rest_value = ''.join(vars[slice(0, len(vars), 2)])
                    rest_value = '{}({})'.format(rest_value,state)
                    return middle_value, rest_value
            else:
                print('ppp',punit)
                print('Two many borders!')
                raise Exception
        else:
            return None

    @staticmethod
    def is_the_one(var_str=None, the_one=None):
        if re.search(the_one,var_str) is not None:
            found = re.search(''.join([the_one,'$']),var_str).group()
            rest = re.sub(found,'',var_str)
            return found, rest
        else:
            return None


class ExtractDataTableWithRowVariable(DataSheetExtracter):
    def __init__(self, dframe=None, data_rows=None, data_columns=None):
        DataSheetExtracter.__init__(self)
        self._dframe = dframe
        self._data_rows = data_rows
        self._data_columns = data_columns
        self._row_variable_column = sorted(list(set(range(self._dframe.shape[1]))-set(self._data_columns)))
        self._double_column = len(self._row_variable_column)==2

    def __call__(self):
        if self._double_column:
            the_start = self._data_rows[0]
            the_end = None
            the_region = []
            for i in range(self._data_rows[0], self._data_rows[-1] + 2):
                if i not in self._data_rows and the_end is None:
                    the_end = i
                    the_region.append(self._dframe.iloc[the_start:the_end, range(self._row_variable_column[0], self._row_variable_column[1])])
                    p2 = self._dframe.iloc[the_start:the_end,
                         range(self._row_variable_column[1], self._dframe.shape[1])].rename(columns=dict(zip(range(self._row_variable_column[1], self._dframe.shape[1]),
                                                                                                             range(self._row_variable_column[0], self._row_variable_column[1]))))
                    the_region.append(p2)
                    the_start = None
                if i in self._data_rows and the_start is None:
                    the_start = i
                    the_end = None

            pdata = pd.concat(the_region)
            return pdata[pdata.notnull().any(axis=1)]
        else:
            return self._dframe.iloc[self._data_rows,]


class ExtractTitle(DataSheetExtracter):
    def __init__(self, dframe=None, title_row=-1):
        DataSheetExtracter.__init__(self)
        self._dframe = dframe
        self._title_row = title_row

    def __call__(self):
        if self._title_row == -1:
            return None

        return self._dframe.iloc[self._title_row,0]


class ExtractUnit(DataSheetExtracter):
    def __init__(self, dframe=None, unit_row=-1, units=None, unit_len=None):
        DataSheetExtracter.__init__(self)
        self._dframe = dframe
        self._unit_row = unit_row
        self._units = units
        self._unit_len = unit_len

    def __call__(self):
        if self._unit_row == -1:
            return self._units

        for item in self._dframe.iloc[self._unit_row, :]:
            item = re.sub('\s+','',str(item))
            if re.match('单位(:|：)', str(item)) is not None:
                general_unit = (re.split('(:|：)', str(item))[2])

        units = []
        if self._units is not None:
            for item in self._units:
                if item is None:
                    units.append(general_unit)
                else:
                    units.append(item)
            return units
        else:
            return [general_unit] * self._unit_len


class ReplaceRegion(DataSheetReplacer):
    def __init__(self, regions=None, year=None, top_level=1, down_level=3, correction=None):
        DataSheetReplacer.__init__(self)
        self._regions = regions
        self._year = year
        self._top_level = top_level
        self._down_level = down_level
        self._correction = correction

        if isinstance(regions,(list,tuple)):
            self._to_be_matched = pd.DataFrame(self._regions, columns=['region'])
        elif isinstance(regions,pd.Series):
            self._to_be_matched = pd.DataFrame(self._regions.values, columns=['region'])
        elif isinstance(regions,pd.DataFrame):
            self._to_be_matched = pd.DataFrame(self._regions[0].values, columns=['region'])
        else:
            print('Unsupported Type',type(regions))
            raise Exception

    def __call__(self):
        region_matcher = RegionMatcher(self._to_be_matched, year=self._year,
                                       top_level=self._top_level, down_level=self._down_level)
        region_matcher.place_anchor(type='match')
        #region_matcher.output_of_region_set_mapping.to_excel(r'E:\data\citystat\generated\test.xlsx')
        region_matcher.matching_using_region_set()
        if self._correction is not None:
            region_matcher.matching_using_correction(self._correction)
        return {'region':region_matcher.matched_region,
                'unmatched_region':region_matcher.not_matched_region,
                'auto_correction_region':region_matcher.auto_correction(),
                'region_map':region_matcher.output_of_region_set_mapping}


class ExtractnNonNumericRow(DataSheetExtracter):
    def __init__(self, data_table=None):
        DataSheetExtracter.__init__(self)
        self._data_table = data_table

    def __call__(self):
        return self._data_table[~self._data_table.iloc[:, 1:].applymap(Rule.is_numeric_or_is_na).all(axis=1)]


class ExtractStatement(DataSheetExtracter):
    def __init__(self, dframe=None, other_row=-1, match_word=None):
        DataSheetExtracter.__init__(self)
        self._dframe = dframe
        self._other_row = other_row
        self._match_word = match_word

    def __call__(self):
        statement = []
        for i in self._other_row:
            if re.match(self._match_word,str(self._dframe.iloc[i,0])) is not None:
                statement.append(re.sub('\s+','',str(self._dframe.iloc[i,0])))
        if len(statement) < 1:
            return None
        elif len(statement) < 2:
            return statement
        else:
            return statement


class CorrectBoundary(DataSheetCorrector):
    def __init__(self, boundary=None,boundary_correction={'地区':'全市','市区':'市辖区','建成区':'建成区'},
                 title=None, user_boundary=None, boundary_len=None):
        DataSheetCorrector.__init__(self)
        self._boundary = boundary
        self._boundary_correction=boundary_correction
        self._title = title
        self._user_boundary = user_boundary
        self._boundary_len = boundary_len

    def __call__(self):
        boundary = self._boundary
        #print(boundary)
        if boundary is not None:
            for i in range(len(boundary)):
                if re.sub('\s+','',str(boundary[i])) in self._boundary_correction:
                    boundary[i] = self._boundary_correction[re.sub('\s+','',str(boundary[i]))]
            for item in boundary:
                if item not in self._boundary_correction.values():
                    print('{} not qualified!!!'.format(item))
                    raise Exception
        else:
            title = self._title
            split_title = re.split('\(',title)
            if len(split_title) > 1:
                for item in split_title[1:]:
                    if re.split('\)', item)[0] == '不包括市辖县':
                        boundary = ['市辖区'] * self._boundary_len
                        break
                    if re.split('\)', item)[0] == '包括市辖县':
                        boundary = ['全市'] * self._boundary_len
                        break
                    if re.split('\)', item)[0] == '全市':
                        boundary = ['全市'] * self._boundary_len
                        break
                    if re.split('\)', item)[0] == '市辖区':
                        boundary = ['市辖区'] * self._boundary_len
                        break
                if boundary is None:
                    if self._user_boundary is not None:
                        boundary = [self._user_boundary] * self._boundary_len
                    else:
                        print('boundary is not Exist!!!!!')
                        raise Exception
            else:
                if self._user_boundary is not None:
                    boundary = [self._user_boundary] * self._boundary_len
                else:
                    print('boundary is not Exist!!!!!')
                    raise Exception

        return boundary


class CorrectNonNumericDataRow(DataSheetCorrector):
    def __init__(self, data_table=None, replace=None):
        DataSheetCorrector.__init__(self)
        self._data_table = data_table
        self._replace = replace

    def __call__(self):
        data_table = self._data_table
        for key in self._replace:
            data_table = data_table.applymap(lambda x: re.sub(key,self._replace[key],str(x)))

        return data_table


if __name__ == '__main__':
    rdata = pd.read_excel(r'E:\data\citystat\transform\01.xls',sheetname=0,header=None)
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
    print('hhhh',title_row,rdata.iloc[title_row,])
    print(unit)
    print(variable_rows,rdata.iloc[variable_rows,])

    column_variable = ExtractColumnVariable(dframe=rdata,variable_column=data_columns,variable_row=variable_rows)()
    print(column_variable)

    multi_variable = ExtractColumnMultiVariable(column_variable=column_variable,
                                                decomposer={'unit':('middle','\(|\)|（|）'),
                                                            'boundary':('theone','地区|市区')},
                                                double_column=len(set(range(rdata.shape[1]))-set(data_columns))==2)()
    variable = multi_variable.get('variable')
    units = multi_variable.get('unit')
    boundary = multi_variable.get('boundary')
    print(variable,units,boundary)
    print(len(set(range(rdata.shape[1]))-set(data_columns))==1,sorted(list(set(range(rdata.shape[1]))-set(data_columns))))
    print(rdata.shape[1])

    data_table_with_row_var = ExtractDataTableWithRowVariable(dframe=rdata,data_rows=data_rows,data_columns=data_columns)()
    print(data_table_with_row_var)
    data_table_with_row_var.to_excel(r'E:\data\citystat\transform\double1.xlsx')
    print(unit,units)
    final_units = ExtractUnit(dframe=rdata,unit_row=unit,units=units)()
    print(final_units)

    region_data = ReplaceRegion(regions=data_table_with_row_var.iloc[:,0],year=2000,down_level=2,
                                correction=r'E:\data\citystat\transform\replace.xls')()
    print(region_data)
    region_data.get('region_map').to_excel(r'E:\data\citystat\transform\region_map.xlsx')

    rowvar = ['origin']
    colvar = []
    for i in range(len(variable)):
        colvar.append('|'.join([variable[i],final_units[i],boundary[i]]))
    rowvar.extend(colvar)
    data_table_with_row_var.columns = rowvar
    pdata = pd.merge(region_data.get('region'),data_table_with_row_var,on='origin')
    pdata.to_excel(r'E:\data\citystat\transform\pdata.xlsx')

    rrow = data_table_with_row_var[~data_table_with_row_var.iloc[:,1:].applymap(Rule.is_numeric_or_is_na).all(axis=1)]


    '''
    print(pd.DataFrame(data_table_with_row_var.iloc[:,0].values, columns=['region']))
    region_matcher = RegionMatcher(pd.DataFrame(data_table_with_row_var.iloc[:,0].values, columns=['region']), year=2010, down_level=2)
    region_matcher.place_anchor(type='match')
    region_matcher.matching_using_region_set()
    result2 = region_matcher.output_of_region_set_mapping
    result2.to_excel(r'E:\data\citystat\transform\test3.xls')
    print(region_matcher.not_matched_region)
    region_matcher.matched_region.to_excel(r'E:\data\citystat\transform\test6.xlsx')
    region_matcher.not_matched_region.to_excel(r'E:\data\citystat\transform\replace1.xlsx')
    print(region_matcher.auto_correction())
    region_matcher.matching_using_correction(correction=r'E:\data\citystat\transform\replace.xls')
    region_matcher.matched_region.to_excel(r'E:\data\citystat\transform\final.xlsx')

    collection_variable = MonCollection(database=MonDatabase(mongodb=MongoDB(),
                                                             database_name='variable'),
                                        collection_name='referencevariable')
    refer_variables = collection_variable.find().distinct('variable')
    bmatcher = BulkMatcher(variable)
    print(bmatcher.matching(refer_variables,type='fuzzy',error_percent=0.4))

    region_columns = sorted(set(range(rdata.shape[1]))-set(data_columns))
    print(region_columns)
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
            #print(rdata.iloc[the_start:the_end,range(3,6)])
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
    #region_matcher.matching_using_correction(r'E:\data\citystat\transform\replace.xls')
    result = region_matcher.matched_region
    print(result)
    result.to_excel(r'E:\data\citystat\transform\test6.xlsx')'''


