#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: cal_corr.py
# @time: 2022/11/27 12:33
import pandas as pd
from pandas.api.types import is_numeric_dtype

Table = ["pubg", "entrepreneurship", "vaccine_correlation"]
for i in Table:
    table_path = "./" + i + ".csv"
    table = pd.read_csv(table_path)
    label = [""]
    array = []
    person = []
    spearman = []
    kendall = []
    for attr in table.columns:
        if is_numeric_dtype(table[attr]):
            label.append(attr[:3]+attr[-2:])
            array.append(list(table[attr]))
    for m in range(len(array)):
        p = []
        p.append(label[m + 1])
        s = []
        s.append(label[m + 1])
        k = []
        k.append(label[m + 1])
        for n in range(len(array)):
            x = pd.Series(array[m])
            y = pd.Series(array[n])
            p.append(x.corr(y, method="pearson"))
            s.append(x.corr(y, method="spearman"))
            k.append(x.corr(y, method="kendall"))
        person.append(p)
        spearman.append(s)
        kendall.append(k)
    df_person = pd.DataFrame(data=person, columns=label)
    df_spearman = pd.DataFrame(data=spearman, columns=label)
    df_kendall = pd.DataFrame(data=kendall, columns=label)
    df_person.to_csv("../server/static/data/" + i + "_person.csv",index=None)
    df_spearman.to_csv("../server/static/data/" + i + "_spearman.csv",index=None)
    df_kendall.to_csv("../server/static/data/" + i + "_kendall.csv",index=None)
