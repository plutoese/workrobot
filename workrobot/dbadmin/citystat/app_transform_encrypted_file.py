# coding = UTF-8

# --------------------------------
# 这个程序用来转换加密的xls文件
# ---------------------------------

import os
from libs.imexport.class_Excel import Excel
from libs.imexport.class_winexcel import WinExcel

# 读取文件
source_path = r'E:\data\citystat\origin'
target_path = r'E:\data\citystat\done'
file_path = os.listdir(source_path)

for item in file_path:
    origin_path = os.path.join(source_path,item)
    if os.path.isdir(origin_path):
        target_more_path = os.path.join(target_path,item)
        os.mkdir(target_more_path)
        for inner_item in os.listdir(origin_path):
            inner_file = os.path.join(origin_path,inner_item)

            mexcel = WinExcel(inner_file)
            rdata = mexcel.read()
            mexcel.close()

            target_file = os.path.join(target_more_path, inner_item)
            print(target_file)
            moutexcel = Excel(target_file)
            moutexcel.new().append(rdata, 'sheet1')
            moutexcel.close()
    else:
        origin_file = os.path.join(source_path,item)
        mexcel = WinExcel(origin_file)
        rdata = mexcel.read()
        #mexcel.close()

        target_file = os.path.join(target_path,item)
        moutexcel = Excel(target_file)
        print(rdata)
        moutexcel.new().append(rdata, 'sheet1')
        moutexcel.close()

