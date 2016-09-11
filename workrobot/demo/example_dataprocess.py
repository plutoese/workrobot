# coding = UTF-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# example_dataprocess.py
# @简介：简介数据的导入、处理和分析流程
# @作者：Glen
# @日期：2016.8.13
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import pickle
import numpy as np
from operator import itemgetter
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection
from libs.database.class_mongoceic import MonDBCEIC
from libs.utils.class_formatconverter import MongoDBToPandasFormat
from libs.utils.class_datasweeper import BalancePanelConverter
from libs.utils.class_balanceddataselector import BalancedDataSelector
from libs.explorer.class_dataset import DataSet
from libs.utils.class_variable import VariableCreator
from libs.utils.class_basicmodel import Describe

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# 1. 数据获得
# @来源：MongoDB数据库
# @简介：从数据库中查询获得数据
# @方法：两种方法获得数据
#       1. 利用基础类(MongoDB、MonDatabase和MonColletion)
#       2. 利用具体数据库类
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

# 方法一
# 首先创建MonCollection对象
mcollection = MonCollection(database=MonDatabase(mongodb=MongoDB(), database_name='region'),
                            collection_name='provincestat')
# ------------------notice------------------------
# 如果要连接网络数据库，可以用字符串方式连接MongoDB数据库
# mongo = MongoDB(conn_str='mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
# ------------------------------------------------

# 通过find()进行查询，格式参照pymongo文档
cursor_general_way = mcollection.find({'variable':{'$in':['人均地区生产总值','私人控股企业法人单位数','城镇居民消费','城镇单位就业人员平均工资']}},
                                      projection={'_id':0,'variable':1,'value':1,'province':1,'acode':1,'year':1})

# -------------------------------------------------------------------------------------------------------------
# @关键变量cursor_general_way的类型 —— dict
# :cursor_general_way
# {'year': '2011', 'province': '北京', 'value': 289754.0, 'acode': '110000', 'variable': '私人控股企业法人单位数'}
# {'year': '2011', 'province': '辽宁', 'value': 248133.0, 'acode': '210000', 'variable': '私人控股企业法人单位数'}
# {'year': '2012', 'province': '吉林', 'value': 69471.0, 'acode': '220000', 'variable': '私人控股企业法人单位数'}
# {'year': '2011', 'province': '吉林', 'value': 64184.0, 'acode': '220000', 'variable': '私人控股企业法人单位数'}
# {'year': '2012', 'province': '黑龙江', 'value': 94640.0, 'acode': '230000', 'variable': '私人控股企业法人单位数'}
# -------------------------------------------------------------------------------------------------------------

# 方法二
# 利用具体的数据库类，例如MonDBCEIC(CEIC数据）、MonDBProvinceStat(省级统计年鉴数据)
# 由于它们是MonCollection的子类，因此仍然可以调用find()进行查询
mongo = MongoDB()
mdb = MonDatabase(mongodb=mongo, database_name='region')
ceic_db = MonDBCEIC(database=mdb)
cursor_specified_way = ceic_db.find()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 2. 数据转换
# @来源：MongoDB查询得到的数据
# @简介：主要把查询得到的dict格式的数据记录，转换为常用的pandas.DataFrame数据框
# @方法：利用MongoDBToPandasFormat对象的__call__()进行长表到宽表的转换
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# 首先创建MongoDBToPandasFormat对象，参数cursor是mongoDB查询得到的结果
converter = MongoDBToPandasFormat(cursor_general_way)

# 调用__call__()进行转换
# 基于pandas的pivot_table()
data_table = converter(values='value', index=['acode','year'], columns='variable', dropna=True)

# -------------------------------------------------------------------------------------------------------------
# @关键变量data_table的类型 —— pandas.DataFrame
# :data_table
# variable     人均地区生产总值  城镇单位就业人员平均工资   城镇居民消费  私人控股企业法人单位数
# acode  year
# 110000 1993    8006.0           NaN   308.81          NaN
#        1994   10240.0           NaN   197.60          NaN
#        1995   12690.0           NaN   296.93          NaN
#        ...
# 120000 1993    5800.0           NaN   161.67          NaN
#        1994    7751.0           NaN   185.78          NaN
#        1995    9769.0           NaN   230.05          NaN
#        ...
# -------------------------------------------------------------------------------------------------------------

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 2'. 平衡数据集（可选）
# @简介：去除数据集中的缺失数据，获得平衡数据集
# @方法：方法一用来处理面板数据，方法二用来选择横截面或时间序列数据
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# 方法一
# 创建BalancePanelConverter对象
panel_creator = BalancePanelConverter(data=data_table, keep_index='acode')

# 调用__call__()，得到平衡面板
panel_data = panel_creator()

# -------------------------------------------------------------------------------------------------------------
# @关键变量panel_data的类型 —— pandas.DataFrame
# :panel_data
# variable     人均地区生产总值  城镇单位就业人员平均工资   城镇居民消费  私人控股企业法人单位数
# acode  year
# 110000 2010   73856.0       65158.0  4402.72     282726.0
#        2011   81658.0       75482.0  5147.07     289754.0
#        2012   87475.0       84742.0  5790.13     302438.0
# 120000 2010   72994.0       51489.0  2039.64     101465.0
#        2011   85213.0       55658.0  2480.85     114857.0
#        2012   93173.0       61514.0  2867.48     130302.0
# 130000 2010   28668.0       31451.0  4162.45     189638.0
#        2011   33969.0       35309.0  4937.26     201671.0
#        2012   36584.0       38658.0  5554.79     220456.0
# -------------------------------------------------------------------------------------------------------------

# 方法二
# 获得平衡横截面数据或时间序列数据
# 对于pandas.DataFrame格式的数据表，可以用DataFrame.dropna()，DataFrame.fillna()或DataFrame.replace()
# 此外，这里提供了一个方法，根据设定缺失数据的上限，来选择数据集

# 首先导入CEIC的数据
F = open(r'E:\github\workrobot\workrobot\files\ceic_raw_data_year.pkl', 'rb')
ceic_whole_data = pickle.load(F)

# 选择2010年的数据
ceic_data_2010 = ceic_whole_data.loc[2010]

# 创建BalancedDataSelector对象
selector = BalancedDataSelector(data=ceic_data_2010)

# 设定缺失数据数量的上限
max_na_number_per_variable = 5

# 调用select(),完成选择器构建
variable_selector = selector.select(max_na_number_per_variable=max_na_number_per_variable)

# 获得符合缺失数据上限条件的某个数据集
variables = list(list(variable_selector.keys())[10])

'''
variables = {item:len(item) for item in variable_selector.keys()}
sorted_variables = sorted(variables.items(), key=itemgetter(1), reverse=True)

datasets = []
for item in sorted_variables[0:10]:
    random_data_table = ceic_data_2010.loc[:, list(item[0])].dropna()
    datasets.append(random_data_table)

F = open(r'E:\github\workrobot\workrobot\data\ceic\random_datasets.pkl', 'wb')
pickle.dump(datasets, F)
F.close()'''

random_data_table = ceic_data_2010.loc[:, variables].dropna()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3. 创建数据集，添加流程，进行数据分析
# @来源：整理完成的数据集
# @简介：构建数据集，利用add_data_method()添加方法，通过run()进行数据处理和分析
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# 创建数据集
research_dataset = DataSet(data=random_data_table, name='CEIC random dataset', type='cross section')
print(list(research_dataset.data.columns))


# 添加变量转换方法到流程中
# 添加对数变量
research_dataset.add_data_method(VariableCreator(data=research_dataset.data, func=np.log,
                                                 name='log',variable_names=['企业数_工业'],
                                                 mode='append'),
                                 method_name='log',method_type=1)

# 添加和变量
research_dataset.add_data_method(VariableCreator(research_dataset.data, np.add, 'add', ['从业人数_第三产业'], '从业人数总和', 'append', research_dataset.data['从业人数_制造业']),
                                 method_name='add', method_type=1)

# 添加describe方法
research_dataset.add_data_method(Describe(data=research_dataset.data),
                                 method_name='describe',method_type=2)

# 依次运行流程中的方法
research_dataset.run()

# 打印数据方法结果
print(research_dataset)

print(list(research_dataset.result['describe'].keys()))
print(research_dataset.result['describe']['summary'])