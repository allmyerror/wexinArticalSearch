# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     config.py
   Description :
   Author :       Sean
   date：          2017/12/3
-------------------------------------------------
   Change Activity:
                   2017/12/3:
-------------------------------------------------
"""
from pypinyin import lazy_pinyin

# 微信文章探索的关键字
KEYWORD = '风景'

# mongoDB配置
MONGO_URL = 'localhost'
MONGO_DB = 'wexinArticle'
MONGO_TABLE = ''.join(lazy_pinyin(KEYWORD))

# 最大重试次数
MAXCOUNT = 5