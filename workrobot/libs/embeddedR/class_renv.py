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
REnv
    R语言环境，创建R实例，在Python中进行R语言调用


**使用方法**
==================


"""

import re
import numpy as np
import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.rinterface import RNULLType
from rpy2.robjects import Vector, FloatVector, IntVector, StrVector, Matrix, DataFrame, BoolVector
from libs.imexport.class_statadata import Statadata


class REnv:
    def __init__(self):
        """ 初始化R实例

        :return: 无返回值
        """
        self._R = robjects
        self._items = set()

    def __setitem__(self, key, value):
        pass

    def __getitem__(self, item):
        if isinstance(item, Vector):
            if len(np.array(item)) < 2:
                return np.array(item)[0]
            else:
                return np.array(item)
        elif isinstance(item, Matrix):
            return np.array(item)
        elif isinstance(item, DataFrame):
            pass
        else:
            print('Unknow type: ', type(item))
            raise Exception

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass


if __name__ == '__main__':
    r_env = REnv()
    print(r_env[robjects.StrVector('abc')])
    print(r_env[importr('base').pi])
    v = robjects.FloatVector([1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
    m = robjects.r['matrix'](v, nrow = 2)
    print(type(m))
    print(np.array(m))

    d = {'a': robjects.IntVector((1,2,3)), 'b': robjects.IntVector((4,5,6))}
    dataf = robjects.DataFrame(d)
    print(dataf.colnames, dataf.rownames)
    print(np.array(dataf[0]))

    data_dict = dict()
    for i in range(len(dataf.colnames)):
        data_dict[dataf.colnames[i]] = np.array(dataf[i])
    print(pd.DataFrame(data_dict))
