import pandas as pd
import json
import copy
import math

import numpy as np
import scipy.stats as stats


def standardization(data):
    mu = np.mean(data, axis=0)
    sigma = np.std(data, axis=0)
    return (data - mu) / sigma


def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range


def trendline(data):  # 拟合曲线
    order = 1
    index = [i for i in range(1, len(data) + 1)]  # x轴坐标
    # print(data)
    coeffs = np.polyfit(index, list(data), order)  # 曲线拟合
    #  k = coeffs[0] # 斜率
    # print(coeffs)
    return coeffs


def judge_slope(coeffs, data, degree, shake=1):
    tan_k = math.tan(degree * math.pi / 180)  # 注意弧度转化
    # print(coeffs[0])
    # print(tan_k)
    if coeffs[0] >= tan_k:
        return "1"
    elif coeffs[0] <= -tan_k:
        return "1"
    else:
        return get_shake(coeffs, data, shake)


def get_shake(coeffs, data, shake):
    count = 0
    for i, d in enumerate(data):  # i+1相当于横坐标，从1开始
        y = np.polyval(coeffs, i + 1)
        count += (y - d) ** 2
    # print("count: ",count)
    if count > shake:
        return "2"
    else:
        return "3"


# 封装针对一个fact计算分数的函数，然后获取每一个fact的值
def cal_each_fact(fact_ep, data):
    # impact
    # 该fact的subspace 就是 占了几个格子
    # record行数 * 所涉及的列数
    fact_records_num = 0
    if 'transform' in fact_ep['vis']:
        if fact_ep['vis']['transform']:
            fact_filter_attr = fact_ep['vis']['transform'][0]
    else:
        fact_filter_attr = []
    # 如果是oneof + range 的话 肯定有and
    Data = copy.deepcopy(data)
    # 统计每个fact所占的数据数
    if fact_filter_attr:
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
    else:
        fact_records_num = len(data)
    # print(fact_records_num)

    impact_score = fact_records_num / len(data)
    # print(fact_records_num)
    print('impact_score: ')
    print(impact_score)

    # # significance
    # # 统计出现在有哪些类型
    # # for key in vega_list:
    # #    print(vega_list[key]['task'])'quantitative'
    # # var_y = 0
    # # distribution
    # # 计算方差 方差越大score越高
    # fact_filter_attr = fact_ep['vis']['transform'][0]
    # # 如果是oneof + range 的话 肯定有and
    # Data = copy.deepcopy(data)
    # if ('and' in fact_filter_attr['filter'].keys()):
    #     for fliter in fact_filter_attr['filter']['and']:
    #         if 'oneOf' in fliter:
    #             fact_filter_of = fliter
    #             fact_filter_attr_dict_oneof = fact_filter_of['field']  # Region
    #             fact_filter_oneof = fact_filter_of['oneOf'][0]  # MiddleEastandNorthernAfrica 不一定只有一个
    #             Data = Data[Data[fact_filter_attr_dict_oneof] == fact_filter_oneof]
    #         else:
    #             fact_filter_rg = fliter
    #             fact_filter_attr_dict_range = fact_filter_rg['field']  # HappinessRank
    #             fact_filter_range = fact_filter_rg['range']  # 一个取值范围 [1，53]
    #             Data = Data[Data[fact_filter_attr_dict_range] >= float(fact_filter_range[0])]
    #             Data = Data[Data[fact_filter_attr_dict_range] <= float(fact_filter_range[1])]
    #
    # # 如果只有oneof
    # elif ('oneOf' in fact_filter_attr['filter'].keys()):
    #     fact_filter_attr_dict_oneof = fact_filter_attr['filter']['field']  # Region
    #     fact_filter_oneof = fact_filter_attr['filter']['oneOf'][0]  # MiddleEastandNorthernAfrica 不一定只有一个
    #     Data = Data[Data[fact_filter_attr_dict_oneof] == fact_filter_oneof]
    #
    # # 如果只有range
    # elif ('range' in fact_filter_attr['filter'].keys()):
    #     fact_filter_attr_dict_range = fact_filter_attr['filter']['field']  # HappinessRank
    #     fact_filter_range = fact_filter_attr['filter']['range']  # 一个取值范围 [1，53]
    #     Data = Data[Data[fact_filter_attr_dict_range] >= float(fact_filter_range[0])]
    #     Data = Data[Data[fact_filter_attr_dict_range] <= float(fact_filter_range[1])]

    # 针对不同的任务类型判断fact的统计显著性分数

    task = fact_ep['task']

    significance_score = 0

    if task == "distribution" or task == "derived_value" or task == "proportion":
        var_y = 0
        c = 0
        for encoding in fact_ep['vis']['encoding'].keys():
            if fact_ep['vis']['encoding'][encoding]['type'] == 'quantitative':
                if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                    d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                    d = normalization(d)
                    var_y += np.std(d)
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
                    d = normalization(d)
                    var_y += np.std(d)
                    c += 1
            elif fact_ep['vis']['encoding'][encoding]['type'] == "nominal":
                if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                    d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                    d = normalization(d)
                    var_y += np.std(d)
                    c += 1
        if c == 0:
            significance_score = 0
        else:
            significance_score = var_y / c
    elif task == "trend":
        var_y = 0
        c = 0
        trend = 0
        for encoding in fact_ep['vis']['encoding'].keys():
            if fact_ep['vis']['encoding'][encoding]['type'] == 'quantitative':
                if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                    d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                    d = normalization(d)
                    var_y += np.std(d)
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
                    d = normalization(d)
                    var_y += np.std(d)
                    c += 1
            elif fact_ep['vis']['encoding'][encoding]['type'] == "nominal":
                if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                    d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                    d = normalization(d)
                    var_y += np.std(d)
                    c += 1
        if c == 0:
            var_y = 0
        else:
            var_y = var_y / c
        if fact_ep['vis']['encoding']['y']['type'] == 'quantitative':
            value = list(Data[fact_ep['vis']['encoding']['y']['field']])
            coeffs = trendline(value)
            res = judge_slope(coeffs, value, degree=1, shake=1)
            if res == "1":
                trend = 0.8
        else:
            trend = 0
        significance_score = 0.2 * var_y + 0.8 * trend
    elif task == "correlation":
        var_y = 0
        c = 0
        for encoding in fact_ep['vis']['encoding'].keys():
            if fact_ep['vis']['encoding'][encoding]['type'] == 'quantitative':
                if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                    d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                    d = normalization(d)
                    var_y += np.std(d)
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
                    d = normalization(d)
                    var_y += np.std(d)
                    c += 1
            elif fact_ep['vis']['encoding'][encoding]['type'] == "nominal":
                if fact_ep['vis']['encoding'][encoding]['aggregate'] == "count":
                    d = list(Data[fact_ep['vis']['encoding'][encoding]['field']].value_counts())
                    d = normalization(d)
                    var_y += np.std(d)
                    c += 1
        if c == 0:
            var_y = 0
        else:
            var_y = var_y / c
        if fact_ep['vis']['encoding']['x']['type'] == 'quantitative' and fact_ep['vis']['encoding']['y'][
            'type'] == 'quantitative' and len(list(Data[fact_ep['vis']['encoding']['x']['field']])) >= 2 and len(
            list(Data[fact_ep['vis']['encoding']['y']['field']])) >= 2:
            corr = abs(stats.pearsonr(list(Data[fact_ep['vis']['encoding']['x']['field']]),
                                      list(Data[fact_ep['vis']['encoding']['y']['field']]))[0])
        else:
            corr = 0
        significance_score = corr * 0.8 + var_y * 0.2
    else:
        significance_score = 0
    print("significance_score:")
    print(significance_score)

    return impact_score, significance_score
