# !/usr/bin/env python
# -*- coding:utf-8 -*-
user = "12306账号"
password = "12306账号密码"
username = "若快打码平台账号"
password1 = "若快打码平台密码"
import time

def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        time.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False