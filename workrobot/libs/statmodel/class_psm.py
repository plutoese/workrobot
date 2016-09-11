# coding=UTF-8

"""
=========================================
回归分析——倾向值得分匹配模型
=========================================

:Author: glen
:Date: 2016.8.29
:Tags: regression psm
:abstract: Propensity Score Matching(倾向值得分匹配模型)

**类**
==================
Logistic
    用logistic模型进行回归分析的主类


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


class PropensityScoreMatching(BasicModel):
    def __init__(self, data=None, name='Propensity Score Matching', formula=None, method='nearest',
                 distance = 'logit', var_transform=False, *args, **kwargs):
        super().__init__(data=data, name=name, *args, **kwargs)

        # 创建REnv实例
        self._renv = REnv()
        # 创建matchit
        self._formula = formula
        # 创建方法
        self._method = method
        # 创建距离
        self._distance = distance
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

        # 导入MatchIt库
        self._renv._R.r('library("MatchIt")')
        # 把数据转换为R数据格式
        self._renv['mdata'] = self._renv.python_to_r_object(self._copy_data)
        self._summary = importr('base').summary

    def __call__(self):
        if self._copy_data is not None:
            # estimate propensity scores and create matched data set using 'matchit'
            matching_it_str = 'match_it <- matchit({0}, data = mdata, method = "{1}", distance = "{2}")'.format(self._formula, self._method, self._distance)
            self._renv._R.r(matching_it_str)
            self._renv._R.r('psm <- match_it$nn')
            self._result['psm'] = self._renv['psm']

            self._renv._R.r('matched_data <- match.data(match_it,distance ="pscore")')
            self._result['matched_data'] = self._renv['matched_data']
        else:
            print('Data is not defined!')
            raise Exception

        return self._result

    def __repr__(self):
        dot_line = '-'*80
        title = 'Propensity Score Matching: {}\n'.format(self._origin_formula)
        return ''.join([title,
                        dot_line,'\n',
                        self._result['psm'].__repr__(),'\n',
                        dot_line,'\n'])

    @property
    def matched_data(self):
        return self._result['matched_data']

if __name__ == '__main__':
    stata_file = r'D:\data\test\lalonde.dta'
    stdata = Statadata(stata_file)
    mdata = stdata.read()
    print(mdata)

    reg_obj = PropensityScoreMatching(data=mdata,
                                      formula='treat ~ age + educ + black + hispan + nodegree + married + re74 + re75')
    call_obj = reg_obj()
    print(list(call_obj.keys()))
    print(call_obj['psm'])
    print(call_obj['matched_data'])
    print(reg_obj)


