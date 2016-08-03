# coding=UTF-8

"""
=========================================
Python调用R语言类
=========================================

:Author: glen
:Date: 2016.8.2
:Tags: model R
:abstract: 主要用于对R语言的调用

**类**
==================
RActor
    创建R实例，在Python中进行R语言调用


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

import re
import numpy as np
import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.rinterface import RNULLType
from rpy2.robjects import FloatVector, IntVector, StrVector, Matrix, DataFrame, BoolVector
from libs.imexport.class_statadata import Statadata


class RActor:
    def __init__(self):
        self._R = robjects
        self._variables_in_R = dict()

    def create_variable_in_R(self, variable_name, value):
        if isinstance(value, (list, np.ndarray, pd.Series)):
            self._R.globalenv[variable_name] = RActor.python_type_to_R_type(value)
        elif isinstance(value, pd.DataFrame):
            indexes = value.index
            rownames = ''.join(["c('","','".join(list(indexes)),"')"])
            value_dict = value.to_dict('list')
            for key in value_dict:
                value_dict[key] = RActor.python_type_to_R_type(value_dict[key])
            self._R.globalenv[variable_name] = DataFrame(value_dict)
            self._R.r(''.join(['rownames(',variable_name,') <- ',rownames]))
        else:
            self._R.globalenv[variable_name] = value

    def get_variable_in_R(self, variable_name):
        """ 返回R中的一个变量

        :param str variable_name: 变量名
        :return: 无返回值
        """
        # 获得变量的值

        value, type, indexs = self._r_variable(variable_name)

        if type == 'vector':
            if len(list(value)) < 2:
                return (list(value))[0]
            return pd.Series(list(value),index=indexs[0])
        if type == 'matrix':
            return pd.DataFrame(np.matrix(value),index=indexs[0],columns=indexs[1])
        if type == 'dataframe':
            dframe = pd.DataFrame(pd.Series(list(item)) for item in value)
            dframe = dframe.T
            dframe.index = indexs[0]
            dframe.columns = indexs[1]
            return dframe

    def _r_variable(self,variable_name=None):
        """ 辅助函数，提取variable的信息

        :param variable_name:
        :return:
        """
        value = self._R.r(variable_name)
        if isinstance(value,(IntVector,FloatVector,StrVector,BoolVector)):
            type = 'vector'
            name = self._R.r(''.join(['names(',variable_name,')']))
            if isinstance(name,RNULLType):
                name = None
            else:
                name = list(name)
            return value,type,(name,)

        if isinstance(value,Matrix):
            type = 'matrix'
        if isinstance(value,DataFrame):
            type = 'dataframe'
        colnames = self._R.r(''.join(['colnames(',variable_name,')']))
        rownames = self._R.r(''.join(['rownames(',variable_name,')']))
        if isinstance(colnames,RNULLType):
            colnames = None
        else:
            colnames = list(colnames)
        if isinstance(rownames,RNULLType):
            rownames = None
        else:
            rownames = list(rownames)
        return value, type, (rownames,colnames)

    @classmethod
    def python_type_to_R_type(cls, pobject=None):
        if isinstance(pobject,(list, np.ndarray, pd.Series)):
            if isinstance(pobject,(list, pd.Series)):
                pobject = np.array(pobject)

            if re.match('^int',pobject.dtype.name) is not None:
                return IntVector(pobject)
            elif re.match('^float',pobject.dtype.name) is not None:
                return FloatVector(pobject)
            elif re.match('^str',pobject.dtype.name) is not None:
                return StrVector(pobject)
            elif re.match('^bool',pobject.dtype.name) is not None:
                return StrVector(pobject)
            else:
                return pobject
        else:
            return pobject


if __name__ == '__main__':
    d = pd.DataFrame({'one' : pd.Series([4, 5, 6, 7], index=['a', 'b', 'c', 'd']),
         'two' : pd.Series([1.2, 2.4, 3.6, 4.8], index=['a', 'b', 'c', 'd'])})
    d_dict = d.to_dict('list')
    #print(d_dict)

    '''
    dframe = dict({'one' : FloatVector([1.2, 2., 3.]),'two' : IntVector([4, 5, 6])})

    actor = RActor()
    actor.create_variable_in_R('mdata',dframe)
    value = actor.get_variable_in_R('mdata')
    print(type(value))
    dframe = pd.DataFrame(pd.Series(list(item)) for item in value)
    dframe = dframe.T
    print(dframe)'''

    x = [4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14]
    ract = RActor()
    ract.create_variable_in_R('x',x)
    print(type(ract.get_variable_in_R('x')))
    print(ract.get_variable_in_R('x'))
    print(list(ract.get_variable_in_R('x')))

    y = 'hello'
    ract.create_variable_in_R('y',y)
    print(type(ract.get_variable_in_R('y')))
    print(ract.get_variable_in_R('y'))

    d = pd.DataFrame({'one' : pd.Series([4, 5, 6, 7], index=['a', 'b', 'c', 'd']),
                      'two' : pd.Series([1.2, 2.4, 3.6, 4.8], index=['a', 'b', 'c', 'd'])})
    ract.create_variable_in_R('d',d)
    print(ract.get_variable_in_R('d'))
