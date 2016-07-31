# coding=UTF-8

"""
=========================================
模型基础类
=========================================

:Author: glen
:Date: 2016.7.30
:Tags: model
:abstract: 模型基础类，主要用于被继承

**类**
==================
BasicModel
    创建基础模型类，用于继承


**使用方法**
==================


**示范代码**
==================
::

    >>># 创建pandas.DataFrame格式数据
    >>>pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    >>># 创建VariableApplyFunc对象
    >>>var_func = VariableCreator(data=data, func=np.log, name='log', variable_names=['one'])
    >>># 调用回调函数
    >>>print(var_func())
"""

import numpy as np
import pandas as pd
from collections import OrderedDict

class BasicModel:
    """ 创建基础模型

    :param pd.DataFrame data: 数据
    :param function func: 函数
    :param str func_name: 函数名称
    :param list variable_names: 变量名表
    :param list new_variable_names: 新变量名表
    :param str mode: 模式，可选择'append'或'replace'
    :return: 无返回值
    """
    def __init__(self, data=None, name='model',*args, **kwargs):
        self._data = data
        self._name = name
        self._args = args
        self._kwargs = kwargs

        self._result = OrderedDict()

    def __call__(self):
        """ 回调函数

        :return: 返回变换后的数据
        :rtype: pandas.DataFrame
        """

        return self._result

    def __repr__(self):
        """ 打印对象

        :return: 返回对象信息
        :rtype: str
        """
        fmt_str = 'Model Name: {}'.format(self.name)
        return fmt_str

    @property
    def name(self):
        """ 返回对象的名称

        :return: 返回对象的名称
        """
        return self._name

    @property
    def statistics(self):
        return self._result.keys()


class Describe(BasicModel):
    def __init__(self, data=None, name='describe',*args, **kwargs):
        super().__init__(data=data, name=name, *args, **kwargs)

    def __call__(self):
        self._result['summary'] = self._data.describe()
        return self._result

    def __repr__(self):
        fmt_str = 'Model Name: {}'.format(self.name)
        fmt_str = fmt_str + '\n' + self._result['summary'].__repr__()
        return fmt_str

if __name__ == '__main__':
    data = pd.DataFrame({'one' : pd.Series([1., 2., 3., 6.], index=['a', 'b', 'c', 'd']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})
    print(type(data.describe()))
    des = Describe(data)
    result = des()
    print(des)
    print(list(des.statistics))




