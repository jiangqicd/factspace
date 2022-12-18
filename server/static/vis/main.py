#!/usr/bin/env python
# encoding: utf-8
#@author: jiangqi
#@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
#@contact: jiangqi@zjut.edu.com
#@file: main.py
#@time: 2022/11/16 12:50
import json

with open("./vaccine_correlation.json", 'r') as load_f:
    load_dict = json.load(load_f)
for k in load_dict:
    if load_dict[k]["vis"]["mark"]["type"]=="boxplot":
        load_dict[k]["task"]="aggregation"
save_dict = json.dumps(load_dict, indent=4)
with open("./vaccine_correlation.json", 'w') as file:
    file.write(save_dict)