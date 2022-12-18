#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: res_cal.py
# @time: 2022/11/30 13:06
import pandas as pd
import json
from numpy import transpose
import numpy as np
import matplotlib.pyplot as plt

Answer = {'embedding-0': 'B', 'embedding-1': 'C', 'embedding-2': 'A', 'embedding-3': 'C', 'embedding-4': 'D'}
Res_embedding = []
Res_time = []
Res_path = []
ti=[]
score=[]
path = "./survey_res"
with open(path, 'r') as load_f:
    load_dict = json.load(load_f)
for k in load_dict:
    s = []
    t = []
    r = []
    for i in load_dict[k]:
        if i in list(Answer.keys()):
            if Answer[i] == load_dict[k][i]:
                r.append(1)
            else:
                r.append(-1)
        if "path" in i:
            s.append(int(load_dict[k][i]))
            score.append(int(load_dict[k][i]))
        if "time" in i:
            t.append(load_dict[k][i])
            ti.append(load_dict[k][i])
    Res_path.append(s)
    Res_time.append(t)
    Res_embedding.append(r)
Res_embedding = transpose(Res_embedding).tolist()
Res_path = transpose(Res_path).tolist()
Res_time = transpose(Res_time).tolist()
print(Res_embedding)
print(Res_path)
print(Res_time)
data = []
err = []
for i in Res_time:
    data.append(np.mean(i))
    print(np.mean(i))
    err.append(np.std(i))
print(data)
y = data
x = np.arange(1, len(y) + 1) / 2
print(y)
print(x)
y_err = err
print(y_err)
print(np.mean(score))
print(np.std(score))
fig, ax = plt.subplots(figsize=(6, 5), dpi=80)
err_attr = {"elinewidth": 2, "ecolor": "black", "capsize": 6}  # 这是误差棒的属性
bar1 = ax.bar(x, y, yerr=y_err, error_kw=err_attr, width=0.25)
ax.set_ylim(bottom=0.5)  # y轴最小值从0.5开始
ax.set_ylabel("Time", color='black', fontsize=20)
ax.tick_params(axis='y', labelcolor='black', labelsize=15)
ax.set_xticks(x)

legends = ['T1', 'T2', 'T3', 'T4', 'T5']
ax.set_xticklabels(legends, fontsize=15)
plt.tight_layout()
plt.show()
