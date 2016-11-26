# coding=UTF-8

# -----------------------------------------------
# class_winexcel文件
# @class: WinExcel类
# @introduction: WinExcel类用win32来读写Excel文件
# @dependency: win32com
# @author: plutoese
# @date: 2016.05.12
# ------------------------------------------------

import win32com.client


class WinExcel:
    """ WinExcel类用win32来读写Excel文件

    :param str filename: 想要读写的文件名
    :return: 无返回值
    :var str filename: 文件名
    """

    def __init__(self, file_name=None):
        # Excel程序
        self.excel = win32com.client.Dispatch('Excel.Application')
        # 设定文件名
        self.file_name = file_name
        # 导入Excel文件
        self.workbook = self.excel.Workbooks.open(self.file_name)
        # 工作表数量
        self.number_of_sheets = self.workbook.Sheets.Count - 1
        # Excel文件数据
        self.data = None

    def read(self):
        result = []
        for i in range(self.number_of_sheets):
            sheet = self.workbook.Sheets[i]
            # 行数
            row_number = sheet.UsedRange.Rows.Count
            # 列数
            column_number = sheet.UsedRange.Columns.Count
            result.extend(sheet.Range(sheet.Cells(1,1),sheet.Cells(row_number,column_number)).Value)
        return result

    def close(self):
        self.workbook.Close()

if __name__ == '__main__':
    filename = r'E:\data\procedure\Process\reduction\data\2005_prefecture\2_41_环境投资额_全市_地级市_2005.xls'
    #filename = r'E:\data\procedure\Process\reduction\data\1999_prefecture\3_24_劳动工资_地级市_1999.xls'
    mexcel = WinExcel(filename)
    print(mexcel.number_of_sheets)
    print(mexcel.read())
    print(len(mexcel.read()))
    mexcel.close()

