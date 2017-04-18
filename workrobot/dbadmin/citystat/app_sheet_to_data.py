# coding = UTF-8

import time
import os
import configparser
from libs.spreadsheet.class_datasheetanalyst import *
from libs.spreadsheet.class_datasheet import DataSheet

# 0. 初始化和参数设置
# 读取配置文件
CONFIG_FILE = r'D:\data\citystat\correction\config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE,encoding='UTF-8')

# 设置年份
YEAR = 2011

# 设置数据文件路径
DATA_FILE_PATH = config['default']['DATA_FILE_PATH']
FILES = [os.path.join(DATA_FILE_PATH,item) for item in os.listdir(DATA_FILE_PATH)]
ANALYSIS_FILE_PATH = config['default']['ANALYSIS_FILE_PATH']

#FILES = ['E:/data/citystat/datafile/3_10_土地资源_二_地级市_2001.xls']

# 设置数据行中间分隔规则
rule_fn = {'row_with_specified_first_word':Rule.row_with_specified_first_word}
row_location_split_fn = rule_fn[config['default']['row_location_split_fn']]
row_location_split_fn_param = {key:config['row_split_fn_param'].get(key,raw=True) for key in config['row_split_fn_param']}

# 注解匹配模式
statement_matcher = config['default']['statement_matcher']

# 设置变量分解规则
var_row_decomposer = {'unit': ('middle', config['var_row_decomposer'].get('unit',raw=True)),
                      'boundary': ('theone', config['var_row_decomposer'].get('boundary',raw=True))}

# 设置地区匹配规则
match_region_year = YEAR
match_region_down_level = int(config['prefecture2011']['match_region_down_level'])
match_region_correction = config['prefecture2011']['match_region_correction']

# 设置区域范围用词
correction_boundary = {key:config['boundary_correction'].get(key,raw=True) for key in config['boundary_correction']}
user_boundary = {}
#user_boundary = {key:config['prefecture2000_usr_boundary'].get(key,raw=True) for key in config['prefecture2000_usr_boundary']}

variable_pdata = None

for i in range(len(FILES)):
    if i < 0:
        continue
    file = FILES[i]
    print(i,': ',file)
    start_analysis = time.time()
    # 读取文件内容
    mdatasheet = DataSheet(file, type='dataframe')
    done_import = time.time()

    # 删除空行空列
    mdatasheet.add_to_work_flow({'name': '删除空行', 'operation': TransformToNoBlankRowsDF(dframe=mdatasheet.data)})
    mdatasheet.add_to_work_flow({'name': '删除空列', 'operation': TransformToNoBlankColumnsDF(dframe=mdatasheet.data)})
    done_handle_blank_row_column = time.time()

    # 定位数据表
    mdatasheet.add_to_work_flow({'name': '定位数据列', 'operation': LocateDataTableColumns(dframe=mdatasheet.data)})
    mdatasheet.add_to_work_flow({'name': '定位数据行', 'operation': LocateDataTableRows(dframe=mdatasheet.data,
                                                                                   data_columns=mdatasheet.location['data_column'],
                                                                                   split_fn=row_location_split_fn,**row_location_split_fn_param)})
    done_location_data_row_column = time.time()

    # 定位标题行
    mdatasheet.add_to_work_flow({'name': '定位标题行', 'operation': LocateTitle(dframe=mdatasheet.data,data_start=mdatasheet.location['data_row'][0])})
    # 定位单位行
    mdatasheet.add_to_work_flow({'name': '定位单位行', 'operation': LocateUnit(dframe=mdatasheet.data,data_start=mdatasheet.location['data_row'][0])})
    # 定位变量行
    mdatasheet.add_to_work_flow({'name': '定位变量行', 'operation': LocateColumnVariable(dframe=mdatasheet.data,
                                                                                    data_start=mdatasheet.location['data_row'][0],
                                                                                    title_row=mdatasheet.location['title'],
                                                                                    unit_row=mdatasheet.location['unit'])})

    mdatasheet.add_to_work_flow({'name': '定位其他行', 'operation': LocateOtherRows(dframe=mdatasheet.data,
                                                                               title_row=mdatasheet.location['title'],
                                                                               unit_row=mdatasheet.location['unit'],
                                                                               variable_row=mdatasheet.location['column_variable_row'],
                                                                               data_row=mdatasheet.location['data_row'])})

    done_location_title_unit_vars_rows = time.time()

    # 析出变量
    mdatasheet.add_to_work_flow({'name': '合并变量行', 'operation': ExtractColumnVariable(dframe=mdatasheet.data,
                                                                                     variable_column=mdatasheet.location['data_column'],
                                                                                     variable_row=mdatasheet.location['column_variable_row'])})
    mdatasheet.add_to_work_flow({'name': '分解变量', 'operation': ExtractColumnMultiVariable(column_variable=mdatasheet.info['column_variable'],
                                                                                         decomposer=var_row_decomposer,
                                                                                         double_column=len(set(range(mdatasheet.data.shape[1])) - set(mdatasheet.location['data_column'])) == 2)})
    done_extract_variables = time.time()

    # 析出标题和单位
    mdatasheet.add_to_work_flow({'name': '析出标题', 'operation': ExtractTitle(dframe=mdatasheet.data, title_row=mdatasheet.location['title'])})
    mdatasheet.add_to_work_flow({'name': '析出单位', 'operation': ExtractUnit(dframe=mdatasheet.data, unit_row=mdatasheet.location['unit'],
                                                                          units=mdatasheet.info.get('unit'),unit_len=len(mdatasheet.info['variable']))})

    mdatasheet.add_to_work_flow({'name': '析出注解', 'operation': ExtractStatement(dframe=mdatasheet.data,
                                                                               other_row=mdatasheet.location[
                                                                                   'other_row'],
                                                                               match_word=statement_matcher)})

    done_extract_title_unit = time.time()

    # 析出数据表格
    mdatasheet.add_to_work_flow({'name': '带行变量的数据表格', 'operation': ExtractDataTableWithRowVariable(dframe=mdatasheet.data,
                                                                                                   data_rows=mdatasheet.location['data_row'],
                                                                                                   data_columns=mdatasheet.location['data_column'])})

    done_extract_data_table = time.time()

    # 匹配地区
    mdatasheet.add_to_work_flow({'name': '匹配地区', 'operation': ReplaceRegion(regions=mdatasheet.info['data_table_with_row_variable'].iloc[:, 0],
                                                                            year=match_region_year, down_level=match_region_down_level,
                                                                            correction=match_region_correction)})

    done_region_matcher = time.time()

    # 定位非数据行
    mdatasheet.add_to_work_flow({'name': '解析非数字行', 'operation': ExtractnNonNumericRow(data_table=mdatasheet.info['data_table_with_row_variable'])})

    done_location_non_number_row = time.time()

    # 纠正区域范围用词错误
    mdatasheet.add_to_work_flow({'name': '纠正区域范围用词错误', 'operation': CorrectBoundary(boundary=mdatasheet.info.get('boundary'),
                                                                                    boundary_correction=correction_boundary,
                                                                                    title=mdatasheet.info['title'], user_boundary=user_boundary.get(mdatasheet.info['title']),
                                                                                    boundary_len=len(mdatasheet.info['variable']))})

    mdatasheet.add_to_work_flow({'name': '纠正非数字行', 'operation': CorrectNonNumericDataRow(data_table=mdatasheet.info['data_table_with_row_variable'],
                                                                                         replace={'．': '.'})})

    # 定位非数据行
    mdatasheet.add_to_work_flow({'name': '解析非数字行', 'operation': ExtractnNonNumericRow(data_table=mdatasheet.info['data_table_with_row_variable'])})

    done_windup = time.time()

    fmt = '\n读取文件内容所花费时间: {}'.format(done_import-start_analysis)
    fmt = ''.join([fmt, '\n删除空行空列所花费时间: {}'.format(done_handle_blank_row_column - done_import)])
    fmt = ''.join([fmt, '\n定位数据行列所花费时间: {}'.format(done_location_data_row_column - done_handle_blank_row_column)])
    fmt = ''.join([fmt, '\n定位标题单位和变量行所花费时间: {}'.format(done_location_title_unit_vars_rows - done_location_data_row_column)])
    fmt = ''.join([fmt, '\n解析变量所花费时间: {}'.format(done_extract_variables - done_location_title_unit_vars_rows)])
    fmt = ''.join([fmt, '\n解析标题和单位所花费时间: {}'.format(done_extract_title_unit - done_extract_variables)])
    fmt = ''.join([fmt, '\n解析数据表所花费时间: {}'.format(done_extract_data_table - done_extract_title_unit)])
    fmt = ''.join([fmt, '\n匹配地区所花费时间: {}'.format(done_region_matcher - done_extract_data_table)])
    fmt = ''.join([fmt, '\n定位非数据行所花费时间: {}'.format(done_location_non_number_row - done_region_matcher)])
    fmt = ''.join([fmt, '\n收尾工作所花费时间: {}'.format(done_windup - done_location_non_number_row)])

    #print(fmt)
    print(mdatasheet.report)
    mdatasheet.output_analysis(generated_path=ANALYSIS_FILE_PATH)

    pack_variable = mdatasheet.info['variable']
    pack_unit = mdatasheet.info['units']
    pack_boundary = mdatasheet.info['boundary']
    pack_data = pd.DataFrame({'variable':pack_variable,'unit':pack_unit,'boundary':pack_boundary},
                             columns=['variable','unit','boundary'])
    pack_data['title'] = mdatasheet.info['title']

    if variable_pdata is None:
        variable_pdata = pack_data
    else:
        variable_pdata = pd.concat([variable_pdata,pack_data])

variable_pdata.to_excel(os.path.join(ANALYSIS_FILE_PATH,'变量分析表.xlsx'))