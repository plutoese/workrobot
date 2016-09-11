# coding=UTF-8

"""
=========================================
自助法
=========================================

:Author: glen
:Date: 2016.9.5
:Tags: bootstrap R
:abstract: 自助法

**类**
==================
Bootstrap
    自助法


**使用方法**
==================


**示范代码**
==================

"""

from libs.imexport.class_statadata import Statadata
from libs.embeddedR.class_renv import REnv
import pandas as pd
from collections import OrderedDict


class Bootstrap:
    def __init__(self, data=None, func=None):
        self._Renv = REnv()

        # 导入R中的boot库
        self._Renv._R.r('library("boot")')

        # 定义函数
        self._func = '{0} <- {1}'.format('myfunc',func)
        self._Renv._R.r(self._func)

        # 导入数据
        self._Renv['data'] = REnv.python_to_r_object(data)

    def run(self, num=999, **kwargs):
        # 组合boot字符串
        boot_str = 'result <- boot(data, myfunc, R={0}'.format(num)
        for arg in kwargs:
            boot_str = ''.join([boot_str, ',' , ' {}={}'.format(arg, kwargs[arg])])
        boot_str = ''.join([boot_str, ')'])

        print(boot_str)
        # 运行自助法
        self._Renv._R.r(boot_str)

        # 取得自助法结果
        boot_data = self._Renv._R.r('result$t')
        original = self._Renv._R.r('result$t0')
        bootSE =boot_data.std(axis=0)
        bootBias = pd.DataFrame(boot_data-original).mean()

        pdict = OrderedDict()
        pdict['original'] = original
        pdict['bootSE'] = bootSE
        pdict['bootBias'] = bootBias
        return {'boot_data':boot_data, 'stat':pd.DataFrame(pdict)}


if __name__ == '__main__':
    '''
    stata_file = 'd:/data/userdata/newcity.dta'
    stdata = Statadata(stata_file)
    city_data = stdata.read()

    boot = Bootstrap(data=city_data, func='function(d, w) sum(d$x * w)/sum(d$u * w)')
    result = boot.run(stype='"w"')

    print(result['stat'])

    '''
    stata_file = 'd:/data/userdata/mtcars.dta'
    stdata = Statadata(stata_file)
    cars_data = stdata.read()

    boot = Bootstrap(data=cars_data, func='function(formula, data, indices){\n\td <- data[indices,]\n\tfit <- lm(formula, data=d)\n\treturn(coef(fit))}')
    result = boot.run(formula='mpg~wt+disp')

    print(result['stat'])

