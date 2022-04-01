#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: storyGenerator.py
# @time: 2022/2/19 13:08
import numpy as np
import scipy.stats
import pandas as pd
import json
import math
import copy


class StoryGenerator:

    def __init__(self, table_path, vl_specs, JS_path, cluster_data, level, custom):
        self.table_path = table_path
        self.vl_specs = vl_specs
        self.JS_path = JS_path
        self.table = pd.read_csv(self.table_path)
        self.JS_divs = {}
        self.cluster_data = cluster_data
        self.storyline = {"cross_cluster": {}, "in_cluster": {}}
        self.clusters = {}
        self.radius = 600
        self.rate = 0.5
        self.bins = 4
        self.visted_clusters = []
        self.seq = []
        self.k = 10
        self.custom = []
        self.topkthreshold = 100
        for i in self.cluster_data:
            if i["id"] == custom:
                self.custom.append(i)
        self.level = level
        if self.level == "low":
            self.radius = 150
            self.rate = 0.5
        elif self.level == "medium":
            self.radius = 175
            self.rate = 0.75
        else:
            self.radius = 200
            self.rate = 0.9

    # calculate JS divergence of two array distributions
    def JS_div(self, arr1, arr2, num_bins):
        max0 = max(np.max(arr1), np.max(arr2))
        min0 = min(np.min(arr1), np.min(arr2))
        bins = np.linspace(min0 - 1e-4, max0 - 1e-4, num=num_bins)
        PDF1 = pd.cut(arr1, bins).value_counts() / len(arr1)
        PDF2 = pd.cut(arr2, bins).value_counts() / len(arr2)
        return self.JS_divergence(PDF1.values, PDF2.values)

    # JS divergence
    def JS_divergence(self, p, q):
        M = (p + q) / 2
        return 0.5 * scipy.stats.entropy(p, M, base=2) + 0.5 * scipy.stats.entropy(q, M, base=2)

    # calculate KL divergence of two array distributions
    def KL_div(self, arr1, arr2, num_bins):
        max0 = max(np.max(arr1), np.max(arr2))
        min0 = min(np.min(arr1), np.min(arr2))
        bins = np.linspace(min0 - 1e-4, max0 - 1e-4, num=num_bins)
        PDF1 = pd.cut(arr1, bins).value_counts() / len(arr1)
        PDF2 = pd.cut(arr2, bins).value_counts() / len(arr2)
        return self.KL_divergence(PDF1.values, PDF2.values)

    # KL divergence
    def KL_divergence(self, p, q):
        return scipy.stats.entropy(p, q, base=2)

    def get_JS_divs(self):
        i = 0
        print("开始计算")
        for vm in self.vl_specs:
            js = {}
            for vn in self.vl_specs:
                i += 1
                print("--------------------------进度------------------------",
                      i / len(self.vl_specs) / len(self.vl_specs))
                print("-------------------------正在计算第", i, "对-------------------------")
                Vm = self.vl_specs[vm]
                Vn = self.vl_specs[vn]
                if vm != vn:

                    m_table = self.table
                    n_table = self.table

                    m = Vm["vis"]
                    n = Vn["vis"]

                    m_transform = {}
                    n_transform = {}

                    if "transform" in m:
                        m_transform = m["transform"][0]
                    if "transform" in n:
                        n_transform = n["transform"][0]

                    if "filter" in m_transform:
                        if "and" in m_transform["filter"]:
                            for f in m_transform["filter"]["and"]:
                                m_table = m_table[m_table[f["field"]] == f["oneOf"][0]]
                        else:
                            m_table = m_table[
                                m_table[m_transform["filter"]["field"]] == m_transform["filter"]["oneOf"][0]]

                    if "filter" in n_transform:
                        if "and" in n_transform["filter"]:
                            for f in n_transform["filter"]["and"]:
                                n_table = n_table[n_table[f["field"]] == f["oneOf"][0]]
                        else:
                            n_table = n_table[
                                n_table[n_transform["filter"]["field"]] == n_transform["filter"]["oneOf"][0]]

                    m_encoding = {}
                    n_encoding = {}

                    if "encoding" in m:
                        m_encoding = m["encoding"]
                    if "encoding" in n:
                        n_encoding = n["encoding"]

                    # data aggregation is not considered
                    m_data = []
                    n_data = []

                    for k in m_encoding.keys():
                        if m_encoding[k]["type"] == "quantitative":
                            m_data.append(list(m_table[m_encoding[k]["field"]]))
                    for k in n_encoding.keys():
                        if n_encoding[k]["type"] == "quantitative":
                            n_data.append(list(n_table[n_encoding[k]["field"]]))

                    # # To do, consider data aggregation
                    # m_data = []
                    # n_data = []
                    #
                    # for k in m_encoding.keys():
                    #     if m_encoding[k]["type"] == "quantitative":
                    #         if m_encoding[k]["aggregate"] == "count":
                    #             m_data.append(list(m_table[m_encoding[k]["field"]].value_counts()))
                    #         elif m_encoding[k]["aggregate"] == "mean":
                    #             print("to do")
                    #         else:
                    #             m_data.append(list(m_table[m_encoding[k]["field"]]))
                    #     elif m_encoding[k]["type"] == "nominal":
                    #         if m_encoding[k]["aggregate"] == "count":
                    #             m_data.append(list(m_table[m_encoding[k]["field"]].value_counts()))
                    # for k in n_encoding.keys():
                    #     if n_encoding[k]["type"] == "quantitative":
                    #         if n_encoding[k]["aggregate"] == "count":
                    #             n_data.append(list(n_table[n_encoding[k]["field"]].value_counts()))
                    #         elif n_encoding[k]["aggregate"] == "mean":
                    #             print("to do")
                    #         else:
                    #             n_data.append(list(n_table[n_encoding[k]["field"]]))
                    #     elif n_encoding[k]["type"] == "nominal":
                    #         if n_encoding[k]["aggregate"] == "count":
                    #             n_data.append(list(n_table[n_encoding[k]["field"]].value_counts()))

                    divergence = 0
                    for p in m_data:
                        for q in n_data:
                            divergence += self.JS_div(p, q, 10)
                    if (len(m_data) * len(n_data)) != 0:
                        divergence = divergence / (len(m_data) * len(n_data))
                    else:
                        divergence = 1
                    js[vn] = divergence
                else:
                    js[vn] = 1
            self.JS_divs[vm] = js
            data = json.dumps(self.JS_divs, indent=4)
            with open(self.JS_path, 'w') as file:
                file.write(data)

    def generateStorylines(self):

        # read JS divergence
        with open(self.JS_path, 'r') as load_f:
            self.JS_divs = json.load(load_f)

        key_nodes = []
        # get top-k fact
        self.get_cluster_data()
        # Pick a node at random
        # for k in self.clusters:
        #     key_nodes.append(choice(self.clusters[k]))

        key_nodes.extend(self.custom)
        data = copy.deepcopy(self.cluster_data)

        data.sort(key=lambda x: x["score"], reverse=True)
        key_nodes.append(data[0])
        for i in data:
            flag = True
            for j in key_nodes:
                if self.node_to_node_distance(i, j) < self.topkthreshold:
                    flag = False
            if flag:
                if len(key_nodes) < self.k:
                    key_nodes.append(i)
        # self.in_cluster_detect(key_nodes)
        self.cross_cluster_detect(key_nodes)

        return self.storyline

    def in_cluster_detect(self, nodes):

        print(self.cluster_data[0])
        for n in nodes:

            cur_cluster = self.clusters[n["label"]]

            # divergence = []
            #
            # for i in range(len(cur_cluster)):
            #     divergence.append(self.JS_divs[n["id"]][cur_cluster[i]["id"]])

            distance = []
            for i in range(len(cur_cluster)):
                dx = n["cx"] - cur_cluster[i]["cx"]
                dy = n["cy"] - cur_cluster[i]["cy"]
                distance.append(math.sqrt(dx * dx + dy * dy))

            # Label = []
            # if len(divergence) >= self.bins:
            #     bin_labels = []
            #     for i in range(self.bins):
            #         bin_labels.append(i)
            #     Label.extend(list(pd.cut(divergence, bins=self.bins, labels=bin_labels)))
            # else:
            #     bin_labels = []
            #     for i in range(len(divergence)):
            #         bin_labels.append(i)
            #     Label.extend(list(pd.cut(divergence, bins=len(divergence), labels=bin_labels)))

            Label = []
            if len(distance) >= self.bins:
                bin_labels = []
                for i in range(self.bins):
                    bin_labels.append(i)
                Label.extend(list(pd.cut(distance, bins=self.bins, labels=bin_labels)))
            else:
                bin_labels = []
                for i in range(len(distance)):
                    bin_labels.append(i)
                Label.extend(list(pd.cut(distance, bins=len(distance), labels=bin_labels)))

            # Hierarchical data distributed by divergence
            hierarchical = {}

            for i in range(len(Label)):
                if Label[i] in hierarchical:
                    hierarchical[Label[i]].append(cur_cluster[i])
                else:
                    hierarchical[Label[i]] = [cur_cluster[i]]

            relay_node = n
            for k in hierarchical:
                target_node = self.get_furthest_node(relay_node, hierarchical[k])
                if n != target_node:
                    self.storyline["in_cluster"].append(
                        {"source": relay_node, "target": target_node})
                    relay_node = self.get_furthest_node(relay_node, hierarchical[k])

    def get_cluster_data(self):
        for node in self.cluster_data:
            if node["label"] != -1:
                if node["label"] in self.clusters:
                    self.clusters[node["label"]].append(node)
                else:
                    self.clusters[node["label"]] = [node]

    def cross_cluster_detect(self, nodes):

        for n in nodes:
            self.visted_clusters=[n["label"]]
            self.cross_cluster_storyline_detect(n["id"], n, self.radius, n["label"])

    def cross_cluster_storyline_detect(self, node_id, node, radius, start):

        neighbor_clusters = self.get_close_cluster(node, radius)

        if len(neighbor_clusters) > 0:
            for k in neighbor_clusters:
                if k not in self.visted_clusters:

                    self.visted_clusters.append(k)

                    closest_node = self.get_closest_node(node, self.clusters[k])
                    if not ("visted" in node and "visted" in closest_node):
                        if node_id in self.storyline["cross_cluster"]:
                            self.storyline["cross_cluster"][node_id].append({"source": node, "target": closest_node})
                        else:
                            self.storyline["cross_cluster"][node_id] = [{"source": node, "target": closest_node}]

                        node["visted"] = True
                        closest_node["visted"] = True
                        self.cross_cluster_storyline_detect(node_id, closest_node, radius * self.rate, start)
        else:
            self.visted_clusters = [start]

    def get_closest_node(self, source_node, target_nodes):

        closet_node = target_nodes[0]

        score = []
        dis = []

        for target_node in target_nodes:
            dis.append(self.node_to_node_distance(source_node, target_node))
            score.append(float(target_node["score"]))
        if len(set(dis)) != 0:
            dis = self.normalization(dis)
        if len(set(score)) != 0:
            score = self.normalization(score)

        Score = []
        for i in score:
            Score.append(1 - i)

        score = Score

        rank = []
        for i in range(len(target_nodes)):
            rank.append(dis[i] + score[i])

        closet_node = target_nodes[rank.index(min(rank))]
        return closet_node

    def normalization(self, data):
        _range = np.max(data) - np.min(data)
        return (data - np.min(data)) / _range

    def get_furthest_node(self, source_node, target_nodes):

        d = 0
        furthest_node = target_nodes[0]

        for target_node in target_nodes:
            dis = self.node_to_node_distance(source_node, target_node)
            if dis >= d:
                d = dis
                furthest_node = target_node

        return furthest_node

    def node_to_node_distance(self, source_node, target_node):
        cx = target_node["cx"] - source_node["cx"]
        cy = target_node["cy"] - source_node["cy"]
        return math.sqrt(cx * cx + cy * cy)

    def node_to_cluster_distance(self, node, cluster):
        dis = 0
        for n in cluster:
            dis += self.node_to_node_distance(node, n)
        return dis / len(cluster)

    def get_close_cluster(self, node, radius):

        close_clusters = []
        cur_cluster = node["label"]

        for k in self.clusters:
            if k != cur_cluster:
                if self.node_to_cluster_distance(node, self.clusters[k]) <= radius:
                    close_clusters.append(k)

        return close_clusters

    # A = [1,-3], B = [5,-1]
    # A->B = [1,-3,5,-1]
    def get_angle(self, v1, v2):
        dx1 = v1[2] - v1[0]
        dy1 = v1[3] - v1[1]
        dx2 = v2[2] - v2[0]
        dy2 = v2[3] - v2[1]
        angle1 = math.atan2(dy1, dx1)
        angle1 = int(angle1 * 180 / math.pi)
        angle2 = math.atan2(dy2, dx2)
        angle2 = int(angle2 * 180 / math.pi)
        if angle1 * angle2 >= 0:
            included_angle = abs(angle1 - angle2)
        else:
            included_angle = abs(angle1) + abs(angle2)
            if included_angle > 180:
                included_angle = 360 - included_angle
        return included_angle

    def get_neighbor_node(self, source_node, target_node):

        neighbors = []

        # s->t
        s_to_t = [source_node["cx"], source_node["cy"], target_node["cx"], target_node["cy"]]
        # t->s
        t_to_s = [target_node["cx"], target_node["cy"], source_node["cx"], source_node["cy"]]

        for node in self.clusters[source_node["label"]]:
            if node["id"] != source_node["id"]:
                # s->node
                s_to_node = [source_node["cx"], source_node["cy"], node["cx"], node["cy"]]
                # t->node
                t_to_node = [target_node["cx"], target_node["cy"], node["cx"], node["cy"]]

                if self.get_angle(s_to_t, s_to_node) <= 90 and self.get_angle(t_to_s, t_to_node) <= 90:
                    neighbors.append(node)

        for node in self.clusters[target_node["label"]]:
            if node["id"] != target_node["id"]:
                # s->node
                s_to_node = [source_node["cx"], source_node["cy"], node["cx"], node["cy"]]
                # t->node
                t_to_node = [target_node["cx"], target_node["cy"], node["cx"], node["cy"]]

                if self.get_angle(s_to_t, s_to_node) <= 90 and self.get_angle(t_to_s, t_to_node) <= 90:
                    neighbors.append(node)

        neighbors.append(target_node)

        return neighbors

    def nearest_search(self, source_node, target_node, neighbors, count):
        if len(neighbors) == 0:
            self.seq.append({"source": source_node, "target": target_node})
        else:
            next_node = self.get_closest_node(source_node, neighbors)
            if next_node["id"] != target_node["id"]:
                if count < 5:
                    self.seq.append({"source": source_node, "target": next_node})
                    new_neighbors = self.get_neighbor_node(next_node, target_node)
                    count += 1
                    self.nearest_search(next_node, target_node, new_neighbors, count)
                else:
                    self.seq.append({"source": source_node, "target": target_node})
            else:
                self.seq.append({"source": source_node, "target": next_node})
