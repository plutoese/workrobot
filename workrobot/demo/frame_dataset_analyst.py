# coding = UTF-8

import random
from libs.explorer.class_dataset import DataSet
from libs.database.class_mongoceic import MonDBCEIC
from libs.database.class_mondbprovincestat import MonDBProvinceStat
from libs.imexport.class_mongodb import MongoDB, MonDatabase
from libs.utils.class_formatconverter import MongoDBToPandasFormat
from libs.utils.class_datasweeper import BalancePanelConverter, DeleteNARow
from libs.utils.class_basicmodel import Describe
from libs.statmodel.class_reg import Reg
from copy import deepcopy

# 0. setup
# 0.1 系统默认参数
# 0.1.1 数据库选择初始化
DATABASES = {1: 'region'}
COLLECTIONS = {1: MonDBProvinceStat, 2: MonDBCEIC}

# 0.2 用户自定义项
# 0.2.1 数据库选择
# 1 —— region
DATABASE_CHOICE = 1

# 0.2.2 数据集合选择
# 1 —— provincestat
# 2 —— ceic
COLLECTION_CHOICE = 2

# 0.2.3 是否打印数据库基本信息
COLLECTION_INFO = False

# 0.2.4 随机选择
# 变量随机选择
VARIABLE_RANDOM_CHOICE = 2
# 时期数随机选择
PERIOD_RANDOM_CHOICE = 1
# 开始年份随机选择
START_TIME_CHOICE = 1990
# 区域随机选择
REGION_RANDOM_CHOICE = 0

# 是否是随机样本，如果是，则进行循环，不是则退出
RANDOMIZATION = VARIABLE_RANDOM_CHOICE * REGION_RANDOM_CHOICE * REGION_RANDOM_CHOICE

# 0.2.4
# 自定义选择
USER_VARIABLES = None
USER_PERIOD = None
USER_REGION = None
USER_FILTER = dict()
USER_PROJECTION = {'_id':0,'variable':1,'value':1,'acode':1,'year':1}
USER_SORT = [('acode',1),('year',1)]

# 平滑面板时固定的轴名称
USER_FIXED_INDEX = 'acode'

# 数据集最小数量
USER_MIN_DATASET_NUMBER = 50

# 1. to query in the mongodb
# 1.1 连接数据库
user_database = MonDatabase(mongodb=MongoDB(), database_name=DATABASES.get(DATABASE_CHOICE))
user_colllection = COLLECTIONS.get(COLLECTION_CHOICE)(database=user_database)

# 1.2 数据库基本参数打印
if COLLECTION_INFO:
    user_colllection.info()

round = 1
while True:
    # 1.3 查询数据，返回结果
    # 打印开始信息
    print(''.join(['='*40,'Round ',str(round),'='*40]))

    # 设定变量variables
    if VARIABLE_RANDOM_CHOICE > 0:
        variables = random.sample(user_colllection.variables,VARIABLE_RANDOM_CHOICE)
    elif VARIABLE_RANDOM_CHOICE < 0:
        variables = random.sample(user_colllection.variables,random.randrange(1,len(user_colllection.variables)))
    else:
        variables = USER_VARIABLES

    # 打印选择的变量
    if variables is None:
        print('Variables not selected')
    else:
        print(''.join(['Variables Selected: ',','.join(variables)]))

    # 设定时间段period
    if PERIOD_RANDOM_CHOICE > 0:
        start_time = random.choice(user_colllection.period[user_colllection.period.index(START_TIME_CHOICE):-PERIOD_RANDOM_CHOICE])
        period = [str(y) for y in range(start_time,start_time+PERIOD_RANDOM_CHOICE)]
    elif PERIOD_RANDOM_CHOICE < 0:
        random_period_length = random.choice(range(1,len(range(START_TIME_CHOICE,user_colllection.period[-1]))))
        start_time = random.choice(user_colllection.period[user_colllection.period.index(START_TIME_CHOICE):-random_period_length+1])
        period = [str(y) for y in range(start_time,start_time+random_period_length)]
    else:
        if USER_PERIOD is None:
            period = [str(y) for y in user_colllection.period[user_colllection.period.index(START_TIME_CHOICE):]]
        else:
            period = [str(y) for y in USER_PERIOD]

    # ceic的year变量是int型的
    if COLLECTION_CHOICE == 2:
        period = [int(y) for y in period]

    # 打印选择的时期
    if period is None:
        print('Period not selected')
    else:
        print(''.join(['Period Selected: ',','.join([str(p) for p in period])]))

    # 设置区域
    if REGION_RANDOM_CHOICE > 0:
        regions = random.sample(user_colllection.acode,REGION_RANDOM_CHOICE)
    elif REGION_RANDOM_CHOICE <0:
        random_region_number = random.choice(range(1,len(user_colllection.acode)))
        regions = random.sample(user_colllection.acode,random_region_number)
    else:
        regions = USER_REGION

    # 打印选择的区域
    if regions is None:
        print('Regions not selected')
    else:
        print(''.join(['Regions Selected: ',','.join(regions)]))

    # 设定查询
    if variables is not None:
        USER_FILTER['variable'] = {'$in':variables}
    if period is not None:
        USER_FILTER['year'] = {'$in': period}
    if regions is not None:
        USER_FILTER['acode'] = {'$in': regions}

    # 打印查询语句
    print('Query string: ',USER_FILTER)

    USER_DATAFRAME_INDEXES = []
    if regions is None or len(regions) > 1:
        USER_DATAFRAME_INDEXES.append('acode')
    if period is None or len(period) > 1:
        USER_DATAFRAME_INDEXES.append('year')

    # 查询
    #USER_FILTER =  {'variable': {'$in': ['企业数_工业_内资企业', '煤气、天然气供量_生活']}, 'year': {'$in': [1995]}}
    cursor = user_colllection.find(filter=USER_FILTER, projection=USER_PROJECTION, sort=USER_SORT)
    if cursor.count() < 1:
        continue

    # 2. to convert data
    mongoconverter = MongoDBToPandasFormat(cursor)
    raw_data = mongoconverter(values='value', index=USER_DATAFRAME_INDEXES, columns='variable',dropna=True)

    # 打印查询得到的原始数据
    print(''.join(['-'*40,'Original DataSet','-'*40]))
    print(raw_data)

    # 3. construct dataset
    research_dataset = DataSet(raw_data,'region data')

    # 4. data cleaning
    if (period is None or len(period) > 1) and (regions is None or len(regions) > 1):
        research_dataset.add_data_method(BalancePanelConverter(data=research_dataset._work_data,keep_index=USER_FIXED_INDEX),
                                         method_name='balanced',method_type=1)
    else:
        research_dataset.add_data_method(DeleteNARow(data=research_dataset._work_data),
                                         method_name='delete NA rows',method_type=1)

    # 打印work flow的队列
    print('Work Flow before running: ', research_dataset.work_flow)

    research_dataset.run()

    # 打印work_flow的队列
    print('Work Flow after running: ', research_dataset.work_flow)

    # 打印调整平滑后的原始数据
    print(''.join(['-'*40,'Balanced DataSet','='*40]))
    print(research_dataset.data)

    if RANDOMIZATION:
        break

    if len(research_dataset.data) > USER_MIN_DATASET_NUMBER:
        break

    round += 1

print(research_dataset)

# 5. data explore
# 5.1 探索性数据分析
method_name = 'describe'
research_dataset.add_data_method(Describe(data=research_dataset.data),
                                 method_name=method_name, method_type=2)
research_dataset.run()
print(list((research_dataset.result[method_name]).keys()))
print(research_dataset)

# 6. data mining


# 7. modeling
# 用英文变量名替代中文变量名
print('--------------- modelling---------------')


if len(research_dataset.data.columns) > 1:
    formula = '{} ~ {}'.format(research_dataset.data.columns[0],' + '.join(research_dataset.data.columns[1:]))
    reg_obj = Reg(data=research_dataset.data, formula=formula,var_transform=True)
    result = reg_obj()
    print(reg_obj)
    reg_obj.coefs.to_excel('d:/temp/myresult.xls')
