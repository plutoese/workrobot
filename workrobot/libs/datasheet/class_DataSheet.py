# coding=UTF-8

from libs.imexport.class_Excel import Excel
import pandas as pd
import re
from dbadmin.admincode.class_admindata import AdminData
from collections import OrderedDict

# 处理DataSheet的主类，用来被继承。
# 可以导出DataSet类，有序字典格式


class DataSheet:
    """ 类DataSheet是数据表单的主类，用以被继承。

    """
    def __init__(self, filename=None,sheet=None,type=None):
        if type is None:
            self._rawdata = Excel(filename).read(sheet=sheet)
        else:
            self._rawdata = pd.read_excel(filename,sheetname=sheet,header=None)

    @property
    def data(self):
        return self._data

    @staticmethod
    def is_blank_row(row):
        row_unique_data = set(row)
        for item in row_unique_data:
            if re.match('^\s*$',str(item)) is None:
                return False
        return True

    @staticmethod
    def is_title(row,row_number=None,first_characters='表\d+'):
        if row_number is not None:
            if row_number == 1:
                return True
            else:
                return False
        else:
            if re.match('^{}'.format(first_characters),row[0]) is not None:
                return True
            else:
                return False

    @staticmethod
    def is_data_row(row,type=0,between_data_table=False):
        """ 判断是否是数据行

        :param list row: 数据行
        :param type: 数据行类型, type=1表示全数据类型，type=2表示第一列是地区或变量，其余是数据，type=0,表示自动判断
        :return:
        """
        if between_data_table:
            if DataSheet.is_blank_row(row):
                return False
            else:
                return True
        else:
            head, *rest = row
            rest = set(rest)
            if re.match('^\s*$',head) is None:
                for item in rest:
                    if isinstance(item,(int,float)):
                        return True
                return False
            else:
                return False

    @staticmethod
    def match_for_region(region,year):
        admin_data = AdminData(year=year)
        region = [re.sub('\s+','',item) for item in region]
        result = admin_data[tuple(region)]
        if result is not None:
            if len(region) < 2:
                return [result[0].get('region'),result[0]]
            elif len(region) < 3:
                return [region[0],result[0].get('region'),result[0]]
            else:
                return [region[0],region[1],result[0].get('region'),result[0]]
        else:
            if len(region) < 2:
                return None
            elif len(region) < 3:
                return DataSheet.match_for_region(region=region[1:],year=year)
            else:
                return DataSheet.match_for_region(region=[region[0],region[2]],year=year)

    @staticmethod
    def match_for_regions(regions,year):
        regions_map = OrderedDict()
        region_one_round = []

        for region in regions:
            if len(region_one_round) > 2:
                region_one_round[len(region_one_round)-1] = region
            else:
                region_one_round.append(region)

            result = DataSheet.match_for_region(region_one_round,year)
            if result is not None:
                regions_map[region] = (result[-1].get('region'),result[-1].get('acode'),result[-1].get('_id'))
                region_one_round = result[:-1]
            else:
                print('Can not found: {} {}'.format(' '.join(region_one_round),region))
                regions_map[region] = None

        return regions_map

if __name__ == '__main__':
    mdatasheet = DataSheet(r'E:\data\popcensus\origin\TABLE1.xls')
    #for row in mdatasheet._rawdata:
    #    print(DataSheet.is_blank_row(row),DataSheet.is_title(row),DataSheet.is_data_row(row),row)

    result = DataSheet.match_for_region(['吉林省','浑江区'],'2010')
    if result is not None:
        print(result)