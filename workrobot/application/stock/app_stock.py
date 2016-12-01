# coding = UTF-8

from libs.imexport.class_Excel import Excel
import os
import pandas as pd
import pickle
import re

# 0. 参数设置
STORE = False
LOAD = True

Path = r'E:\data\stock'
target_file = r'（新表头-最终的表格）我国上市公司交叉持股分析.xlsx'

json_file = os.path.join(Path,'datafile.pkl')

main_file = r'持股数据主表-2004-2016年6月我国上市公司交叉持股情况.xls'
industry_file = r'（含行业信息）2004年9月-2016年6月上市公司行业分类情况.xls'
industry_plus_file = r'（按最新股票名称）1992年5月24日-2016年6月30日上市公司行业分类情况.xls'
business_one_file = r'1最新调整数据（年报）-（含成本）2004年9月-2016年6月上市公司经营数据.xls'
business_two_file = r'2最新调整数据（年报）-（含成本）2004年9月-2016年6月上市公司经营数据.xls'
financial_file = r'最新调整数据（年报）-2004年9月-2016年6月我国上市公司主要财务指标.xls'

if STORE:
    # 1. 读入最终表头
    mexcel = Excel(os.path.join(Path,target_file))
    mdata = mexcel.read()
    target_title_header = mdata[0]

    # 2. 读入数据表
    mexcel = Excel(os.path.join(Path, main_file))
    mdata = mexcel.read()
    main_pdata = pd.DataFrame(mdata[1:],columns=mdata[0])

    mexcel = Excel(os.path.join(Path, industry_file))
    mdata = mexcel.read()
    industry_pdata_one = pd.DataFrame(mdata[1:],columns=mdata[0])

    mexcel = Excel(os.path.join(Path, industry_plus_file))
    mdata = mexcel.read()
    industry_plus_pdata = pd.DataFrame(mdata[1:], columns=mdata[0])

    industry_pdata = pd.concat([industry_pdata_one,industry_plus_pdata])

    mexcel = Excel(os.path.join(Path, business_one_file))
    mdata = mexcel.read()
    business_one_pdata = pd.DataFrame(mdata[1:], columns=mdata[0])

    mexcel = Excel(os.path.join(Path, business_two_file))
    mdata = mexcel.read()
    business_two_pdata = pd.DataFrame(mdata[1:], columns=mdata[0])

    business_pdata = pd.concat([business_one_pdata, business_two_pdata])

    mexcel = Excel(os.path.join(Path, financial_file))
    mdata = mexcel.read()
    financial_pdata = pd.DataFrame(mdata[1:], columns=mdata[0])

    print(main_pdata.columns)
    print(industry_pdata_one.columns)
    print(industry_plus_pdata.columns)
    print(industry_pdata.columns)
    print(business_one_pdata.columns)
    print(business_two_pdata.columns)
    print(business_pdata.columns)
    print(financial_pdata.columns)

    pickle.dump({'main':main_pdata,'industry_one':industry_pdata_one,'industry_two':industry_plus_pdata,
               'industry':industry_pdata,'business_one':business_one_pdata,'business_two':business_two_pdata,
               'business':business_pdata,'financial':financial_pdata,'header':target_title_header},
                open(json_file, 'wb'))

if LOAD:
    P = pickle.load(open(json_file,'rb'))
    header = P.get('header')
    main_pdata = P.get('main')
    industry_pdata = P.get('industry')
    business_pdata = P.get('business')
    financial_pdata = P.get('financial')
    print(main_pdata)
    co_1 = []
    co_2 = []
    co_3 = []
    co_4 = []
    for head in header:
        if head in main_pdata.columns:
            co_1.append(head)
            if re.match('上市公司代码_ComCd',head) is None:
                continue
        if head in industry_pdata.columns:
            co_2.append(head)
            if re.match('上市公司代码_ComCd',head) is None:
                continue
        if head in business_pdata.columns:
            co_3.append(head)
            if re.match('上市公司代码_ComCd',head) is None:
                continue
        if head in financial_pdata.columns:
            co_4.append(head)
    print(co_1)
    print(co_2)
    print(co_3)
    print(co_4)
    pdata_1 = main_pdata[co_1]
    pdata_2 = industry_pdata[co_2]
    pdata_3 = business_pdata[co_3]
    pdata_4 = financial_pdata[co_4]

    print('first',pdata_1.shape)

    pdata_2 = pdata_2.drop_duplicates(subset='上市公司代码_ComCd')
    pdata_23 = pdata_2.drop_duplicates(subset=pdata_2.columns)
    print('compared',pdata_2.shape,pdata_23.shape)

    pdata_3 = pdata_3.drop_duplicates(subset='上市公司代码_ComCd')
    pdata_33 = pdata_3.drop_duplicates(subset=pdata_3.columns)
    print('compared', pdata_3.shape, pdata_33.shape)

    pdata_4 = pdata_4.drop_duplicates(subset='上市公司代码_ComCd')
    pdata_43 = pdata_4.drop_duplicates(subset=pdata_4.columns)
    print('compared', pdata_4.shape, pdata_43.shape)

    result = pd.merge(pdata_1, pdata_2, how='left', on=['上市公司代码_ComCd'])
    result = pd.merge(result, pdata_3, how='left', on=['上市公司代码_ComCd'])
    result = pd.merge(result, pdata_4, how='left', on=['上市公司代码_ComCd'])

    print('last',result.shape)
    result.to_excel(os.path.join(Path, 'result.xlsx'))
