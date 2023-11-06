#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: preprocessing.py
# @time: 2022/2/27 15:55
from sklearn.cluster import DBSCAN
from sklearn.metrics import pairwise_distances
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from scipy.stats import ortho_group
from procrustes import orthogonal
from logic_distence.get_logic_dis import logic_dis_extractor
from gvae.data_utils import visvae
from factExtract.extractor import Extractor
from factExtract.score import cal_each_fact
from gvae import vis_grammar
from gvae import vis_vae
from gvae import train
from gvae import data_utils
from storylineGenerate.storyGenerator import StoryGenerator
from sklearn.decomposition import PCA
from sklearn import preprocessing
import json
import time


# distance_compution
def distance_compution(Path):
    for path in Path:
        print("开始计算" + path + "距离矩阵")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        distance_path = "../server/static/data/distance_" + path + ".json"
        logical_distance_path = "../server/static/data/logical_distance_" + path + ".json"
        visual_distance_path = "../server/static/data/visual_distance_" + path + ".json"
        vec_path = "../server/static/data/vec_" + path + ".json"
        vis_display_vegalite_data_path = "../server/static/vis/" + path + ".json"

        tsne = TSNE(n_components=2, perplexity=25)
        pca20 = PCA(n_components=20)

        with open(vis_display_vegalite_data_path, 'r') as load_f:
            load_dict = json.load(load_f)

        # 计算逻辑距离
        lde = logic_dis_extractor(load_dict)

        logic_distence_matrix_org = lde.logic_detect()

        standard = preprocessing.MinMaxScaler()

        logic_distence_matrix_org_standard = list(standard.fit_transform(logic_distence_matrix_org))

        logic_distence_matrix = pca20.fit_transform(logic_distence_matrix_org_standard)

        logic_distence_matrix = list(standard.fit_transform(logic_distence_matrix))

        ld = tsne.fit_transform(logic_distence_matrix_org_standard)

        ld = list(standard.fit_transform(ld))

        # 计算encoding距离
        # model_path
        model_path = "../gvae/trained/" + path + "/vae_H256_D256_C888_333_L20_B200.hdf5"
        # rule_path
        rule_path = "../gvae/trainingdata/" + path + "/rules-cfg.txt"
        # input_data_path
        input_data_path = "../data/" + path + ".txt"
        # encoding data

        encoding_data = []
        with open(input_data_path, 'r') as inputs:
            for line in inputs:
                line = line.strip()
                encoding_data.append(line)

        outputspec, z, id = visvae(encoding_data, rule_path, model_path)

        z = list(standard.fit_transform(z))

        ed = tsne.fit_transform(z)

        ed = list(standard.fit_transform(ed))

        z = list(standard.fit_transform(z))

        visual_distence_matrix = pairwise_distances(z, metric='euclidean')

        visual_distence_matrix = 1 / (visual_distence_matrix + 1)

        visual_distence_matrix_standard = list(standard.fit_transform(visual_distence_matrix))

        comb_dis_n_standard = 0.5 * np.array(visual_distence_matrix_standard) + 0.5 * np.array(
            logic_distence_matrix_org_standard)

        d = tsne.fit_transform(comb_dis_n_standard)
        d = list(standard.fit_transform(d))

        logical_dis = {}
        visual_dis = {}
        distance = {}
        vec = {}
        for i, k in enumerate(load_dict):
            distance[k] = {"x": str(d[i][0]), "y": str(d[i][1])}
            logical_dis[k] = {"lx": str(ld[i][0]), "ly": str(ld[i][1])}
            visual_dis[k] = {"ex": str(ed[i][0]), "ey": str(ed[i][1])}
            vec[k] = {"ld_vec": str(list(logic_distence_matrix_org_standard[i])), "ed_vec": str(list(visual_distence_matrix_standard[i]))}

        logical_dis = json.dumps(logical_dis, indent=4)
        visual_dis = json.dumps(visual_dis, indent=4)
        vec = json.dumps(vec, indent=4)
        distance = json.dumps(distance, indent=4)
        with open(vec_path, 'w') as file:
            file.write(vec)
        with open(distance_path, 'w') as file:
            file.write(distance)
        with open(logical_distance_path, 'w') as file:
            file.write(logical_dis)
        with open(visual_distance_path, 'w') as file:
            file.write(visual_dis)


# data generation
def data_generation(Path):
    for path in Path:
        table_path = "../data/" + path + ".csv"
        vis_table_path = "../static/data/" + path + ".csv"
        encoding_input_data_path = "../data/" + path + ".txt"
        encoding_train_data_path = "../data/train_" + path + ".txt"
        vis_display_vegalite_data_path = "../server/static/vis/" + path + ".json"
        rule_path = "../gvae/trainingdata/" + path + "/rules-cfg.txt"
        training_data = "../gvae/trainingdata/" + path + "/"
        model_train_data_path = "../gvae/trainingdata/" + path + "/train.h5"
        model_save_path = "../gvae/trained/" + path + "/"
        extractor = Extractor(table_path=table_path,
                              vis_table_path=vis_table_path,
                              train_data_path=encoding_train_data_path,
                              vis_data_path=vis_display_vegalite_data_path,
                              encoding_input_path=encoding_input_data_path)
        print("开始提取" + path + "数据")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        extractor.dataPreprocessing()
        extractor.getVisList()
        print("开始训练" + path + "模型")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        model_training(encoding_train_data_path, rule_path, training_data)
        train.train(model_train_data_path, rule_path, model_save_path)


# model training
def model_training(data_path, rule_path, trainingdata_path):
    ## 1. build the CFG rules file
    max_len = data_utils.extract_rules(data_path, rule_path)
    train.MAX_LEN = max_len
    ## 2. generate the traning and testing datasets
    data_utils.generate_datasets(data_path, rule_path, trainingdata_path)


# JS divergence calculation
def JS_divergence_compution(Path):
    for path in Path:
        print("开始计算" + path + "Js散度")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        vis_display_vegalite_data_path = "../server/static/vis/" + path + ".json"

        with open(vis_display_vegalite_data_path, 'r') as load_f:
            load_dict = json.load(load_f)

        table_path = "../data/" + path + ".csv"

        Js_save_path = "../server/static/data/" + path + "_js_divergence.json"

        t = StoryGenerator(table_path, load_dict, Js_save_path, load_dict)

        t.get_JS_divs()


def score(Path):
    # Calculate the score
    for path in Path:
        print("正在计算" + path + "的得分")
        table_path = "../data/" + path + ".csv"
        vis_display_vegalite_data_path = "../server/static/vis/" + path + ".json"
        fact_score = []
        impact_values = []
        significance_values = []
        significance_values_formal = []
        impact_w = 0.4
        significance_w = 0.6
        table = pd.read_csv(table_path)
        with open(vis_display_vegalite_data_path, 'r') as load_f:
            load_dict = json.load(load_f)
        for key in load_dict:
            fact = load_dict[key]
            impact_values.append(cal_each_fact(fact, table)[0])
            if cal_each_fact(fact, table)[1] == cal_each_fact(fact, table)[1]:
                significance_values.append(cal_each_fact(fact, table)[1])
            else:
                significance_values.append(cal_each_fact(fact, table)[0])
        # print(significance_values)
        # Sum = sum(significance_values)
        # print("--------------------------------", Sum)
        # for i in range(len(significance_values)):
        #     fom = significance_values[i] / Sum
        #     print(fom)
        #     significance_values_formal.append(fom)
        for i in range(len(impact_values)):
            # print(impact_values[i])
            # print(significance_values_formal[i])
            fact_score.append(impact_w * impact_values[i] + significance_w * significance_values[i])

        Score = {}
        for i, k in enumerate(load_dict):
            # print(fact_score[i])
            Score[k] = fact_score[i]
        score_save_path = "../server/static/data/" + path + "_score.json"
        data = json.dumps(Score, indent=4)
        with open(score_save_path, 'w') as file:
            file.write(data)


def getTopic(Path):
    for path in Path:
        table_path = "../data/" + path + ".csv"
        vis_display_vegalite_data_path = "../server/static/vis/" + path + ".json"
        score_save_path = "../server/static/data/" + path + "_score.json"
        dis_path = "../server/static/data/distance_" + path + ".json"
        with open(dis_path, 'r') as load_f:
            distance = json.load(load_f)
        with open(score_save_path, 'r') as load_f:
            fact_score = json.load(load_f)
        with open(vis_display_vegalite_data_path, 'r') as load_f:
            load_dict = json.load(load_f)
        dataset = []
        for i, k in enumerate(load_dict):
            dataset.append(
                {"id": k, "x": float(distance[k]["x"]), "task": load_dict[k]["task"], "y": float(distance[k]["y"]),
                 "score": float(fact_score[k]), "vis": load_dict[k]["vis"]})
        storyline = StoryGenerator("../data/" + path + ".csv", dataset, "../data/" + path + "_js_divergence.json",
                                   cluster_data=dataset, level=1, custom="1-1")

        # storyline.generateStorylines()
        storyline.getTok_K_Facts()
        storyline.getTopicFacts()

        all_topic_save_path = "../server/static/data/" + path + "_topic.json"
        data = json.dumps(storyline.topic, indent=4)
        with open(all_topic_save_path, 'w') as file:
            file.write(data)

        top_k_topic_save_path = "../server/static/data/" + path + "_top_k_topic.json"
        data = json.dumps(storyline.top_k_topic, indent=4)
        with open(top_k_topic_save_path, 'w') as file:
            file.write(data)


if __name__ == '__main__':
    tables_path = ["entrepreneurship"]
    data_generation(tables_path)
    distance_compution(tables_path)
    score(tables_path)
    getTopic(tables_path)
