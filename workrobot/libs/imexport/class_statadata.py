# coding=UTF-8

# -----------------------------------------------
# class_statadata文件
# @class: Statadata类
# @introduction: Statadata类用来读写stata数据文件
# @dependency: pandas
# @author: plutoese
# @date: 2016.05.19
# ------------------------------------------------

import pandas as pd


class Statadata:
    """ Statadata类用来读写stata数据文件

    :param str filename: 想要读写的文件名
    :param str encoding: 编码方式，默认是'GBK'
    :return: 无返回值
    :var list variables: 变量列表
    :var list variables_labels: 变量标签列表
    :var list variables_values_labels: 变量的值标签
    :var list values_labels: 值标签的内容
    """
    def __init__(self, filename, encoding='GBK'):
        # 读入stata数据文件
        self.stata_file = pd.read_stata(
            filename, encoding=encoding, convert_categoricals=False, iterator=True)
        # 变量
        self.variables = self.stata_file.varlist
        # 变量标签
        self.variables_labels = self.stata_file.vlblist
        # 变量值标签
        self.variables_values_labels = self.stata_file.lbllist
        # 值标签
        try:
            self.values_labels = self.stata_file.value_labels()
        except:
            self.values_labels = None

    def read(self):
        """ 读入数据

        :return: 返回.dat文件的数据
        :rtype: pd.Dataframe类
        """
        return self.stata_file.read()


if __name__ == '__main__':
    stata_file = r'D:\data\lab\cgss2013.dta'
    stdata = Statadata(stata_file)
    print(stdata.variables)
    print(stdata.variables_labels)
    print(stdata.variables_values_labels)
    print(stdata.values_labels)
