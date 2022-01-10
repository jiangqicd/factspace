#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: test.py.py
# @time: 2022/1/10 19:51
from itertools import combinations

a = [1, 2, 3]
b = [1]
for i in list(combinations(a, 2)):
    print(list(i))
print(len(set(a) & set(b)))
