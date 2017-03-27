# coding = UTF-8

"""
=========================================
电子表单主类
=========================================

:Author: glen
:Date: 2016.11.14
:Tags: sheet analysis
:abstract: 电子表单主类

**类**
==================
DataSheet
    电子表单主类

**使用方法**
==================

**示范代码**
==================

"""

import os
from libs.imexport.class_Excel import Excel
import pandas as pd
import re
from dbadmin.admincode.class_admindata import AdminData
from collections import OrderedDict
from libs.spreadsheet.class_datasheetanalyst import *
from libs.spreadsheet.class_rulemaker import *


class DataSheet:
    """ 类DataSheet是数据表单的主类

    """
    def __init__(self, filename=None,sheet=0,type='dataframe'):
        if type == 'list':
            self._data = Excel(filename).read(sheet=sheet)
        elif type == 'dataframe':
            self._data = pd.read_excel(filename,sheetname=sheet,header=None)
        else:
            print('Unknow type: {}'.format(type))
            raise TypeError

        self._work_flow = []
        self._location = dict()
        self._info = dict()

        self._file_name = filename
        self._path = os.path.dirname(filename)
        self._file = os.path.basename(filename)

    def add_to_work_flow(self,operation=None,run_now=True):
        self._work_flow.append(operation)
        if run_now is True:
            self.run()

    def run(self):
        for operation in self._work_flow:
            if isinstance(operation.get('operation'),DataSheetTransformer):
                self._data = operation.get('operation')()
            elif isinstance(operation.get('operation'),DataSheetLocator):
                if isinstance(operation.get('operation'),LocateDataTableColumns):
                    self._location['data_column'] = operation.get('operation')()
                if isinstance(operation.get('operation'),LocateDataTableRows):
                    self._location['data_row'] = operation.get('operation')()
                if isinstance(operation.get('operation'),LocateTitle):
                    self._location['title'] = operation.get('operation')()
                if isinstance(operation.get('operation'),LocateUnit):
                    self._location['unit'] = operation.get('operation')()
                if isinstance(operation.get('operation'),LocateColumnVariable):
                    self._location['column_variable_row'] = operation.get('operation')()
                if isinstance(operation.get('operation'),LocateOtherRows):
                    self._location['other_row'] = operation.get('operation')()
            elif isinstance(operation.get('operation'),DataSheetExtracter):
                if isinstance(operation.get('operation'),ExtractColumnVariable):
                    self._info['column_variable'] = operation.get('operation')()
                if isinstance(operation.get('operation'),ExtractColumnMultiVariable):
                    self._info.update(operation.get('operation')())
                if isinstance(operation.get('operation'),ExtractDataTableWithRowVariable):
                    self._info['data_table_with_row_variable'] = operation.get('operation')()
                if isinstance(operation.get('operation'),ExtractUnit):
                    self._info['units'] = operation.get('operation')()
                if isinstance(operation.get('operation'),ExtractTitle):
                    self._info['title'] = operation.get('operation')()
                if isinstance(operation.get('operation'),ExtractnNonNumericRow):
                    self._info['not_all_number_row'] = operation.get('operation')()
                if isinstance(operation.get('operation'),ExtractStatement):
                    self._info['statement'] = operation.get('operation')()
            elif isinstance(operation.get('operation'),DataSheetReplacer):
                if isinstance(operation.get('operation'),ReplaceRegion):
                    self._info.update(operation.get('operation')())
            elif isinstance(operation.get('operation'),DataSheetReplacer):
                if isinstance(operation.get('operation'),ReplaceRegion):
                    self._info.update(operation.get('operation')())
            elif isinstance(operation.get('operation'),DataSheetCorrector):
                if isinstance(operation.get('operation'),CorrectBoundary):
                    self._info['boundary'] = (operation.get('operation')())
                if isinstance(operation.get('operation'),CorrectNonNumericDataRow):
                    self._info['data_table_with_row_variable'] = (operation.get('operation')())
            else:
                print('undefined operation')
                raise Exception

    def output_analysis(self,generated_path=None):
        if generated_path is None:
            path = self._path
        else:
            path = generated_path
        unmatched_region = self._info.get('unmatched_region')
        if unmatched_region.size > 0:
            unmatched_region.to_excel(os.path.join(path,''.join([re.split('\.',self._file)[0],'_无法匹配区域.xlsx'])))

        auto_correction_region = self._info.get('auto_correction_region')
        if auto_correction_region.size > 0:
            auto_correction_region.to_excel(os.path.join(path,''.join([re.split('\.',self._file)[0],'_自动匹配区域.xlsx'])))

        not_all_number_row = self._info.get('not_all_number_row')
        if not_all_number_row.size > 0:
            not_all_number_row.to_excel(os.path.join(path, ''.join([re.split('\.', self._file)[0], '_非全部数字行.xlsx'])))

        other_rows = self._location.get('other_row')
        if len(other_rows) > 0:
            self._data.iloc[other_rows,:].to_excel(os.path.join(path, ''.join([re.split('\.', self._file)[0], '_其他行.xlsx'])))

        self.data_table.to_excel(os.path.join(path, ''.join([re.split('\.', self._file)[0], '_数据表格.xlsx'])))

    @property
    def data(self):
        return self._data

    @property
    def workflow(self):
        return self._work_flow

    @property
    def location(self):
        return self._location

    @property
    def info(self):
        return self._info

    @property
    def report(self):
        half_heavy_split_line = '='*50
        light_split_line = '-'*50
        title = self._info.get('title')

        # 标题
        if title is None:
            title = ''
        fmt = ''.join([half_heavy_split_line,title,half_heavy_split_line])

        fmt = ''.join([fmt, '\n', '变量: ', ', '.join(self._info.get('variable'))])
        fmt = ''.join([fmt, '\n', '单位: ', ', '.join(self._info.get('units'))])
        for item in self._info.get('units'):
            if item is None:
                fmt = ''.join([fmt, '\n', '单位中有None存在！！！！！！！'])
                break
        if self._info.get('boundary') is None:
            fmt = ''.join([fmt, '\n', '区域尺度不存在！！！！！！！'])
        else:
            fmt = ''.join([fmt, '\n', '区域范围: ', ', '.join(self._info.get('boundary'))])

        if self._info.get('statement') is None:
            fmt = ''.join([fmt, '\n', '注解不存在！！！！！！！'])
        else:
            fmt = ''.join([fmt, '\n', '注解: ', ', '.join(self._info.get('statement'))])

        unmatched_regions = list(self._info.get('unmatched_region')['region'])
        if len(unmatched_regions) > 0:
            fmt = ''.join([fmt, '\n', '无法匹配区域: ', ', '.join(unmatched_regions),'!!!!!'])

        not_all_number_row= self._info.get('not_all_number_row')
        if not_all_number_row.size > 0:
            fmt = ''.join([fmt, '\n',light_split_line, '非全部数字行', light_split_line])
            fmt = ''.join([fmt, '\n', not_all_number_row.to_string()])
        else:
            fmt = ''.join([fmt, '\n', '无非数字数据行.'])

        fmt = ''.join([fmt,'\n'])
        return fmt

    @property
    def data_table(self):
        variable = self._info.get('variable')
        units = self._info.get('units')
        boundary = self._info.get('boundary')
        region_table = self._info.get('region')
        origin_table = self._info.get('data_table_with_row_variable')
        rowvar = ['origin']
        colvar = []
        for i in range(len(variable)):
            if boundary is not None:
                colvar.append('|'.join([variable[i], units[i], boundary[i]]))
            else:
                colvar.append('|'.join([variable[i], units[i]]))
        rowvar.extend(colvar)
        origin_table.columns = rowvar
        pdata = pd.merge(region_table, origin_table, on='origin')
        return pdata

if __name__ == '__main__':
    mdatasheet = DataSheet(r'E:\data\citystat\transform\3_15_工业总产值_地级市_2000.xls',type='dataframe')
    #print(mdatasheet.data)
    mdatasheet.add_to_work_flow({'name':'删除空行','operation':TransformToNoBlankRowsDF(dframe=mdatasheet.data)})
    mdatasheet.add_to_work_flow({'name': '删除空列', 'operation': TransformToNoBlankColumnsDF(dframe=mdatasheet.data)})
    #mdatasheet.run()
    mdatasheet.add_to_work_flow({'name': '定位数据列', 'operation': LocateDataTableColumns(dframe=mdatasheet.data)})
    #mdatasheet.run()

    mdatasheet.add_to_work_flow({'name':'定位数据行', 'operation': LocateDataTableRows(dframe=mdatasheet.data,
                                                                                       data_columns=mdatasheet.location['data_column'],
                                                                                   split_fn=Rule.row_with_specified_first_word,specified_word='^(\d(-|—)\d)|(城市)')})
    #mdatasheet.run()
    mdatasheet.add_to_work_flow({'name':'定位标题行','operation':LocateTitle(dframe=mdatasheet.data,data_start=mdatasheet.location['data_row'][0])})
    #mdatasheet.run()

    mdatasheet.add_to_work_flow({'name':'定位单位行','operation':LocateUnit(dframe=mdatasheet.data,data_start=mdatasheet.location['data_row'][0])})
    mdatasheet.add_to_work_flow({'name': '定位变量行', 'operation': LocateColumnVariable(dframe=mdatasheet.data,
                                                                                    data_start=mdatasheet.location['data_row'][0],
                                                                                    title_row=mdatasheet.location['title'],
                                                                                    unit_row=mdatasheet.location['unit'])})

    mdatasheet.add_to_work_flow({'name': '定位其他行', 'operation': LocateOtherRows(dframe=mdatasheet.data,
                                                                               title_row=mdatasheet.location['title'],
                                                                               unit_row=mdatasheet.location['unit'],
                                                                               variable_row=mdatasheet.location['column_variable_row'],
                                                                               data_row=mdatasheet.location['data_row'])})

    mdatasheet.add_to_work_flow({'name': '合并变量行', 'operation': ExtractColumnVariable(dframe=mdatasheet.data,
                                                                                    variable_column=mdatasheet.location['data_column'],
                                                                                    variable_row=mdatasheet.location['column_variable_row'])})

    mdatasheet.add_to_work_flow({'name': '分解变量', 'operation': ExtractColumnMultiVariable(column_variable=mdatasheet.info['column_variable'],
                                                                                         decomposer={'unit':('middle','\(|\)|（|）'),
                                                                                                     'boundary':('theone','地区|市区')},
                                                                                         double_column=len(set(range(mdatasheet.data.shape[1]))-set(mdatasheet.location['data_column']))==2)})
    mdatasheet.add_to_work_flow({'name': '带行变量的数据表格', 'operation': ExtractDataTableWithRowVariable(dframe=mdatasheet.data,
                                                                                                   data_rows=mdatasheet.location['data_row'],
                                                                                                   data_columns=mdatasheet.location['data_column'])})

    mdatasheet.add_to_work_flow({'name': '匹配地区', 'operation': ReplaceRegion(regions=mdatasheet.info['data_table_with_row_variable'].iloc[:,0],
                                                                            year=2000, down_level=2,
                                                                            correction=r'E:\data\citystat\transform\replace.xls')})

    mdatasheet.add_to_work_flow({'name': '析出标题', 'operation': ExtractTitle(dframe=mdatasheet.data, title_row=mdatasheet.location['title'])})

    mdatasheet.add_to_work_flow({'name': '析出单位', 'operation': ExtractUnit(dframe=mdatasheet.data,unit_row=mdatasheet.location['unit'],
                                                                          units=mdatasheet.info['unit'],unit_len=len(mdatasheet.info['variable']))})

    mdatasheet.add_to_work_flow({'name': '析出注解', 'operation': ExtractStatement(dframe=mdatasheet.data,
                                                                               other_row=mdatasheet.location['other_row'],
                                                                               match_word='^\*')})

    mdatasheet.add_to_work_flow({'name': '解析非数字行', 'operation': ExtractnNonNumericRow(data_table=mdatasheet.info['data_table_with_row_variable'])})

    #mdatasheet.add_to_work_flow({'name': '纠正区域范围用词错误', 'operation': CorrectBoundary(boundary=mdatasheet.info['boundary'],
    #                                                                                boundary_correction={'地区':'全市','市区':'市辖区'},
    #                                                                                title=mdatasheet.info['title'], user_boundary=None,
    #                                                                                boundary_len=len(mdatasheet.info['variable']))})

    mdatasheet.add_to_work_flow({'name': '纠正非数字行', 'operation': CorrectNonNumericDataRow(data_table=mdatasheet.info['data_table_with_row_variable'],
                                                                                         non_numeric_data_index=mdatasheet.info['not_all_number_row'].index,
                                                                                         replace={'．':'.'})})

    mdatasheet.add_to_work_flow({'name': '解析非数字行', 'operation': ExtractnNonNumericRow(data_table=mdatasheet.info['data_table_with_row_variable'])})

    '''
    for info in mdatasheet.location:
        print('-'*80)
        print(info)
        #print(mdatasheet.location[info])
        print('='*80)

    for info in mdatasheet.info:
        print('-'*80)
        print(info)
        #print(mdatasheet.info[info])
        print('='*80)'''

    mdatasheet.output_analysis()
    print(mdatasheet.report)
