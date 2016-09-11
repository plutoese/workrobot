# coding=UTF-8

"""
=========================================
Python调用R语言类
=========================================

:Author: glen
:Date: 2016.8.18
:Tags: model R
:abstract: 主要用于对R语言的调用

**类**
==================
REnv
    R语言环境，创建R实例，在Python中进行R语言调用


**示范代码**
==================
::

    >>># 创建R环境
    >>>r_env = REnv()
    >>># 把R格式的数据转换为Python数据格式
    >>>print(r_env[robjects.StrVector('abc')])
    >>># 返回MongoDB中的数据库列表
    >>>print(mongo.client.database_names())
    >>># 返回MongoDB数据库中数据集合列表


"""

import numpy as np
import pandas as pd
import rpy2.robjects as robjects
from rpy2.rinterface import RNULLType
from rpy2.robjects.packages import importr
from rpy2.robjects import Vector, FloatVector, Matrix, DataFrame, ListVector, Formula, numpy2ri
from libs.imexport.class_statadata import Statadata
import rpy2.robjects.packages as rpackages


class REnv:
    def __init__(self):
        """ 初始化R实例

        :return: 无返回值
        """
        self._R = robjects

    @classmethod
    def python_to_r_object(cls, item):
        """ 把python对象转化为R对象，类方法

        :param item: Python对象，可以转换的类型有：list，tuple，pd.Series, np.ndarray, pd.DataFrame
        :return: R对象
        """
        numpy2ri.activate()
        if isinstance(item,(list, tuple, pd.Series)):
            return np.array(item)
        elif isinstance(item, pd.DataFrame):
            data_dict = {col_names: np.array(item[col_names]) for col_names in item.columns}
            rdataframe = DataFrame(data_dict)
            rdataframe.rownames = np.array(item.index)
            return rdataframe
        elif isinstance(item, (np.ndarray,bool,int,float,str)):
            return item
        else:
            print('Unsuported type: ',type(item))
            raise Exception

    def __setitem__(self, key, value):
        """ 在R进程中创建变量名为key的对象，其值为value

        :param key: 变量名
        :param value: 变量值
        :return: 无返回值
        """
        robjects.globalenv[key] = value

    def __getitem__(self, item):
        """ 获得R进程中变量的Python格式

        :param item: R进程中的变量，或者R格式的变量
        :return: Python格式的变量
        """
        # R的vector类别和numpy.array可以直接转换
        # 如果R对象是数据框（dataframe）格式，那么可以通过字典作为中间变量，转换为pandas.DataFrame
        # 如果R对象是ListVector，那么用递归方法把值保持到dict对象
        # 如果是R对象是Vector（Matrix也可以视为此类），则直接调用numpy.array
        if isinstance(item, str):
            if item in set(self._R.r.ls(self._R.globalenv)):
                item = self._R.r[item]
            else:
                print('Not a valid variable!')
                raise Exception

        if isinstance(item, DataFrame):
            column_names, indexes = item.colnames, item.rownames
            data_dict = dict()
            for i in range(len(column_names)):
                data_dict[column_names[i]] = np.array(item[i])
            pdata = pd.DataFrame(data_dict)
            pdata.index = indexes
            return pdata
        elif isinstance(item, Matrix):
            if isinstance(item.rownames, RNULLType) and isinstance(item.colnames, RNULLType):
                return pd.DataFrame(np.matrix(item))
            elif isinstance(item.rownames, RNULLType):
                return pd.DataFrame(np.matrix(item),columns=item.colnames)
            elif isinstance(item.colnames, RNULLType):
                return pd.DataFrame(np.matrix(item),index=item.rownames)
            else:
                return pd.DataFrame(np.matrix(item),index=item.rownames,columns=item.colnames)
        elif isinstance(item, ListVector):
            result = dict()
            for unit in item.names:
                if unit == 'family':
                    continue
                result[unit] = self.__getitem__(item[item.names.index(unit)])
            return result
        elif isinstance(item, Formula):
            return item.__repr__()
        elif isinstance(item, Vector):
            if len(np.array(item)) < 2:
                return np.array(item)[0]
            else:
                if isinstance(item.names, RNULLType):
                    series = pd.Series(np.array(item))
                else:
                    indexes = list(item.names)
                    if len(np.array(item)) == len(indexes):
                        series = pd.Series(np.array(item),index=indexes)
                    else:
                        series = pd.Series(np.array(item))
                return series
        elif isinstance(item, RNULLType):
            return None
        else:
            print('Unknow type: ', type(item))
            raise Exception

    @classmethod
    def numpy2ri_close(cls):
        """ 关闭R对象和numpy对象的自动转换

        :return: 无返回值
        """
        numpy2ri.activate()

if __name__ == '__main__':
    r_env = REnv()
    print(r_env[robjects.StrVector('abc')])
    print(type(r_env[robjects.StrVector('abc')]))
    print(isinstance(robjects.StrVector('abc'), DataFrame))
    print(r_env[importr('base').pi])
    v = robjects.FloatVector([1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
    m = robjects.r['matrix'](v, nrow = 2)
    print(type(m))
    print(np.array(m))
    print(r_env[m])

    d = {'a': robjects.IntVector((1,2,3)), 'b': robjects.IntVector((4,5,6))}
    dataf = robjects.DataFrame(d)
    print(isinstance(dataf,Vector))
    print(r_env[dataf])

    '''
    print('='*80)

    # 创建R形式的变量
    ctl = FloatVector([4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14])
    trt = FloatVector([4.81,4.17,4.41,3.59,5.87,3.83,6.03,4.89,4.32,4.69])

    # 调用R下的gl函数
    group = importr('base').gl(2, 10, 20, labels = ["Ctl","Trt"])
    # 注意，函数返回的也是R对象，这里group的类型是 <class 'rpy2.robjects.vectors.FactorVector'>
    weight = ctl + trt

    # 在R中创建全局变量
    robjects.globalenv["weight"] = weight
    robjects.globalenv["group"] = group
    lm_D9 = importr('stats').lm("weight ~ group")
    result = r_env[lm_D9]
    for key in result:
        print(key, ' -- ', result[key])


    print('++++++++++++++++++++++++++++++')
    print(type(r_env.python_to_r_object([1,2,3])))
    d = pd.DataFrame({'one' : [1., 2., 3., 4.],'two' : [4., 3., 2., 1.]})
    d.index = ['hello','world','OK','newbie']
    print(d)
    print(r_env.python_to_r_object(d))
    r_env['x'] = REnv.python_to_r_object(d)
    print(r_env['x'])
    print(type(r_env['x']))

    '''
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    stata_file = r'D:\data\test\wage1.dta'
    stdata = Statadata(stata_file)
    mdata = stdata.read()
    rdata = mdata[['lwage','educ','exper','tenure']]

    r_env['mdata'] = REnv.python_to_r_object(rdata)
    print(r_env['mdata'])
    lm = importr('stats').lm
    lm_obj = lm('lwage~educ+exper+tenure',data=REnv.python_to_r_object(rdata))
    print(r_env[lm_obj]['coefficients'])

    r_env.numpy2ri_close()
