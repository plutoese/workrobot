# coding=UTF-8

"""
=========================================
变量匹配类
=========================================

:Author: glen
:Date: 2016.10.26
:Tags: variable
:abstract: 对变量进行匹配

**类**
==================
VariableMatcher
    区域匹配类

**使用方法**
==================

**示范代码**
==================

"""

import re
from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection
from libs.datasheet.class_DataSheet import DataSheet
import regex
import pandas as pd
import numpy as np


class VariableMatcher:
    def __init__(self):
        self._variables = []
        self._unit = []

    def matching(self,variable_rows=None,unit_sep='\(|\)|（|）',unit=None,db_search=True,query_dict=None,file=None):
        # 分解原始数据行
        _variables, _unit = self.handle_origin_variable_row(variable_rows=variable_rows,unit_sep=unit_sep,unit=unit)
        var_unit_dict = dict(zip(_variables,_unit))
        pd_result = pd.DataFrame({'origin_variable':_variables,'matched_variable':None,'unit':None},
                                 columns=['origin_variable','matched_variable','unit'])
        not_found_vars = _variables

        found_var_dict = dict()
        db_var_dict = dict()
        found_unit_dict = dict()
        if file is not None:
            pd_middle_result = VariableMatcher.search_from_file(not_found_vars,file=file)
            found_var = pd_middle_result[pd_middle_result['matched_variable'].notnull()]
            found_var_dict = dict(zip(found_var['origin_variable'],found_var['matched_variable']))
            found_unit = pd_middle_result[pd_middle_result['unit'].notnull()]
            found_unit_dict = dict(zip(found_unit['origin_variable'], found_unit['unit']))
            not_found_vars = list(pd_middle_result[pd_middle_result['matched_variable'].isnull()]['origin_variable'])

        if db_search:
            pd_middle_result = VariableMatcher.search_from_dbase(not_found_vars, query_dict=query_dict)
            found_var = pd_middle_result[pd_middle_result['matched_variable'].notnull()]
            db_var_dict = dict(zip(found_var['origin_variable'],found_var['matched_variable']))

        for ind in pd_result.index:
            if db_var_dict.get(pd_result.loc[ind, 'origin_variable']) is not None:
                pd_result.loc[ind, 'matched_variable'] = db_var_dict.get(pd_result.loc[ind, 'origin_variable'])
            if found_var_dict.get(pd_result.loc[ind, 'origin_variable']) is not None:
                pd_result.loc[ind, 'matched_variable'] = found_var_dict.get(pd_result.loc[ind, 'origin_variable'])

            if pd_result.loc[ind,'matched_variable'] is None:
                pd_result.loc[ind, 'matched_variable'] = pd_result.loc[ind,'origin_variable']

            if var_unit_dict.get(pd_result.loc[ind, 'origin_variable']) is not None:
                pd_result.loc[ind, 'unit'] = var_unit_dict.get(pd_result.loc[ind, 'origin_variable'])
            if found_unit_dict.get(pd_result.loc[ind, 'origin_variable']) is not None:
                pd_result.loc[ind, 'unit'] = found_unit_dict.get(pd_result.loc[ind, 'origin_variable'])

            if pd_result.loc[ind,'unit'] is None:
                print('{} unit is not exist!'.format(pd_result.loc[ind,'origin_variable']))
                raise Exception

        return pd_result

    def destruct_variable_row(self,variable_rows=None,unit_sep='\(|\)|（|）'):
        if variable_rows.shape[0] == 1:
            return variable_rows

        latest = None
        start = 0
        for i in range(variable_rows.shape[1]):
            if variable_rows.iloc[0,i] is np.nan:
                if latest is not None:
                    variable_rows.values[0,i] = latest
                if i == variable_rows.shape[1] - 1:
                    variable_rows.values[1:,start:i+1] = self.destruct_variable_row(variable_rows=variable_rows.iloc[1:,start:i+1])
            else:
                latest = variable_rows.iloc[0,i]
                if i > start:
                    variable_rows.values[1:,start:i] = self.destruct_variable_row(variable_rows=variable_rows.iloc[1:,start:i])
                    start = i

        return variable_rows

    def handle_origin_variable_row(self,variable_rows=None,unit_sep='\(|\)|（|）',unit=None):
        variable_rows = self.destruct_variable_row(variable_rows=variable_rows)

        variables = []
        units = []
        for j in range(variable_rows.shape[1]):
            rvar = variable_rows.iloc[:,j].str.cat(sep='_')
            rvar_split = re.split(unit_sep,rvar)
            if len(rvar_split) == 3:
                units.append(re.sub('\s+','',rvar_split[1]))
                variables.append(''.join([rvar_split[0],rvar_split[2]]))
            else:
                units.append(unit)
                variables.append(rvar_split[0])

        vars = []
        for v in variables:
            if re.match('.*\_$',v) is not None:
                vars.append(re.sub('\s+', '', v[:len(v)-1]))
            else:
                vars.append(re.sub('\s+', '', v))

        return vars, units

    @staticmethod
    def substitue(variables=None,substitution=None):
        if isinstance(variables,str):
            return {variables:substitution}
        elif isinstance(variables,pd.DataFrame):
            result = dict()
            for i in range(variables.shape[0]):
                result[variables.iloc[i,0]] = re.split(';',variables.iloc[i,1])
            return result
        else:
            print('Unsupport Type: ',type(variables))
            raise Exception

    @staticmethod
    def search_for_similar_variable(variables,source=None):
        """ 寻找近似的变量

        :param str,list variables: 原始变量
        :param list source: 可选变量集
        :return: 返回匹配的变量
        :rtype: pandas.DataFrame
        """
        origin_variable = []
        var_possible_match = []
        not_matched_count = []
        if isinstance(variables,str):
            for source_var in source:
                if VariableMatcher.fuzzy_variable_matching(variables,source_var) is not None:
                    origin_variable.append(variables)
                    var_possible_match.append(source_var)
                    not_matched_count.append(sum(VariableMatcher.fuzzy_variable_matching(variables,source_var).fuzzy_counts))
            return pd.DataFrame({'origin_variable':origin_variable,
                                 'matched_variable':var_possible_match,
                                 'fuzzy_count':not_matched_count},
                                columns=['origin_variable','matched_variable','fuzzy_count'])
        elif isinstance(variables,list):
            for v in variables:
                for source_var in source:
                    if VariableMatcher.fuzzy_variable_matching(v,source_var) is not None:
                        origin_variable.append(v)
                        var_possible_match.append(source_var)
                        not_matched_count.append(sum(VariableMatcher.fuzzy_variable_matching(v,source_var).fuzzy_counts))
                if v not in origin_variable:
                    origin_variable.append(v)
                    var_possible_match.append(None)
                    not_matched_count.append(0)
            return pd.DataFrame({'origin_variable':origin_variable,
                                 'matched_variable':var_possible_match,
                                 'fuzzy_count':not_matched_count},
                                columns=['origin_variable','matched_variable','fuzzy_count']
                                )
        else:
            return None

    @staticmethod
    def search_for_same_variable(variables,source=None):
        """ 寻找一样的变量

        :param str,list variables: 原始变量
        :param list source: 可选变量集
        :return: 返回匹配的变量
        :rtype: pandas.DataFrame
        """
        origin_variable = []
        var_possible_match = []
        if isinstance(variables, str):
            for source_var in source:
                if re.match(''.join(['^',variables,'$']), source_var) is not None:
                    origin_variable.append(variables)
                    var_possible_match.append(source_var)
                    break
            if len(origin_variable) < 1:
                origin_variable = [variables]
                var_possible_match = [None]
            return pd.DataFrame({'origin_variable': origin_variable,
                                 'matched_variable': var_possible_match},
                                columns=['origin_variable', 'matched_variable'])
        elif isinstance(variables, list):
            for v in variables:
                for source_var in source:
                    if re.match(''.join(['^',v,'$']), source_var) is not None:
                        origin_variable.append(v)
                        var_possible_match.append(source_var)
                if v not in origin_variable:
                    origin_variable.append(v)
                    var_possible_match.append(None)
            return pd.DataFrame({'origin_variable': origin_variable,
                                 'matched_variable': var_possible_match},
                                columns=['origin_variable', 'matched_variable']
                                )
        else:
            return None

    @staticmethod
    def search_from_file(variables=None,file=None):
        units_dict = None
        origin_vars_dataframe = pd.read_excel(file,header=None)
        if origin_vars_dataframe.shape[1] < 3:
            vars_dataframe = origin_vars_dataframe[origin_vars_dataframe.notnull().all(axis=1)]
            vars_dict = dict(zip(vars_dataframe.iloc[:, 0], vars_dataframe.iloc[:, 1]))
        else:
            vars_dataframe = origin_vars_dataframe.iloc[:, [0, 1]]
            vars_dataframe = vars_dataframe[vars_dataframe.notnull().all(axis=1)]
            vars_dict = dict(zip(vars_dataframe.iloc[:, 0], vars_dataframe.iloc[:, 1]))
            units_dataframe = origin_vars_dataframe.iloc[:, [0, 2]]
            units_dataframe = units_dataframe[units_dataframe.notnull().all(axis=1)]
            units_dict = dict(zip(units_dataframe.iloc[:, 0], units_dataframe.iloc[:, 1]))

        pd_result = VariableMatcher.search_for_same_variable(variables=variables, source=vars_dict.keys())
        for ind in pd_result.index:
            pd_result.loc[ind, 'matched_variable'] = vars_dict.get(pd_result.loc[ind, 'matched_variable'])
            if units_dict is not None:
                pd_result.loc[ind, 'unit'] = units_dict.get(pd_result.loc[ind, 'origin_variable'])

        return pd_result

    @staticmethod
    def search_from_dbase(variables=None,query_dict=None,match='exact'):
        collection_variable = MonCollection(database=MonDatabase(mongodb=MongoDB(), database_name='region'),
                                            collection_name='storedvariable')
        found = collection_variable.find(query_dict)
        found_dict = {item['origin']:item['variable'] for item in found}
        if match == 'exact':
            pd_result = VariableMatcher.search_for_same_variable(variables=variables,source=found_dict.keys())
            for ind in pd_result.index:
                pd_result.loc[ind, 'matched_variable'] = found_dict.get(pd_result.loc[ind, 'matched_variable'])
        else:
            pd_result = VariableMatcher.search_for_similar_variable(variables=variables,source=found_dict.keys())
            for ind in pd_result.index:
                pd_result.loc[ind, 'matched_middel_variable'] = pd_result.loc[ind, 'matched_variable']
                pd_result.loc[ind,'matched_variable'] = found_dict.get(pd_result.loc[ind,'matched_variable'])

        return pd_result

    @staticmethod
    def fuzzy_variable_matching(variable,compared,error='auto'):
        if re.match('^auto$',error) is not None:
            error = max(1,int(len(variable)*0.6))

        return regex.fullmatch('(?:%s){e<=%s}' % (variable, str(error)),compared)

if __name__ == '__main__':
    mongo = MongoDB()
    mdb = MonDatabase(mongodb=mongo, database_name='region')
    collection_province = MonCollection(database=mdb, collection_name='popcensus')
    collection_variable = MonCollection(database=mdb, collection_name='storedvariable')

    '''
    var = set()
    for v in sorted(collection_province.find().distinct('variable')):
        var.add(re.sub('\s+','',v))
        print(v,len(v))
    print(len(var))
    print(len(collection_province.find().distinct('variable')))'''


    #for v in collection_province.find().distinct('variable'):
    #    collection_variable.collection.insert_one({'variable':v,'source':'中国人口普查'})

    #vars = [item['variable'] for item in collection_variable.find()]
    #x = ['总人口_合计', '总人口_男', '总人口_女', '总人口_性别比', '户籍人口', '少数民族人口比重_', '非农业户口人口比重_', '城乡人口_城镇', '城乡人口_乡村', '家庭户_户数', '家庭户_人口数', '家庭户_户规模', '家庭户_其中：一人户', '家庭户类别_一代户', '家庭户类别_二代户', '家庭户类别_三代户', '家庭户类别_四代以上户']
    #vmatcher = VariableMatcher()
    #print(pd.read_excel(r'E:\data\popcensus\origin\var_popcensus.xls',header=None))
    #print(vmatcher.search_from_file(x,file=r'E:\data\popcensus\origin\var_popcensus.xls'))
    #print(VariableMatcher.search_for_similar_variable(x,vars))

    sheet = DataSheet(filename=r'E:\data\popcensus\origin\01.xls', sheet=0, type=1)
    rdata = sheet._rawdata
    rdata = rdata[rdata.notnull().any(axis=1)]
    #print(rdata.iloc[1:4])
    vmatcher = VariableMatcher()
    vars, _ = vmatcher.handle_origin_variable_row(rdata.iloc[1:4])
    vars = vars[1:]
    print(vars)
    #print(VariableMatcher.search_from_dbase(variables=vars,query_dict={'source':'中国人口普查'},match='exact'))
    #origin_vars_dataframe = pd.read_excel(r'E:\data\popcensus\origin\variable_matcher.xls',header=None)
    #result = VariableMatcher.search_from_file(variables=vars,file=r'E:\data\popcensus\origin\variable_matcher.xls')
    #print(result[result.notnull().all(axis=1)])
