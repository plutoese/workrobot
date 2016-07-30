# coding=UTF-8

"""
=========================================
变量处理类
=========================================

:Author: glen
:Date: 2016.7.29
:Tags: variable
:abstract: 对创建、转换和删除数据集中的变量

**类**
==================
LogVariable
    对变量进行对数变换


**使用方法**
==================


**示范代码**
==================
::

    >>># 创建MongoDBToPandasFormat对象
    >>>mongoconverter = MongoDBToPandasFormat(cursor)
    >>># 连接MongoDB中的数据库
    >>>result = mongoconverter(values='value', index=['year'], columns='variable',dropna=True)
"""

import numpy as np
import pandas as pd


class LogVariable:
    """ 对变量取对数

    :param pd.DataFrame data: 数据
    :param str variables: 变量名
    :param str name: 方法名
    :return: 无返回值
    """
    def __init__(self, data=None, variables=None, name='Log transform',
                 mode='replace', new_variables = None):
        self._data = data
        self._variables = variables
        self._name = name
        self._mode = mode
        self._new_variables = new_variables

    def __call__(self):
        """ 回调函数

        :return: 返回对数变换后的数据
        :rtype: pandas.DataFrame
        """
        if self._mode == 'replace':
            self._data[self._variables] = self._data[self._variables].applymap(np.log)
        elif self._mode == 'append':
            for i in range(len(self._variables)):
                if self._new_variables is None:
                    self._data['_'.join(['log',self._variables[i]])] = self._data[self._variables[i]].apply(np.log)
                else:
                    self._data[self._new_variables[i]] = self._data[self._variables[i]].apply(np.log)
        else:
            print('Unknown Mode!')
            raise Exception

        return self._data

    def __repr__(self):
        """ 打印对象

        :return: 返回对象信息
        :rtype: str
        """
        fmt_str = '{}: {}'.format(self._name, ','.join(self._variables))
        return fmt_str


if __name__ == '__main__':
    d = pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    d.insert(len(d.columns),'three',[8,8,8,8])
    print(d)
    logv = LogVariable(d)

    print(d[['one','two']])
    d[['one','two']] = d[['one','two']].apply(np.log)
    print(d)





