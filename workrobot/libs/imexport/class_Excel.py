# coding=UTF-8

# -----------------------------------------------
# class_Excel文件
# @class: Excel类
# @introduction: Excel类用来读写Excel文件
# @dependency: xlrd, xlswriter
# @author: plutoese
# @date: 2015.10.17
# ------------------------------------------------

"""
.. code-block:: python

    filename = 'E:\\Data\\city\\variable\\m2012.xlsx'
    mexcel = Excel(filename)
    mdata = mexcel.read()
    print(mexcel.sheet)
    print(mdata)

    outfile = 'd:\\down\\demo.xlsx'
    moutexcel = Excel(outfile)
    moutexcel.new().append(mdata)
    moutexcel.close()
"""

import os
import xlrd
import xlsxwriter


class Excel:
    """ 类Excel用来读写Excel文件。

    :param str filename: 想要读写的文件名
    :return: 无返回值
    :var str filename: 文件名
    """

    def __init__(self, file_name=None):
        # 设定文件名
        self.file_name = file_name
        # 工作表
        self.sheet = None
        # Excel文件数据
        self.data = None

        self.workbook = None
        self.worksheet = None

    @property
    def sheet_names(self):
        """ 返回所有的表单名称

        :return:
        """
        with xlrd.open_workbook(self.file_name) as mfile:
            return mfile.sheet_names()

    def read(self, sheet=None):
        """读取Excel文件的数据

        :param int,str,list sheet: Excel工作表，可以使工作表号，也可以是工作表名。默认是None，代表所有的工作表。
        :return: Excel工作表中所有数据
        :rtype: list
        """
        # 连接文件
        with xlrd.open_workbook(self.file_name) as self.file:
            # 如果sheet参数是None，读取所有工作表的数据
            if sheet is None:
                self.sheet = self.file.sheets()
            else:
                self.sheet = []
                # 类型检查及设置self.sheet
                if isinstance(sheet, int):
                    self.sheet.append(self.file.sheet_by_index(sheet))
                elif isinstance(sheet, str):
                    self.sheet.append(self.file.sheet_by_name(sheet))
                elif isinstance(sheet, list):
                    if isinstance(sheet[0], int):
                        self.sheet = [self.file.sheet_by_index(
                                sheet_number) for sheet_number in sheet]
                    elif isinstance(sheet[0], str):
                        self.sheet = [self.file.sheet_by_name(
                                sheet_name) for sheet_name in sheet]
                    else:
                        print('Your sheet list is not int or str!')
                        print('Exception: ', sheet)
                        raise TypeError
                else:
                    print('Your sheet type is not int or str!')
                    print('Exception: ', sheet)
                    raise TypeError

            # 读取数据
            self.data = [single_sheet.row_values(i)
                         for single_sheet in self.sheet for i in range(single_sheet.nrows)]

            return self.data

    def new(self, file_name=None):
        """创建新的Excel文件

        :param str filename: 新文件的名称
        :return: 自身对象
        :rtype: Excel Object
        """

        # 创建Workbook对象
        if file_name is None:
            file_name = self.file_name

        self.workbook = xlsxwriter.Workbook(file_name)

        return self

    def append(self, data, sheet_name=None):
        """写入数据到Excel文件的工作表

        :param list data: 要写入Excel文件的数据
        :param str sheet_name: 工作表的名称，缺省值为Sheet1
        :return: 无返回值
        """
        # 创建工作表
        if sheet_name is None:
            self.worksheet = self.workbook.add_worksheet()
        else:
            self.worksheet = self.workbook.add_worksheet(sheet_name)

        for i in range(len(data)):
            for j in range(len(data[i])):
                self.worksheet.write(i, j, data[i][j])

    def close(self):
        """关闭Excel文件

        :return: 无返回值
        """
        self.workbook.close()


if __name__ == '__main__':
    filename = r'd:\down\citydata.xls'
    mexcel = Excel(filename)
    print(mexcel.sheet_names)
    mdata = mexcel.read()
    print(len(mdata))
    print(mexcel.sheet)
    print(mdata)

    outfile = r'd:\down\demo.xlsx'
    moutexcel = Excel(outfile)
    moutexcel.new().append(mdata, 'mysheet')
    moutexcel.close()
