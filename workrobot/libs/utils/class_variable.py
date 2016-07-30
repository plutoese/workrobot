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
可以调用函数对变量进行变换，函数包括numpy的函数，详见http://docs.scipy.org/doc/numpy/reference/ufuncs.html


**示范代码**
==================
::

    >>># 创建pandas.DataFrame格式数据
    >>>pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    >>># 创建VariableApplyFunc对象
    >>>var_func = VariableApplyFunc(data=data, func=np.log, func_name='log', variable_names=['one'])
    >>># 调用回调函数
    >>>print(var_func())
"""

import numpy as np
import pandas as pd


class VariableApplyFunc:
    """ 对变量进行转换

    :param pd.DataFrame data: 数据
    :param function func: 函数
    :param str func_name: 函数名称
    :param list variable_names: 变量名表
    :param list new_variable_names: 新变量名表
    :param str mode: 模式，可选择'append'或'replace'
    :return: 无返回值
    """
    def __init__(self, data=None, func=None, func_name='func',
                 variable_names=None, new_variable_names = None, mode='append',
                 *args, **kwargs):
        self._data = data
        self._variable_names = variable_names
        self._func_name = func_name
        self._mode = mode
        if new_variable_names is None:
            self._new_variable_names = ['_'.join([func_name,var_name]) for var_name in variable_names]
        else:
            self._new_variable_names = new_variable_names
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        """ 回调函数

        :return: 返回变换后的数据
        :rtype: pandas.DataFrame
        """
        for i in range(len(self._variable_names)):
            if self._mode == 'append':
                self._data[self._new_variable_names[i]] = self._func(self._data[self._variable_names[i]], *self._args, **self._kwargs)
            else:
                self._data[self._variable_names[i]] = self._func(self._data[self._variable_names[i]], *self._args, **self._kwargs)

        return self._data

    def __repr__(self):
        """ 打印对象

        :return: 返回对象信息
        :rtype: str
        """
        fmt_str = '{}: {}'.format(self._mode, ','.join(self._new_variable_names))
        return fmt_str


class DelVariables:
    """ 删除变量

    :param pd.DataFrame data: 数据
    :param list variable_names: 变量名表
    :return: 无返回值
    """
    def __init__(self, data=None, variable_names=None):
        self._data = data
        self._variable_names = variable_names

    def __call__(self):
        """ 回调函数

        :return: 删除后的数据
        :rtype: pandas.DataFrame
        """
        for var_name in self._variable_names:
            del self._data[var_name]

        return self._data

    def __repr__(self):
        """ 打印对象

        :return: 返回对象信息
        :rtype: str
        """
        fmt_str = 'Deleted: {}'.format(','.join(self._variable_names))
        return fmt_str


if __name__ == '__main__':
    data = pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    var_func = VariableApplyFunc(data, np.add, 'add',['one'],None,'append',data['two'])
    print(var_func())
    print(np.log(data['one']))
    del data['one']
    print(data)





