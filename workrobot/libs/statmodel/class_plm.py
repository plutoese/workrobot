# coding=UTF-8

"""
=========================================
回归分析——面板数据模型
=========================================

:Author: glen
:Date: 2016.8.18
:Tags: regression panel_data
:abstract: 面板数据模型估计——固定效应和随机效应

**类**
==================
Plm
    面板数据模型估计——固定效应和随机效应


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


class Plm(BasicModel):
    def __init__(self, data=None, id=None, time=None,
                 name='panel data model', formula=None,
                 var_transform=False, model='Fixed', *args, **kwargs):
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

        #self._formula = Formula(self._formula)
        self._model = model

        # 导入plm库
        self._renv._R.r('library("plm")')
        # 把数据转换为R数据格式
        self._renv['mdata'] = self._renv.python_to_r_object(self._copy_data)
        # 把数据格式转换为面板格式
        fmt_str = 'pdata <- pdata.frame(mdata, index=c("{0}","{1}"))'
        self._renv._R.r(fmt_str.format(id,time))

        self._summary = importr('base').summary

    def __call__(self):
        if self._copy_data is not None:
            plm_str = 'plm({0},data=pdata,model="{1}")'
            print(plm_str.format(self._formula, self._model))
            plm_obj = self._renv._R.r(plm_str.format(self._formula, self._model))
            self._result['plm'] = self._renv[plm_obj]
            self._result['summary'] = self._renv[self._summary(plm_obj)]
        else:
            print('Data is not defined!')
            raise Exception

        return self._result

    def __repr__(self):
        dot_line = '-'*80
        title = 'Panel Data Result: {}\n'.format(self._origin_formula)
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
    '''
    stata_file = r'D:\data\test\JTRAIN.dta'
    stdata = Statadata(stata_file)
    mdata = stdata.read()
    print(mdata.columns)
    plm = importr('plm')

    reg_obj = Plm(data=mdata, formula='log(scrap)~d88+d89+grant+grant_1', id='fcode', time='year')
    call_obj = reg_obj()
    print(reg_obj.coefs)
    print(reg_obj._result['summary']['coefficients'])
    print(reg_obj)'''

    stata_file = r'D:\data\test\wagepan.dta'
    stdata = Statadata(stata_file)
    mdata = stdata.read()
    print(mdata.columns)
    plm = importr('plm')

    reg_obj = Plm(data=mdata, formula='lwage~educ+black+hisp+exper+I(exper^2)+married+union+yr',
                  id='nr', time='year', model='random')
    reg_obj._renv._R.r('pdata$yr<-factor(pdata$year)')
    call_obj = reg_obj()
    print(reg_obj.coefs)
    print(reg_obj._result['summary']['coefficients'])
    print(reg_obj)

