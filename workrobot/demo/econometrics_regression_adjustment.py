# coding = UTF-8

# ===================================
# 这个程序用来实现Regression-Adjustment
# ===================================

import numpy as np
from libs.imexport.class_statadata import Statadata
from libs.statmodel.class_lm import Lm
from rpy2.robjects.packages import importr
from libs.embeddedR.class_renv import REnv

# 1. 导入数据
stata_file = r'd:\data\userdata\jtrain2.dta'
stdata = Statadata(stata_file)
raw_data = stdata.read()

# 2. 比较两组对象
grouped = raw_data.groupby('train')
compared = grouped.aggregate(np.mean)
print(compared.T)

for _, group in grouped:
    print(group.mean())

# 3. 回归
reg_obj = Lm(data=raw_data, formula = 're78 ~ train')
call_obj = reg_obj()
print(reg_obj.coefs)

reg_obj = Lm(data=raw_data, formula = 're78 ~ train + re74 + re75 + age + agesq + nodegree + married + black + hisp')
call_obj = reg_obj()
print(reg_obj.coefs)

# 4. 自助法



