# coding=UTF-8

from libs.imexport.class_Excel import Excel
import pandas as pd
import re
from libs.datasheet.class_DataSheet import DataSheet
from copy import copy
from dbadmin.popcensus.class_popcensusdatabase import PopCensusDatabase


class PopCensusSheet(DataSheet):
    """ 类PopCensusSheet是人口普查数据的表单类

    """
    def __init__(self, filename=None,sheet=None,type=None,year='2010'):
        DataSheet.__init__(self,filename=filename,sheet=sheet,type=type)
        self._title = None
        self._variables = []
        self._datatable = []
        self._region = dict()
        self._year = year

        self.pop_census = PopCensusDatabase()
        self.var_unit_dict = dict()
        for v in self.pop_census.variables:
            found = self.pop_census.collection._collection.find_one({'variable':v})
            self.var_unit_dict[found.get('variable')] = found.get('unit')

        self._parse()

    def to_record(self):
        records = []
        for item in self._datatable:
            region = item[0]
            if self._region[region] is not None:
                acode = self._region[region][1]
                regionid = self._region[region][2]
            else:
                acode = None
                regionid = None
            for i in range(len(self._variables)):
                one_record = dict()
                one_record['variable'] = self._variables[i]
                one_record['unit'] = self.var_unit_dict[self._variables[i]]
                one_record['region'] = region
                one_record['acode'] = acode
                one_record['regionid'] = regionid
                one_record['year'] = self._year
                one_record['source'] = '2010年中国人口普查'
                one_record['value'] = item[1:][i]
                records.append(one_record)
        return records

    def _parse(self):
        self._decompose()
        self._match_regions()
        self.compose_variable()

    def set_unit(self,var_unit=None):
        self.var_unit_dict.update(var_unit)

    def compose_variable(self):
        if len(self._variables) > 1:
            row = self._variables[0]
            for i in range(len(row)):
                if re.match('^\s*$',row[i]) is not None:
                    row[i] = latest
                else:
                    latest = row[i]
            variables= []
            for i in range(len(self._variables[0])):
                tmp_var = ''
                for j in range(len(self._variables)):
                    tmp_var = ''.join([tmp_var,self._variables[j][i]])
                variables.append(tmp_var)

            self._variables = variables[1:]
        else:
            self._variables = self._variables[0][1:]

    def _match_regions(self):
        region = []
        for row in self._datatable:
            if len(region) > 2:
                region[len(region)-1] = row[0]
            else:
                region.append(row[0])

            result = DataSheet.match_for_region(region,self._year)
            if result is not None:
                self._region[row[0]] = (result[-1].get('region'),result[-1].get('acode'),result[-1].get('_id'))
                region = result[:-1]
            else:
                print('Can not found: {} {}'.format(' '.join(region),row[0]))
                self._region[row[0]] = None

    def _decompose(self):
        raw_data = copy(self._rawdata)

        #去除空列
        process_data_without_blank_rows = [row for row in raw_data if not DataSheet.is_blank_row(row)]

        # 记录数据行开始
        for i in range(len(process_data_without_blank_rows)):
            if DataSheet.is_data_row(process_data_without_blank_rows[i]):
                data_table_starter = i
                break

        # 记录数据行结束
        for i in range(len(process_data_without_blank_rows)-1,0,-1):
            if DataSheet.is_data_row(process_data_without_blank_rows[i]):
                data_table_ender = i
                break

        # 解析表头
        if DataSheet.is_title(process_data_without_blank_rows[0]):
            self._title = process_data_without_blank_rows[0][0]
        else:
            print('The first row is not title!')
            raise Exception

        # 储存到数据表
        for i in range(data_table_starter,data_table_ender+1):
            if DataSheet.is_data_row(process_data_without_blank_rows[i],between_data_table=True):
                self._datatable.append(process_data_without_blank_rows[i])
            else:
                print('Not Data Row: {}'.format(' '.join(process_data_without_blank_rows[i])))
                raise Exception

        # 储存变量
        for i in range(1,data_table_starter):
            self._variables.append(process_data_without_blank_rows[i])

if __name__ == '__main__':
    psheet = PopCensusSheet(r'E:\data\popcensus\origin\2010_08.xls')
    #psheet.set_unit({'总和生育率':'%'})
    #psheet.set_unit({'6岁以上扫盲班教育程度男性人口':'人','6岁以上扫盲班教育程度女性人口':'人',
    #                 '6岁以上中学专科教育程度男性人口':'人','6岁以上中学专科教育程度女性人口':'人',
    #                 '6岁以上大学本科教育程度男性人口':'人','6岁以上大学本科教育程度女性人口':'人',
    #                 '6岁以上研究生教育程度男性人口':'人','6岁以上研究生教育程度女性人口':'人'})

    #psheet.set_unit({'15岁及以上各种职业人口':'人','15岁及以上国家机关党群组织企业事业单位负责人':'人',
    #                '15岁及以上专业技术人员':'人','15岁及以上办事人员和有关人员':'人',
    #                '15岁及以上商业服务业人员':'人','15岁及以上农林牧渔水利业生产人员':'人',
    #                '15岁及以上生产运输设备操作人员及有关人员':'人','15岁及以上不便分类的其他从业人员':'人',
    #                '从未工作正在寻找工作人口':'人','失去工作正在寻找工作人口':'人'})

    #psheet.set_unit({'15岁及以上各种行业人口':'人','15岁及以上农林牧渔业人口':'人',
    #                 '15岁及以上采掘业人口':'人','15岁及以上制造业人口':'人',
    #                 '15岁及以上电力燃气及水的生产和供应业人口':'人','15岁及以上建筑业人口':'人',
    #                 '15岁及以上地质勘探和水利管理业人口':'人','15岁及以上交通运输仓储及邮电通信业人口':'人',
    #                 '15岁及以上批发和零售及贸易餐饮业人口':'人','15岁及以上金融保险业人口':'人',
    #                 '15岁及以上房地产业人口':'人','15岁及以上社会服务业人口':'人',
    #                 '15岁及以上卫生体育和社会福利业人口':'人','15岁及以上教育文化艺术及广播电影电视业人口':'人',
    #                 '15岁及以上科学研究和综合技术服务业人口':'人','15岁及以上国家机关政党机关和社会团体人口':'人',
    #                 '15岁及以上其他行业人口':'人'})

    #psheet.set_unit({'15岁及以上初婚有配偶人口':'人','15岁及以上初婚有配偶男性人口':'人',
    #                 '15岁及以上初婚有配偶女性人口':'人','15岁及以上再婚有配偶人口':'人',
    #                 '15岁及以上再婚有配偶男性人口':'人','15岁及以上再婚有配偶女性人口':'人',
    #                 '15-50岁妇女平均活产子女数':'人','15-50岁妇女平均存活子女数':'人'})
    #psheet.set_unit({'长表家庭户':'户','长表住房中有厨房家庭户':'户',
    #                 '长表住房中无厨房家庭户':'户','长表是饮用自来水家庭户':'户',
    #                 '长表否饮用自来水家庭户':'户','长表住房中有洗澡设施家庭户':'户',
    #                 '长表住房中无洗澡设施家庭户':'户','长表住房中有厕所家庭户':'户',
    #                 '长表住房中无厕所家庭户':'户','长表自建住房家庭户':'户',
    #                 '长表购买住房家庭户':'户','长表租用住房家庭户':'户',
    #                 '长表其他住房家庭户':'户'})

    pop_census = PopCensusDatabase()

    '''
    for record in psheet.to_record():
        print(record)
        pop_census.collection._collection.insert_one(record)'''

    #pop_census.collection._collection.update_many({'variable':'6岁以上大学本科教育程度女性人口'},{'$set':{'variable':'6岁以上大学本科及以上教育程度女性人口'}})


    print(pop_census.collection._collection.count({'year':'2010'}))
    #pop_census.collection._collection.delete_many({'year':'2000'})
    #print(pop_census.collection._collection.count({'year':'2000'}))

