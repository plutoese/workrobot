# coding = UTF-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# machine_classfied_ldmwp.py
# @简介：用scikit-learn估计器分类
# @作者：Glen
# @日期：2016.8.13
# @资料来源：Python数据挖掘入门与实践
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

# --------------------------------------------------
# 用Python编写的scikit-learn库，实现了一系列数据挖掘算法，
# 提供通用编程接口、标准化的测试和调参工具。
# 基本概念：
# - 估计器(Estimator)：用于分类、聚类和回归处理
# - 转换器(Transformer)：用于数据预处理和数据转换
# - 流水线(Pipeline)：组合数据挖掘流程，便于再次使用
# --------------------------------------------------

# ------------------------------------------
# scikit-learn估计器
# 估计器用于分类任务，主要包括以下两个函数。
# - fit()：训练算法，设置内部参数
# - predict()：参数为测试集。
# ------------------------------------------

# ----------------------------------------
# 近邻算法
# 计算近邻的重要之处在于对距离的度量
# 常用的度量方法有：欧式距离、曼哈顿距离和余弦距离
# 距离的选择方式对结果可能会产生重要的影响
# -----------------------------------------

import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.grid_search import GridSearchCV
from collections import defaultdict
from operator import itemgetter

# 导入数据
F = open(r'E:\github\workrobot\workrobot\data\ceic\random_datasets.pkl', 'rb')
datasets = pickle.load(F)

dataset_choosed = datasets[0]

# 变量的中英文转换
columns_chinese = dataset_choosed.columns
columns_english = ['_'.join(['v',str(item)]) for item in range(len(columns_chinese))]
columns_mapping = dict(zip(columns_english, columns_chinese))

# 设定数据框的新变量
dataset_choosed.columns = columns_english

# 分类数据
y = dataset_choosed['v_0'].gt(dataset_choosed['v_0'].mean())
x = dataset_choosed.iloc[:,range(1,len(columns_english))]

# 划分数据集
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=14)

# K近邻分类器
estimator = KNeighborsClassifier()
# 估计
estimator.fit(x_train, y_train)

# 预测
y_predicted = estimator.predict(x_test)

# 打印结果
accuracy = np.mean(y_test == y_predicted) * 100
print('The accuracy is {0:.1f}%.'.format(accuracy))

# 交叉检验
scores = cross_val_score(estimator,x,y,scoring='accuracy')
average_accuracy = np.mean(scores) * 100
print('The average accuracy is {0:.1f}%.'.format(average_accuracy))

# 设置参数
avg_scores = []
all_scores = []
parameter_values = list(range(1,21))
for n_neighbors in parameter_values:
    estimator = KNeighborsClassifier(n_neighbors=n_neighbors)
    scores = cross_val_score(estimator, x, y, scoring='accuracy')
    avg_scores.append(np.mean(scores))
    all_scores.append(scores)

# 标准预处理
x_transformed = MinMaxScaler().fit_transform(x)
estimator = KNeighborsClassifier()
transformed_scores = cross_val_score(estimator, x_transformed, y, scoring='accuracy')
print('The average accuracy is {0:.1f}%.'.format(np.mean(transformed_scores) * 100))

# 流水线
scaling_pipeline = Pipeline([('scale', MinMaxScaler()), ('predict', KNeighborsClassifier())])
scores = cross_val_score(scaling_pipeline, x, y, scoring='accuracy')
print('The pipeline scored an average accuracy is {0:.1f}%.'.format(np.mean(scores) * 100))

# ---------------------------------------
# 分类算法 —— 决策树
# @简介：一种有监督的机器学习算法
# @方法：scikit-learn库实现了分类回归树(CART)
# ----------------------------------------

print('-'*50)
print('CART')

# 创建对象
clf = DecisionTreeClassifier(random_state=14)
transformed_scores = cross_val_score(clf, x_transformed, y, scoring='accuracy')
print('The average accuracy is {0:.1f}%.'.format(np.mean(transformed_scores) * 100))

# 随机森林
clf = RandomForestClassifier(random_state=14)
transformed_scores = cross_val_score(clf, x_transformed, y, scoring='accuracy')
print('The average accuracy is {0:.1f}%.'.format(np.mean(transformed_scores) * 100))

'''
# 搜索最佳参数
parameter_space = {'max_features':[2, 40, 'auto'],
                   'n_estimators': [100, ],
                   'criterion': ['gini', 'entropy'],
                   'min_samples_leaf': [2, 4, 6]}
clf = RandomForestClassifier(random_state=14)
grid = GridSearchCV(clf, parameter_space)
grid.fit(x, y)
print('Accuracy: {0:.1f}%.'.format(grid.best_score_ * 100))
print(grid.best_estimator_)'''

# --------------------------
# 亲和性分析 —— 电影推荐
# @算法：Apriori算法
# __________________________

print('\n---------------Apriori-------------')

# 导入数据
ratings_filename = r'E:\data\bigdata\movies\u.data'
all_ratings = pd.read_csv(ratings_filename, delimiter='\t', header=None,
                          names = ['UserID', 'MovieID', 'Rating', 'Datetime'])
all_ratings['Datetime'] = pd.to_datetime(all_ratings['Datetime'], unit='s')
print(all_ratings[:5])

all_ratings['Favorable'] = all_ratings['Rating'] > 3
print(all_ratings[10:15])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 变量all_ratings
#     UserID  MovieID  Rating            Datetime Favorable
# 10      62      257       2 1997-11-12 22:07:14     False
# 11     286     1014       5 1997-11-17 15:38:45      True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 选择前200名用户的打分数据用作训练集
ratings = all_ratings[all_ratings['UserID'].isin(range(200))]

# 只包含用户喜欢某部电影的数据行
favorable_ratings = ratings[ratings["Favorable"]]

# 字典，key是用户id，value是该用户喜欢的电影的id集合
favorable_reviews_by_users = dict((k, frozenset(v.values)) for k, v in favorable_ratings.groupby("UserID")["MovieID"])
for k, v in favorable_ratings.groupby("UserID")['MovieID']:
    print(k,' --> ',list(v))

# 每部电影影迷的数量
num_favorable_by_movie = ratings[["MovieID", "Favorable"]].groupby("MovieID").sum()
print(num_favorable_by_movie.sort_values("Favorable", ascending=False)[:5])

print('----------------------Start---------------------')

def find_frequent_itemsets(favorable_reviews_by_users, k_1_itemsets, min_support):
    counts = defaultdict(int)
    for user, reviews in favorable_reviews_by_users.items():
        for itemset in k_1_itemsets:
            if itemset.issubset(reviews):
                for other_reviewed_movie in reviews - itemset:
                    current_superset = itemset | frozenset((other_reviewed_movie,))
                    counts[current_superset] += 1
    return dict([(itemset, frequency) for itemset, frequency in counts.items() if frequency >= min_support])


# 频繁项集
frequent_itemsets = {}  # itemsets are sorted by length
# 最小支持度
min_support = 50

#生成初始的频繁项集
frequent_itemsets[1] = dict((frozenset((movie_id,)), row["Favorable"])
                                for movie_id, row in num_favorable_by_movie.iterrows()
                                if row["Favorable"] > min_support)
print(frequent_itemsets)

print("There are {} movies with more than {} favorable reviews".format(len(frequent_itemsets[1]), min_support))
sys.stdout.flush()

# 遍历生成频繁项集
for k in range(2, 20):
    # Generate candidates of length k, using the frequent itemsets of length k-1
    # Only store the frequent itemsets
    cur_frequent_itemsets = find_frequent_itemsets(favorable_reviews_by_users, frequent_itemsets[k-1],
                                                   min_support)
    if len(cur_frequent_itemsets) == 0:
        print("Did not find any frequent itemsets of length {}".format(k))
        sys.stdout.flush()
        break
    else:
        print("I found {} frequent itemsets of length {}".format(len(cur_frequent_itemsets), k))
        #print(cur_frequent_itemsets)
        sys.stdout.flush()
        frequent_itemsets[k] = cur_frequent_itemsets
# We aren't interested in the itemsets of length 1, so remove those
del frequent_itemsets[1]

# 频繁项集生成完毕，现在需要生成一些统计量
# Now we create the association rules. First, they are candidates until the confidence has been tested
candidate_rules = []
for itemset_length, itemset_counts in frequent_itemsets.items():
    for itemset in itemset_counts.keys():
        for conclusion in itemset:
            premise = itemset - set((conclusion,))
            candidate_rules.append((premise, conclusion))
print("There are {} candidate rules".format(len(candidate_rules)))

# candidate_rules变量是字典，key是前提，value是结论
print(candidate_rules[:5])

# 计算每条规则的置信度
# Now, we compute the confidence of each of these rules. This is very similar to what we did in chapter 1
correct_counts = defaultdict(int)
incorrect_counts = defaultdict(int)
for user, reviews in favorable_reviews_by_users.items():
    for candidate_rule in candidate_rules:
        premise, conclusion = candidate_rule
        if premise.issubset(reviews):
            if conclusion in reviews:
                correct_counts[candidate_rule] += 1
            else:
                incorrect_counts[candidate_rule] += 1
rule_confidence = {candidate_rule: correct_counts[candidate_rule] / float(correct_counts[candidate_rule] + incorrect_counts[candidate_rule])
              for candidate_rule in candidate_rules}

# 根据置信度排序
sorted_confidence = sorted(rule_confidence.items(), key=itemgetter(1), reverse=True)
for index in range(5):
    print("Rule #{0}".format(index + 1))
    (premise, conclusion) = sorted_confidence[index][0]
    print("Rule: If a person recommends {0} they will also recommend {1}".format(premise, conclusion))
    print(" - Confidence: {0:.3f}".format(rule_confidence[(premise, conclusion)]))
    print("")

# ---------------------------------------
# 用转换器抽取特征
# ----------------------------------------

# 模型就是用来简化世界，特征抽取也是一样。
# 降低复杂性有好处，但也有不足，简化会忽略很多细节。

# 这里的例子用adult数据集，预测一个人是否年收入多于五万美元

adult_filename = r'E:\data\bigdata\adult\adult.data'
adult = pd.read_csv(adult_filename, header=None, names=["Age", "Work-Class", "fnlwgt", "Education",
                                                        "Education-Num", "Marital-Status", "Occupation",
                                                        "Relationship", "Race", "Sex", "Capital-gain",
                                                        "Capital-loss", "Hours-per-week", "Native-Country",
                                                        "Earnings-Raw"])
print(adult.head)
