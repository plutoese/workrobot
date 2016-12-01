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
            elif isinstance(operation.get('operation'),DataSheetExtracter):
                if isinstance(operation.get('operation'),ExtractColumnVariable):
                    self._info['column_variable'] = operation.get('operation')()
                if isinstance(operation.get('operation'),ExtractColumnMultiVariable):
                    self._info.update(operation.get('operation')())
                if isinstance(operation.get('operation'),ExtractDataTableWithRowVariable):
                    self._info['data_table_with_row_variable'] = operation.get('operation')()
            else:
                print('undefined operation')
                raise Exception

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

if __name__ == '__main__':
    mdatasheet = DataSheet(r'E:\data\citystat\transform\01.xls',type='dataframe')
    #print(mdatasheet.data)
    mdatasheet.add_to_work_flow({'name':'删除空行','operation':TransformToNoBlankRowsDF(dframe=mdatasheet.data)})
    mdatasheet.add_to_work_flow({'name': '删除空列', 'operation': TransformToNoBlankColumnsDF(dframe=mdatasheet.data)})
    #mdatasheet.run()
    mdatasheet.add_to_work_flow({'name': '定位数据列', 'operation': LocateDataTableColumns(dframe=mdatasheet.data)})
    #mdatasheet.run()

    mdatasheet.add_to_work_flow({'name':'定位数据行', 'operation': LocateDataTableRows(dframe=mdatasheet.data,
                                                                                       data_columns=mdatasheet.location['data_column'],
                                                                                   split_fn=Rule.row_with_specified_first_word,specified_word='^(\d-\d)|(城市)')})
    #mdatasheet.run()
    mdatasheet.add_to_work_flow({'name':'定位标题行','operation':LocateTitle(dframe=mdatasheet.data,data_start=mdatasheet.location['data_row'][0])})
    #mdatasheet.run()

    mdatasheet.add_to_work_flow({'name':'定位单位行','operation':LocateUnit(dframe=mdatasheet.data,data_start=mdatasheet.location['data_row'][0])})
    mdatasheet.add_to_work_flow({'name': '定位变量行', 'operation': LocateColumnVariable(dframe=mdatasheet.data,
                                                                                    data_start=mdatasheet.location['data_row'][0],
                                                                                    title_row=mdatasheet.location['title'],
                                                                                    unit_row=mdatasheet.location['unit'])})

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

    print(mdatasheet.location)
    print(mdatasheet.info)

