#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: search_path.py
# @time: 2022/3/10 14:36
import math


class Searcher:

    def __init__(self, facts, start, end, encoding_weight, logical_weight, score_weight):
        self.facts = facts
        self.start = start
        self.end = end
        self.encoding_weight = encoding_weight
        self.logical_weight = logical_weight
        self.score_weight = score_weight
        self.path = []
        self.clusters = {}
        self.middle_clusters = {}
        self.key_facts = []

        for n in facts:
            if n["id"] == start:
                self.start_fact = n
            elif n["id"] == end:
                self.end_fact = n

    def classify_facts(self):
        for node in self.facts:
            if node["label"] != -1:
                if node["label"] in self.clusters:
                    self.clusters[node["label"]].append(node)
                else:
                    self.clusters[node["label"]] = [node]

    def get_clusters_between_start_and_end(self):
        for label in self.clusters:
            for n in self.clusters[label]:
                if float(n["cx"]) > min([float(self.start_fact["cx"]), float(self.end_fact["cx"])]) and float(
                        n["cx"]) < max([float(self.start_fact["cx"]), float(self.end_fact["cx"])]) and float(
                    n["cy"]) > min([float(self.start_fact["cy"]), float(self.end_fact["cy"])]) and float(
                    n["cy"]) < max([float(self.start_fact["cy"]), float(self.end_fact["cy"])]):
                    if label not in self.middle_clusters:
                        self.middle_clusters[label] = [n]
                    else:
                        self.middle_clusters[label].append(n)

    def get_cloest_cluster(self):

        start_fact = self.start_fact
        self.path.append(self.start_fact)
        while (len(self.middle_clusters.keys()) > 0):
            close_node = self.get_key_fact_in_middle_clusters(start_fact, self.middle_clusters)
            self.path.append(close_node)
            start_fact = close_node
            del self.middle_clusters[close_node["label"]]
        self.path.append(self.end_fact)

    def get_key_fact_in_middle_clusters(self, start, clusters):
        dis = float('inf')
        close_fact = start
        for label in clusters:
            for n in clusters[label]:
                encoding_dis = math.sqrt(
                    (float(n["ex"]) - float(start["ex"])) ** 2 + (float(n["ey"]) - float(start["ey"])) ** 2)
                logical_dis = math.sqrt(
                    (float(n["lx"]) - float(start["lx"])) ** 2 + (float(n["ly"]) - float(start["ly"])) ** 2)
                score = float(n["score"])
                distance = encoding_dis * self.encoding_weight + logical_dis * self.logical_weight + score * self.score_weight
                if distance < dis:
                    close_fact = n
                    dis = distance
        return close_fact

    def compute(self):
        self.classify_facts()
        self.get_clusters_between_start_and_end()
        self.get_cloest_cluster()
        return self.path
