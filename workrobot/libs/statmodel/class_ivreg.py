# coding=UTF-8

"""
=========================================
回归分析——工具变量法
=========================================

:Author: glen
:Date: 2016.8.19
:Tags: regression iv
:abstract: 用iv进行回归分析

**类**
==================
IV
    用工具变量进行回归分析的主类


**使用方法**
==================


**示范代码**
==================

"""

import re
from copy import deepcopy
from rpy2.robjects import Formula
from libs.utils.class_basicmodel import BasicModel
from libs.imexport.class_statadata import Statadata
from libs.embeddedR.class_renv import REnv, importr


class IVReg(BasicModel):
    def __init__(self, data=None, name='IV regression', formula=None, var_transform=False, *args, **kwargs):
        super().__init__(data=data, name=name, *args, **kwargs)

        # 创建REnv实例
        self._renv = REnv()
        # 创建公式
        self._formula = formula
        # 原始公式
        self._origin_formula = self._formula
        self._copy_data = deepcopy(data)

        # 转换变量，特别是那些变量是中文的
        self._var_transform = var_transform
        if self._var_transform:
            self._variables_mapping = [(self._copy_data.columns[i],'_'.join(['var',str(i)]))
                                      for i in range(len(self._copy_data.columns))]
            self._variables_mapping_dict = dict(self._variables_mapping)
            self._variables_mapping_dict_reversed = dict([('_'.join(['var',str(i)]),self._copy_data.columns[i]) for i in range(len(self._copy_data.columns))])
            self._generated_variables = [item[1] for item in self._variables_mapping]
            self._copy_data.columns = self._generated_variables
            for key in self._variables_mapping_dict:
                self._formula = re.sub(key,self._variables_mapping_dict[key],self._formula)

        # self._formula = Formula(self._formula)

        self._ivreg = importr('AER').ivreg
        self._summary = importr('base').summary

    def __call__(self):
        if self._copy_data is not None:
            iv_obj = self._ivreg(self._formula, data=REnv.python_to_r_object(self._copy_data))
            self._result['lm'] = self._renv[iv_obj]
            self._result['summary'] = self._renv[self._summary(iv_obj)]
        else:
            print('Data is not defined!')
            raise Exception

        return self._result

    def __repr__(self):
        dot_line = '-'*80
        title = 'IV Regression Result: {}\n'.format(self._origin_formula)
        nobs = 'Number of Observation: {}'.format(self._data.shape[0])
        return ''.join([title,
                        nobs,'\n',
                        dot_line,'\n',
                        self.coefs.__repr__(),'\n',
                        dot_line,'\n'])

    @property
    def coefs(self):
        coefs = self._result['summary']['coefficients']
        if self._var_transform:
            indexes = coefs.index
            new_indexes = []
            for ind in indexes:
                if ind in self._variables_mapping_dict_reversed:
                    new_indexes.append(self._variables_mapping_dict_reversed[ind])
                elif ind == '(Intercept)':
                    new_indexes.append('常数')
                else:
                    new_indexes.append(ind)
            coefs.index = new_indexes
        return coefs

if __name__ == '__main__':
    stata_file = r'D:\data\test\MROZ.dta'
    stdata = Statadata(stata_file)
    mdata = stdata.read()
    rdata = mdata.loc[(mdata['wage']).notnull()]

    reg_obj = IVReg(data=rdata, formula = 'log(wage)~educ+exper+I(exper^2) | motheduc+fatheduc+exper+I(exper^2)')
    call_obj = reg_obj()
    print(list(call_obj.keys()))
    print(list(call_obj['summary'].keys()))
    print(call_obj['summary']['coefficients'])
    print(call_obj['summary']['call'][1])
    print('\n')
    print(reg_obj)

