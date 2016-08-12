# coding = UTF-8

import sys
import pandas as pd
from collections import defaultdict

# Learning Data Mining with Python
# 书中例子的实现

# 4. 亲和性分析
# 简介：电影推荐，Apriori算法
# 4.1 导入数据
ratings_filename = r'E:\data\bigdata\movies\u.data'
all_ratings = pd.read_csv(ratings_filename, delimiter='\t', header=None,
                          names = ['UserID', 'MovieID', 'Rating', 'Datetime'])
all_ratings['Datetime'] = pd.to_datetime(all_ratings['Datetime'], unit='s')
print(all_ratings[:5])

all_ratings['Favorable'] = all_ratings['Rating'] > 3
print(all_ratings[10:15])

# Sample the dataset.
# You can try increasing the size of the sample, but the run time will be considerably longer
ratings = all_ratings[all_ratings['UserID'].isin(range(200))]
print(ratings[0:5])

favorable_ratings = ratings[ratings["Favorable"]]
print(favorable_ratings[0:5])

# We are only interested in the reviewers who have more than one review
favorable_reviews_by_users = dict((k, frozenset(v.values)) for k, v in favorable_ratings.groupby("UserID")["MovieID"])
for k, v in favorable_ratings.groupby("UserID")['MovieID']:
    print(k,' --> ',list(v))

# Find out how many movies have favourable ratings
num_favorable_by_movie = ratings[["MovieID", "Favorable"]].groupby("MovieID").sum()
print(num_favorable_by_movie.sort_values("Favorable", ascending=False)[:5])

print('-------------------Apriori------------------')



def find_frequent_itemsets(favorable_reviews_by_users, k_1_itemsets, min_support):
    counts = defaultdict(int)
    for user, reviews in favorable_reviews_by_users.items():
        for itemset in k_1_itemsets:
            if itemset.issubset(reviews):
                for other_reviewed_movie in reviews - itemset:
                    current_superset = itemset | frozenset((other_reviewed_movie,))
                    counts[current_superset] += 1
    return dict([(itemset, frequency) for itemset, frequency in counts.items() if frequency >= min_support])


frequent_itemsets = {}  # itemsets are sorted by length
min_support = 50

# k=1 candidates are the isbns with more than min_support favourable reviews
frequent_itemsets[1] = dict((frozenset((movie_id,)), row["Favorable"])
                                for movie_id, row in num_favorable_by_movie.iterrows()
                                if row["Favorable"] > min_support)
print(frequent_itemsets)

print("There are {} movies with more than {} favorable reviews".format(len(frequent_itemsets[1]), min_support))
sys.stdout.flush()

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
