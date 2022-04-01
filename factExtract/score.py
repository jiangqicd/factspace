import pandas as pd
import json
import copy

import numpy as np


# 封装针对一个fact计算分数的函数，然后获取每一个fact的值
def cal_each_fact(fact_ep, data):
    # impact
    # 该fact的subspace 就是 占了几个格子
    # record行数 * 所涉及的列数
    fact_records_num = 0
    fact_filter_attr = fact_ep['vis']['transform'][0]
    # 如果是oneof + range 的话 肯定有and
    Data = copy.deepcopy(data)
    if ('and' in fact_filter_attr['filter'].keys()):
        for fliter in fact_filter_attr['filter']['and']:
            if 'oneOf' in fliter:
                fact_filter_of = fliter
                fact_filter_attr_dict_oneof = fact_filter_of['field']  # Region
                fact_filter_oneof = fact_filter_of['oneOf'][0]  # MiddleEastandNorthernAfrica 不一定只有一个
                Data = Data[Data[fact_filter_attr_dict_oneof] == fact_filter_oneof]
            else:
                fact_filter_rg = fliter
                fact_filter_attr_dict_range = fact_filter_rg['field']  # HappinessRank
                fact_filter_range = fact_filter_rg['range']  # 一个取值范围 [1，53]
                Data = Data[Data[fact_filter_attr_dict_range] >= float(fact_filter_range[0])]
                Data = Data[Data[fact_filter_attr_dict_range] <= float(fact_filter_range[1])]
        fact_records_num = len(Data)
    # 如果只有oneof
    elif ('oneOf' in fact_filter_attr['filter'].keys()):
        fact_filter_attr_dict_oneof = fact_filter_attr['filter']['field']  # Region
        fact_filter_oneof = fact_filter_attr['filter']['oneOf'][0]  # MiddleEastandNorthernAfrica 不一定只有一个
        Data = Data[Data[fact_filter_attr_dict_oneof] == fact_filter_oneof]
        fact_records_num = len(Data[fact_filter_attr_dict_oneof])
    # 如果只有range
    elif ('range' in fact_filter_attr['filter'].keys()):
        fact_filter_attr_dict_range = fact_filter_attr['filter']['field']  # HappinessRank
        fact_filter_range = fact_filter_attr['filter']['range']  # 一个取值范围 [1，53]
        Data = Data[Data[fact_filter_attr_dict_range] >= float(fact_filter_range[0])]
        Data = Data[Data[fact_filter_attr_dict_range] <= float(fact_filter_range[1])]
        fact_records_num = len(Data[fact_filter_attr_dict_range])
    # print(fact_records_num)

    impact_score = fact_records_num / len(data)
    print(fact_records_num)
    print('impact_score: ')
    print(impact_score)

    # significance
    # 统计出现在有哪些类型
    # for key in vega_list:
    #    print(vega_list[key]['task'])'quantitative'
    # var_y = 0
    # distribution
    # 计算方差 方差越大score越高
    fact_filter_attr = fact_ep['vis']['transform'][0]
    # 如果是oneof + range 的话 肯定有and
    Data = copy.deepcopy(data)
    if ('and' in fact_filter_attr['filter'].keys()):
        for fliter in fact_filter_attr['filter']['and']:
            if 'oneOf' in fliter:
                fact_filter_of = fliter
                fact_filter_attr_dict_oneof = fact_filter_of['field']  # Region
                fact_filter_oneof = fact_filter_of['oneOf'][0]  # MiddleEastandNorthernAfrica 不一定只有一个
                Data = Data[Data[fact_filter_attr_dict_oneof] == fact_filter_oneof]
            else:
                fact_filter_rg = fliter
                fact_filter_attr_dict_range = fact_filter_rg['field']  # HappinessRank
                fact_filter_range = fact_filter_rg['range']  # 一个取值范围 [1，53]
                Data = Data[Data[fact_filter_attr_dict_range] >= float(fact_filter_range[0])]
                Data = Data[Data[fact_filter_attr_dict_range] <= float(fact_filter_range[1])]

    # 如果只有oneof
    elif ('oneOf' in fact_filter_attr['filter'].keys()):
        fact_filter_attr_dict_oneof = fact_filter_attr['filter']['field']  # Region
        fact_filter_oneof = fact_filter_attr['filter']['oneOf'][0]  # MiddleEastandNorthernAfrica 不一定只有一个
        Data = Data[Data[fact_filter_attr_dict_oneof] == fact_filter_oneof]

    # 如果只有range
    elif ('range' in fact_filter_attr['filter'].keys()):
        fact_filter_attr_dict_range = fact_filter_attr['filter']['field']  # HappinessRank
        fact_filter_range = fact_filter_attr['filter']['range']  # 一个取值范围 [1，53]
        Data = Data[Data[fact_filter_attr_dict_range] >= float(fact_filter_range[0])]
        Data = Data[Data[fact_filter_attr_dict_range] <= float(fact_filter_range[1])]

    var_y = 0
    c = 0
    for encoding in fact_ep['vis']['encoding'].keys():
        if fact_ep['vis']['encoding'][encoding]['type'] == 'quantitative':
            if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                var_y += np.var(d)
                c += 1
            elif fact_ep['vis']['encoding'][encoding]['aggregate'] == "mean":
                var_y += 0
                c += 1
            elif fact_ep['vis']['encoding'][encoding]['aggregate'] == "sum":
                var_y += 0
                c += 1
            elif fact_ep['vis']['encoding'][encoding]['aggregate'] == "min":
                var_y += 0
                c += 1
            elif fact_ep['vis']['encoding'][encoding]['aggregate'] == "max":
                var_y += 0
                c += 1
            else:
                d = list(Data[fact_ep['vis']['encoding'][encoding]['field']])
                var_y += np.var(d)
                c += 1
        elif fact_ep['vis']['encoding'][encoding]['type'] == "nominal":
            if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                var_y += np.var(d)
                c += 1
    if c == 0:
        var_y = 0
    else:
        var_y = var_y / c
    print('var_y: ')
    print(var_y)
    # derived_value

    # correlation

    return impact_score, var_y
