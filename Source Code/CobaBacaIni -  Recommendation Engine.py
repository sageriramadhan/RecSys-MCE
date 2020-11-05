#!/usr/bin/env python
# coding: utf-8

# ## Import Library
# 

# In[2]:


get_ipython().system('pip install mysql.connector')


# In[3]:


import pandas as pd
from collections import Counter
import mysql.connector as sql


# ## Load Data from MySQL DB
# 

# In[5]:


db_connection = sql.connect(host='remotemysql.com', database='Z17DZVttfB', user='Z17DZVttfB', password='7Uw9X4gOto')
db_cursor = db_connection.cursor()
db_cursor.execute('SELECT * FROM simulation')
table_rows = db_cursor.fetchall()


# In[11]:


df = pd.DataFrame(table_rows)
df.columns = df.iloc[0]
df = df[1:]


# ## Load Data from CSV

# In[9]:


dataset = "reviews_2.csv"
DataFrame = pd.read_csv(dataset, engine='python', error_bad_lines=False, delimiter=";")
DataFrame.head(10)


# ## PreProcessing Part 1 : Filtering Column

# In[3]:


DataFrame = DataFrame.filter(items=['reviewerName', 'title', 'reviewerRating'])
DataFrame.head(10)


# ## PreProcessing Part 2 : Check Null Value
# 

# In[4]:


column = ['reviewerName', 'title', 'reviewerRating']
for columns in column:
    missing = DataFrame[columns].isnull().value_counts()
    print(missing)


# ## PreProcessing Part 3 : Remove non-ASCII Char

# In[5]:


DataFrame = DataFrame.dropna(how='any')

DataFrame = DataFrame[~DataFrame.reviewerName.str.contains(r'[^\x00-\x7F]')]
DataFrame = DataFrame[~DataFrame.title.str.contains(r'[^\x00-\x7F]')]

DataFrame = DataFrame.reset_index(drop=True)

DataFrame.head(10)


# In[6]:


Counter(DataFrame['title'].head(20))


# ## Visualize

# In[7]:


df1 = DataFrame.set_index(['reviewerName', 'title']).sort_index()
df1.head(10)


# ## Preparation : Conver DataTable to Dict

# In[8]:


d = (DataFrame.groupby('reviewerName')['title','reviewerRating'].apply(lambda x: dict(x.values)).to_dict())


# ## Modelling : Euclidean Distance

# In[9]:


def jarak_similarity(prefs,person1,person2):
    si = {} 
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1    
    if len(si) == 0: 
        return 0
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item],2) 
                          for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sum_of_squares)


# In[10]:


def preferensi_mirip(prefs, person, n=10, similarity = jarak_similarity):
    scores = [(similarity(prefs,person,other), other)
            for other in prefs if other!=person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


# In[11]:


def get_recommendations(prefs, person, n=10, similarity = jarak_similarity):
    totals = {} 
    simSums = {}
    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs, person, other)
        if sim <= 0:
            continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item,0) 
                totals[item] += prefs[other][item] * sim
                simSums.setdefault(item,0)
                simSums[item] += sim
    rankings = [(total/simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings[0:n]


# ## Result

# In[12]:


preferensi_mirip(d, 'Witsqadianto')


# In[13]:


get_recommendations(d, 'Witsqadianto')

