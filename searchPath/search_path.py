#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: search_path.py
# @time: 2022/3/10 14:36
from factExtract.score import cal_each_fact
from utils import constants
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import math
import copy
import pandas as pd
import time
import json


class Searcher:

    def __init__(self, table_path, facts, start, end, encoding_weight, logical_weight, score_weight):
        self.facts = facts
        self.start = start
        self.end = end
        self.encoding_weight = encoding_weight
        self.logical_weight = logical_weight
        self.score_weight = score_weight
        self.path = []
        self.mark = []
        self.clusters = {}
        self.middle_clusters = {}
        self.key_facts = []
        self.isTransitionByMark = False
        self.isTransitionByTransform = False
        self.isTransitionByEncoding = False
        self.isEndWithArc = False
        self.isLine = False
        self.isPoint = False
        self.isColor = False
        self.endNodeFact = {}
        self.transitionNode = {}
        self.diff = {"mark": {"modify": []}, "filter": {"modify": [], "add": [], "remove": []},
                     "encoding": {"modify": [], "add": [], "remove": [], "transpose": []}}
        self.mark_encoding_mapping = {
            "tick": [["x"]],
            "boxplot": [["x"]],
            "point": [["x"], ["x", "y"], ["x", "y", "color"]],
            "bar": [["x", "y"]],
            "line": [["x", "y"]],
            "arc": [['theta', 'color']]
        }
        self.encoding_mark_mapping = {
            "x": ["tick", "boxplot", "point"],
            "y": ["tick", "boxplot", "point"],
            "xy": ["point", "bar", "line"],
            "xycolor": ["point"],
            "thetacolor": ["arc"]
        }
        self.attr_mark_mapping = {
            "Q": ["tick", "boxplot", "point"],
            "QQ": ["point", "square", "circle"],
            "QN": ["bar", "point"],
            "QT": ["line", "area"],
            "QQQ": ["point", "square", "circle"],
            "QQN": ["tick"],
            "QQT": ["point"],
            "QNN": ["tick", "bar"],
            "QNT": ["line", "tick"]
        }
        self.attr_task_mapping = {
            "Q": 'distribution',
            "QQ": 'correlation',
            "QN": 'distribution',
            "QT": 'trend',
            "QQQ": 'correlation',
            "QQN": 'distribution',
            "QQT": 'correlation',
            "QNN": 'distribution',
            "QNT": 'distribution'
        }

        self.scores = []
        for n in facts:
            self.scores.append(n["score"])
            if n["id"] == start:
                self.start_fact = n
            elif n["id"] == end:
                self.end_fact = n

        self.table = pd.read_csv(table_path)
        self.attrLabel = dict()
        self.getLabelAttr(self.table.columns)

        if self.start["vis"]["mark"]["type"] == "arc":
            self.path.append({"vis": copy.deepcopy(self.start["vis"])})
            self.start["vis"]["mark"]["type"] = "bar"
            self.start["vis"]["encoding"]["y"] = self.start["vis"]["encoding"]["theta"]
            self.start["vis"]["encoding"]["x"] = self.start["vis"]["encoding"]["color"]
            self.start["vis"]["encoding"].pop("theta")
            self.start["vis"]["encoding"].pop("color")
            self.transitionNode = copy.deepcopy(self.start["vis"])
            self.path.append({"vis": copy.deepcopy(self.start["vis"])})
        else:
            self.transitionNode = copy.deepcopy(self.start["vis"])
            self.path.append({"vis": copy.deepcopy(self.start["vis"])})
        if self.end["vis"]["mark"]["type"] == "arc":
            self.endNodeFact = {"vis": copy.deepcopy(self.end["vis"])}
            self.end["vis"]["mark"]["type"] = "bar"
            self.end["vis"]["encoding"]["y"] = self.end["vis"]["encoding"]["theta"]
            self.end["vis"]["encoding"]["x"] = self.end["vis"]["encoding"]["color"]
            self.end["vis"]["encoding"].pop("theta")
            self.end["vis"]["encoding"].pop("color")
            self.isEndWithArc = True

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
                if float(n["x"]) > min([float(self.start_fact["x"]), float(self.end_fact["x"])]) and float(
                        n["x"]) < max([float(self.start_fact["x"]), float(self.end_fact["x"])]) and float(
                    n["y"]) > min([float(self.start_fact["y"]), float(self.end_fact["y"])]) and float(
                    n["y"]) < max([float(self.start_fact["y"]), float(self.end_fact["y"])]):
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

    # 给列属性定义类别
    def getLabelAttr(self, attributes):
        """
                列属性label
                 'Q': 'quantitative',
                 'N': 'nominal',
                 'T': 'temporal',
                 'O': 'ordinal',
                """
        for attr in attributes:
            Tokens = attr.split(" ")
            for token in Tokens:
                if token.lower() in constants.time:
                    self.attrLabel[attr] = "T"
                elif token.lower() in constants.ordinal:
                    if attr not in self.attrLabel.keys():
                        self.attrLabel[attr] = "O"
            if attr not in self.attrLabel.keys():
                if is_numeric_dtype(self.table[attr]):
                    self.attrLabel[attr] = "Q"
                elif is_string_dtype(self.table[attr]):
                    self.attrLabel[attr] = "N"

    def reSetTitle(self, node):
        slices = []
        if node["transform"]:
            if "and" in node["transform"][0]["filter"]:
                for f in node["transform"][0]["filter"]["and"]:
                    if "oneOf" in f:
                        slices.append({f["field"]: f["oneOf"]})
                    else:
                        slices.append({f["field"]: f["range"]})
            else:
                if "oneOf" in node["transform"][0]["filter"]:
                    slices.append({node["transform"][0]["filter"]["field"]:
                                       node["transform"][0]["filter"]["oneOf"]})
                else:
                    slices.append({node["transform"][0]["filter"]["field"]:
                                       node["transform"][0]["filter"]["range"]})
        filters = []
        for slice in slices:
            key = list(slice.keys())[0]
            value = list(slice.values())[0]
            if self.attrLabel.get(key) == "Q":
                table = copy.deepcopy(self.table)
                table["binned"] = pd.cut(table[key], 3, labels=['Q1', 'Q2', 'Q3'])
                data_Q1 = list(table[table["binned"] == "Q1"][key])
                data_Q2 = list(table[table["binned"] == "Q2"][key])
                data_Q3 = list(table[table["binned"] == "Q3"][key])
                rang_Q1 = []
                rang_Q2 = []
                rang_Q3 = []
                if data_Q1:
                    rang_Q1 = [min(data_Q1), max(data_Q1)]
                if data_Q2:
                    rang_Q2 = [min(data_Q2), max(data_Q2)]
                if data_Q3:
                    rang_Q3 = [min(data_Q3), max(data_Q3)]
                if value == rang_Q1:
                    filters.append(str(key) + " = " + "low level")
                elif value == rang_Q2:
                    filters.append(str(key) + " = " + "medium level")
                elif value == rang_Q3:
                    filters.append(str(key) + " = " + "high level")
            else:
                filters.append(str(key) + " = " + str(value[0]))

        if len(filters) == 1:
            node["title"]["text"] = filters[0]
        elif len(filters) == 0:
            node["title"]["text"] = ""
        elif len(filters) == 2:
            title = []
            for i in range(len(filters)):
                title.append(filters[i])
            node["title"]["text"] = title
        return node

    def difference(self):
        source_vsp = self.start["vis"]
        target_vsp = self.end["vis"]

        ###################################mark######################################

        source_mark = source_vsp["mark"]["type"]
        target_mark = target_vsp["mark"]["type"]

        self.diff["mark"]["modify"].append({"from": source_mark, "to": target_mark})

        ###################################filter####################################

        source_node_filter = []
        source_node_filter_copy = []
        target_node_filter = []
        target_node_filter_copy = []
        # {"field": "country", "oneOf": ["marshall islands"]}
        # {"field": "vaccine_rates", "range": [0.7, 0.99]}

        if "and" in source_vsp["transform"][0]["filter"]:
            source_node_filter.extend(source_vsp["transform"][0]["filter"]["and"])
            source_node_filter_copy.extend(source_vsp["transform"][0]["filter"]["and"])
        else:
            source_node_filter.append(source_vsp["transform"][0]["filter"])
            source_node_filter_copy.append(source_vsp["transform"][0]["filter"])

        if "and" in target_vsp["transform"][0]["filter"]:
            target_node_filter.extend(target_vsp["transform"][0]["filter"]["and"])
            target_node_filter_copy.extend(target_vsp["transform"][0]["filter"]["and"])
        else:
            target_node_filter.append(target_vsp["transform"][0]["filter"])
            target_node_filter_copy.append(target_vsp["transform"][0]["filter"])

        for j in range(len(source_node_filter_copy)):
            index_fs = -1
            index_ft = -1
            for i in range(len(target_node_filter_copy)):
                if source_node_filter_copy[j]["field"] == target_node_filter_copy[i]["field"]:
                    index_fs = j
                    index_ft = i
            if index_ft != -1 and index_fs != -1:
                if source_node_filter_copy[j][list(source_node_filter_copy[j].keys())[1]] != target_node_filter_copy[i][
                    list(target_node_filter_copy[i].keys())[1]]:
                    self.diff["filter"]["modify"].append(
                        {"from": source_node_filter_copy[index_fs], "to": target_node_filter_copy[index_ft]})
                    del source_node_filter[index_fs]
                    del target_node_filter[index_ft]
                else:
                    del source_node_filter[index_fs]
                    del target_node_filter[index_ft]
        for fs in source_node_filter:
            self.diff["filter"]["remove"].append({"from": fs, "to": None})
        for ft in target_node_filter:
            self.diff["filter"]["add"].append({"from": None, "to": ft})

        ###################################encoding#####################################

        source_node_encoding = []
        target_node_encoding = []
        source_node_encoding_copy = []
        target_node_encoding_copy = []

        for k in source_vsp["encoding"]:
            source_node_encoding.append(
                {"channel": k, "attr": source_vsp["encoding"][k]["field"], "type": source_vsp["encoding"][k]["type"],
                 "aggregate": source_vsp["encoding"][k]["aggregate"]})
            source_node_encoding_copy.append(
                {"channel": k, "attr": source_vsp["encoding"][k]["field"], "type": source_vsp["encoding"][k]["type"],
                 "aggregate": source_vsp["encoding"][k]["aggregate"]})
        for k in target_vsp["encoding"]:
            target_node_encoding.append(
                {"channel": k, "attr": target_vsp["encoding"][k]["field"], "type": target_vsp["encoding"][k]["type"],
                 "aggregate": target_vsp["encoding"][k]["aggregate"]})
            target_node_encoding_copy.append(
                {"channel": k, "attr": target_vsp["encoding"][k]["field"], "type": target_vsp["encoding"][k]["type"],
                 "aggregate": target_vsp["encoding"][k]["aggregate"]})

        isBreak = False
        transpose_coordinates = [[], []]
        while (not isBreak):
            print(source_node_encoding)
            print(target_node_encoding)
            print(source_node_encoding_copy)
            print(target_node_encoding_copy)
            transpose_index_es = -1
            transpose_index_et = -1
            for j in range(len(source_node_encoding_copy)):
                isReTry = False
                for i in range(len(target_node_encoding_copy)):
                    if source_node_encoding_copy[j]["attr"] == target_node_encoding_copy[i]["attr"]:
                        if source_node_encoding_copy[j]["channel"] != target_node_encoding_copy[i]["channel"]:
                            transpose_index_es = j
                            transpose_index_et = i
                            self.diff["encoding"]["transpose"].append(
                                {"from": copy.deepcopy(source_node_encoding_copy[transpose_index_es]),
                                 "to": copy.deepcopy(target_node_encoding_copy[transpose_index_et])})
                            for i in range(len(source_node_encoding)):
                                if source_node_encoding[i]["channel"] == source_node_encoding_copy[transpose_index_es][
                                    "channel"]:
                                    source_node_encoding[i]["channel"] = target_node_encoding_copy[transpose_index_et][
                                        "channel"]
                                elif source_node_encoding[i]["channel"] == \
                                        target_node_encoding_copy[transpose_index_et][
                                            "channel"]:
                                    source_node_encoding[i]["channel"] = source_node_encoding_copy[transpose_index_es][
                                        "channel"]
                            source_node_encoding_copy = copy.deepcopy(source_node_encoding)
                            isReTry = True
                            break
                        else:
                            transpose_coordinates[0].append(j)
                            transpose_coordinates[1].append(i)
                if isReTry:
                    break
            if transpose_index_es == -1 and transpose_index_et == -1:
                isBreak = True

        print(transpose_coordinates)

        for i in sorted(list(set(transpose_coordinates[0])), reverse=True):
            del source_node_encoding[i]
            del source_node_encoding_copy[i]

        for i in sorted(list(set(transpose_coordinates[1])), reverse=True):
            del target_node_encoding[i]
            del target_node_encoding_copy[i]

        for j in range(len(source_node_encoding_copy)):
            index_es = -1
            index_et = -1
            for i in range(len(target_node_encoding_copy)):
                if source_node_encoding_copy[j]["type"] == target_node_encoding_copy[i]["type"]:
                    index_es = j
                    index_et = i

            if index_et != -1 and index_es != -1:
                if source_node_encoding_copy[index_es]["channel"] != target_node_encoding_copy[index_et]["channel"]:
                    self.diff["encoding"]["transpose"].append(
                        {"from": copy.deepcopy(source_node_encoding_copy[index_es]),
                         "to": copy.deepcopy(target_node_encoding_copy[index_et])})
                    for i in range(len(source_node_encoding)):
                        if source_node_encoding[i]["channel"] == source_node_encoding_copy[transpose_index_es][
                            "channel"]:
                            source_node_encoding[i]["channel"] = target_node_encoding_copy[transpose_index_et][
                                "channel"]
                        elif source_node_encoding[i]["channel"] == target_node_encoding_copy[transpose_index_et][
                            "channel"]:
                            source_node_encoding[i]["channel"] = source_node_encoding_copy[transpose_index_es][
                                "channel"]
                    source_node_encoding_copy[index_es]["channel"] = target_node_encoding_copy[index_et]["channel"]
                if source_node_encoding_copy[index_es]["attr"] != target_node_encoding_copy[index_et]["attr"]:
                    self.diff["encoding"]["modify"].append(
                        {"from": source_node_encoding_copy[index_es],
                         "to": target_node_encoding_copy[index_et],
                         "channel": source_node_encoding_copy[index_es]["channel"]})
                del source_node_encoding[index_es]
                del target_node_encoding[index_et]

        for es in source_node_encoding:
            self.diff["encoding"]["remove"].append({"from": es, "to": None})
        for et in target_node_encoding:
            self.diff["encoding"]["add"].append({"from": None, "to": et})

    def pathGenerate(self):
        print("------------------------------------------")
        while self.diff["mark"]["modify"] or self.diff["filter"]["modify"] or self.diff["filter"]["add"] or \
                self.diff["filter"]["remove"] or self.diff["encoding"]["transpose"] or self.diff["encoding"][
            "modify"] or \
                self.diff["encoding"]["add"] or self.diff["encoding"]["remove"]:
            print(self.transitionNode)
            print(self.diff)
            # print(self.diff)
            ######################tryTransitionByMark#####################
            if self.diff["mark"]["modify"]:
                if not self.diff["filter"]["modify"] and not self.diff["filter"]["add"] and not self.diff["filter"][
                    "remove"] and not self.diff["encoding"]["transpose"] and not self.diff["encoding"]["modify"] and not \
                        self.diff["encoding"]["add"] and not self.diff["encoding"]["remove"]:
                    if len(self.path) > 1:
                        self.path.pop()
                        self.transitionNode["mark"]["type"] = self.diff["mark"]["modify"][0]["to"]
                        self.path.append({"vis": copy.deepcopy(self.transitionNode)})
                        self.diff["mark"]["modify"] = self.diff["mark"]["modify"][1:]
                        continue
                    else:
                        self.transitionNode["mark"]["type"] = self.diff["mark"]["modify"][0]["to"]
                        self.path.append({"vis": copy.deepcopy(self.transitionNode)})
                        self.diff["mark"]["modify"] = self.diff["mark"]["modify"][1:]
                        continue
            if not self.isTransitionByMark:
                ################################tryTransitionByTransform################################
                if self.diff["filter"]["modify"]:
                    if "and" in self.transitionNode["transform"][0]["filter"]:
                        for i in range(len(self.transitionNode["transform"][0]["filter"]["and"])):
                            if self.transitionNode["transform"][0]["filter"]["and"][i]["field"] == \
                                    self.diff["filter"]["modify"][0]["to"]["field"]:
                                if "oneOf" in self.transitionNode["transform"][0]["filter"]["and"][i]:
                                    insertNode = copy.deepcopy(self.transitionNode)
                                    insertNode["transform"][0]["filter"]["and"].pop(i)
                                    self.isInsert(insertNode)
                                    self.transitionNode["transform"][0]["filter"]["and"][i]["oneOf"] = \
                                        self.diff["filter"]["modify"][0]["to"]["oneOf"]
                                    self.transitionNode = self.reSetTitle(self.transitionNode)
                                    self.diff["filter"]["modify"] = self.diff["filter"]["modify"][1:]
                                    self.tryTransactionsByMark()
                                    fixedVis = self.fixVis()
                                    self.path.append({"vis": copy.deepcopy(fixedVis)})
                                    self.isTransitionByTransform = True
                                    break
                                else:
                                    insertNode = copy.deepcopy(self.transitionNode)
                                    insertNode["transform"][0]["filter"]["and"].pop(i)
                                    self.isInsert(insertNode)
                                    self.transitionNode["transform"][0]["filter"]["and"][i]["range"] = \
                                        self.diff["filter"]["modify"][0]["to"]["range"]
                                    self.transitionNode = self.reSetTitle(self.transitionNode)
                                    self.diff["filter"]["modify"] = self.diff["filter"]["modify"][1:]
                                    self.tryTransactionsByMark()
                                    fixedVis = self.fixVis()
                                    self.path.append({"vis": copy.deepcopy(fixedVis)})
                                    self.isTransitionByTransform = True
                                    break
                        continue
                    else:
                        if "oneOf" in self.transitionNode["transform"][0]["filter"]:
                            insertNode = copy.deepcopy(self.transitionNode)
                            insertNode["transform"] = []
                            self.isInsert(insertNode)
                            self.transitionNode["transform"][0]["filter"]["oneOf"] = \
                                self.diff["filter"]["modify"][0]["to"]["oneOf"]
                            self.transitionNode = self.reSetTitle(self.transitionNode)
                            self.diff["filter"]["modify"] = self.diff["filter"]["modify"][1:]
                            self.tryTransactionsByMark()
                            fixedVis = self.fixVis()
                            self.path.append({"vis": copy.deepcopy(fixedVis)})
                            self.isTransitionByTransform = True
                            continue
                        else:
                            insertNode = copy.deepcopy(self.transitionNode)
                            insertNode["transform"] = []
                            self.isInsert(insertNode)
                            self.transitionNode["transform"][0]["filter"]["range"] = \
                                self.diff["filter"]["modify"][0]["to"]["range"]
                            self.transitionNode = self.reSetTitle(self.transitionNode)
                            self.diff["filter"]["modify"] = self.diff["filter"]["modify"][1:]
                            self.tryTransactionsByMark()
                            fixedVis = self.fixVis()
                            self.path.append({"vis": copy.deepcopy(fixedVis)})
                            self.isTransitionByTransform = True
                            continue
                elif self.diff["filter"]["remove"]:
                    if "and" in self.transitionNode["transform"][0]["filter"]:
                        for i in range(len(self.transitionNode["transform"][0]["filter"]["and"])):
                            if self.transitionNode["transform"][0]["filter"]["and"][i]["field"] == \
                                    self.diff["filter"]["remove"][0]["from"]["field"]:
                                self.transitionNode["transform"][0]["filter"]["and"].pop(i)
                                if not self.transitionNode["transform"][0]["filter"]["and"]:
                                    self.transitionNode["transform"] = []
                                self.transitionNode = self.reSetTitle(self.transitionNode)
                                self.diff["filter"]["remove"] = self.diff["filter"]["remove"][1:]
                                self.tryTransactionsByMark()
                                fixedVis = self.fixVis()
                                self.path.append({"vis": copy.deepcopy(fixedVis)})
                                self.isTransitionByTransform = True
                                break
                    else:
                        if self.transitionNode["transform"][0]["filter"]["field"] == \
                                self.diff["filter"]["remove"][0]["from"]["field"]:
                            self.transitionNode["transform"] = []
                            self.transitionNode = self.reSetTitle(self.transitionNode)
                            self.diff["filter"]["remove"] = self.diff["filter"]["remove"][1:]
                            self.tryTransactionsByMark()
                            fixedVis = self.fixVis()
                            self.path.append({"vis": copy.deepcopy(fixedVis)})
                            self.isTransitionByTransform = True
                            continue
                    continue
                elif self.diff["filter"]["add"]:
                    if self.transitionNode["transform"]:
                        f = []
                        if "and" in self.transitionNode["transform"][0]["filter"]:
                            f.append(self.transitionNode["transform"][0]["filter"]["and"][0])
                        else:
                            f.append(self.transitionNode["transform"][0]["filter"])
                        f.append(self.diff["filter"]["add"][0]["to"])
                        self.transitionNode["transform"][0]["filter"] = {"and": f}
                        self.transitionNode = self.reSetTitle(self.transitionNode)
                        self.diff["filter"]["add"] = self.diff["filter"]["add"][1:]
                        self.tryTransactionsByMark()
                        fixedVis = self.fixVis()
                        self.path.append({"vis": copy.deepcopy(fixedVis)})
                        self.isTransitionByTransform = True
                        continue
                    else:
                        self.transitionNode["transform"].append({"filter": self.diff["filter"]["add"][0]["to"]})
                        self.transitionNode = self.reSetTitle(self.transitionNode)
                        self.diff["filter"]["add"] = self.diff["filter"]["add"][1:]
                        self.tryTransactionsByMark()
                        fixedVis = self.fixVis()
                        self.path.append({"vis": copy.deepcopy(fixedVis)})
                        self.isTransitionByTransform = True
                        continue
                    continue
                if not self.diff["filter"]["modify"] and not self.diff["filter"]["remove"] and not self.diff["filter"][
                    "add"]:
                    self.isTransitionByTransform = False
                if not self.isTransitionByTransform:
                    #################################tryTransitionByEncoding###################################
                    if self.diff["encoding"]["transpose"]:
                        for transpose in self.diff["encoding"]["transpose"]:
                            if transpose["to"]["channel"] not in self.transitionNode["encoding"]:
                                self.transitionNode["encoding"][transpose["to"]["channel"]] = \
                                    self.transitionNode["encoding"][transpose["from"]["channel"]]
                                self.transitionNode["encoding"][transpose["to"]["channel"]]["aggregate"] = \
                                    transpose["to"]["aggregate"]
                                self.transitionNode["encoding"].pop(transpose["from"]["channel"])
                            else:
                                toEncoding = copy.deepcopy(self.transitionNode)["encoding"][transpose["to"]["channel"]]
                                fromEncoding = copy.deepcopy(self.transitionNode)["encoding"][
                                    transpose["from"]["channel"]]
                                fromEncoding['aggregate'] = transpose["to"]["aggregate"]
                                self.transitionNode["encoding"][transpose["from"]["channel"]] = toEncoding
                                self.transitionNode["encoding"][transpose["to"]["channel"]] = fromEncoding

                        # self.path.append({"vis": copy.deepcopy(self.transitionNode)})
                        self.diff["encoding"]["transpose"] = []
                        continue
                    elif self.diff["encoding"]["modify"]:
                        self.transitionNode["encoding"][self.diff["encoding"]["modify"][0]["channel"]]["field"] = \
                            self.diff["encoding"]["modify"][0]["to"]["attr"]
                        self.transitionNode["encoding"][self.diff["encoding"]["modify"][0]["channel"]]["aggregate"] = \
                            self.diff["encoding"]["modify"][0]["to"]["aggregate"]
                        self.tryTransactionsByMark()
                        self.path.append({"vis": copy.deepcopy(self.transitionNode)})
                        self.diff["encoding"]["modify"] = self.diff["encoding"]["modify"][1:]
                        continue
                    elif self.diff["encoding"]["remove"]:
                        self.transitionNode["encoding"].pop(self.diff["encoding"]["remove"][0]["from"]["channel"])
                        self.tryTransactionsByMark()
                        self.path.append({"vis": copy.deepcopy(self.transitionNode)})
                        self.diff["encoding"]["remove"] = self.diff["encoding"]["remove"][1:]
                        continue
                    elif self.diff["encoding"]["add"]:
                        self.transitionNode["encoding"][self.diff["encoding"]["add"][0]["to"]["channel"]] = {
                            "field": self.diff["encoding"]["add"][0]["to"]["attr"],
                            "type": self.diff["encoding"]["add"][0]["to"]["type"],
                            "aggregate": self.diff["encoding"]["add"][0]["to"]["aggregate"],
                            "axis": {"format": "s"}}
                        self.tryTransactionsByMark()
                        self.transitionNode = self.fixVis()
                        self.path.append({"vis": copy.deepcopy(self.transitionNode)})
                        self.diff["encoding"]["add"] = self.diff["encoding"]["add"][1:]
                        continue

        if self.endNodeFact:
            self.path.append(self.endNodeFact)

    def tryTransactionsByMark(self):

        attr = self.getAttrType()

        mark_curr = self.transitionNode["mark"]["type"]

        mark_next = ""

        for mark in self.attr_mark_mapping[attr]:
            if mark not in self.mark:
                mark_next = mark
                self.mark.append(mark)

        if mark_next:
            self.transitionNode["mark"]["type"] = mark_next
        else:
            if mark_curr not in self.attr_mark_mapping[attr]:
                self.transitionNode["mark"]["type"] = self.attr_mark_mapping[attr][0]

    def getAttrType(self):
        attr = ""
        for channel in self.transitionNode["encoding"]:
            if self.attrLabel[self.transitionNode["encoding"][channel]["field"]] == "Q":
                attr += "Q"
        for channel in self.transitionNode["encoding"]:
            if self.attrLabel[self.transitionNode["encoding"][channel]["field"]] == "N":
                attr += "N"
        for channel in self.transitionNode["encoding"]:
            if self.attrLabel[self.transitionNode["encoding"][channel]["field"]] == "T":
                attr += "T"
        return attr

    def fixVis(self):

        fixedVis = copy.deepcopy(self.transitionNode)
        ######################################################################################
        filters = []
        if self.transitionNode["transform"]:
            if "and" in self.transitionNode["transform"][0]["filter"]:
                filters.extend(self.transitionNode["transform"][0]["filter"]["and"])
            else:
                filters.append(self.transitionNode["transform"][0]["filter"])
        encoidng = []
        for channel in self.transitionNode["encoding"]:
            encoidng.append({"channel": channel, "field": self.transitionNode["encoding"][channel]["field"],
                             "type": self.transitionNode["encoding"][channel]["type"]})
        ############################################case-one########################################
        for f in filters:
            if self.attrLabel[f["field"]] == "T":
                for e in encoidng:
                    if self.attrLabel[e["field"]] == "T":
                        fixedVis["encoding"].pop(e["channel"])
                        if fixedVis["encoding"]["y"]["type"] == "quantitative":
                            fixedVis["encoding"]["y"]["aggregate"] = None
        ########################################case-two################################################
        if "x" in fixedVis["encoding"] and "y" in fixedVis["encoding"] and len(fixedVis["encoding"]) == 2:
            if self.attrLabel[fixedVis["encoding"]["x"]["field"]] == "T" or self.attrLabel[
                fixedVis["encoding"]["x"]["field"]] == "N":
                if "axis" in fixedVis["encoding"]["x"]:
                  fixedVis["encoding"]["x"].pop("axis")
                fixedVis["encoding"]["y"]["aggregate"] = "mean"
        ########################################################################################

        attr = ""
        for channel in fixedVis["encoding"]:
            if self.attrLabel[fixedVis["encoding"][channel]["field"]] == "Q":
                attr += "Q"
        for channel in fixedVis["encoding"]:
            if self.attrLabel[fixedVis["encoding"][channel]["field"]] == "N":
                attr += "N"
        for channel in fixedVis["encoding"]:
            if self.attrLabel[fixedVis["encoding"][channel]["field"]] == "T":
                attr += "T"

        mark_curr = fixedVis["mark"]["type"]

        mark_next = ""

        for mark in self.attr_mark_mapping[attr]:
            if mark not in self.mark:
                mark_next = mark
                self.mark.append(mark)

        if mark_next:
            fixedVis["mark"]["type"] = mark_next
        else:
            if mark_curr not in self.attr_mark_mapping[attr]:
                fixedVis["mark"]["type"] = self.attr_mark_mapping[attr][0]

        if fixedVis["mark"]["type"] == "area":
            if not self.isLine:
                fixedVis["mark"]["type"] = "line"
                fixedVis["mark"]["interpolate"] = "monotone"
                fixedVis["mark"]["point"] = True
                self.isLine = True
            else:
                if not self.isColor:
                    fixedVis["mark"]["line"] = True
                    fixedVis["mark"]["color"] = {
                        "x1": 1,
                        "y1": 1,
                        "x2": 1,
                        "y2": 0,
                        "gradient": "linear",
                        "stops": [
                            {"offset": 0, "color": "white"},
                            {"offset": 1, "color": "blue"}
                        ]
                    }
                    self.isColor = True
                else:
                    fixedVis["mark"]["line"] = True
                    fixedVis["mark"]["color"] = {
                        "x1": 1,
                        "y1": 1,
                        "x2": 1,
                        "y2": 0,
                        "gradient": "linear",
                        "stops": [
                            {"offset": 0, "color": "white"},
                            {"offset": 1, "color": "blue"}
                        ]
                    }
                    fixedVis["mark"]["point"] = True

        return fixedVis

    def isInsert(self, node):
        node = self.reSetTitle(node)
        impact_w = 0.4
        significance_w = 0.6
        attr = ""
        for channel in node["encoding"]:
            if self.attrLabel[node["encoding"][channel]["field"]] == "Q":
                attr += "Q"
        for channel in node["encoding"]:
            if self.attrLabel[node["encoding"][channel]["field"]] == "N":
                attr += "N"
        for channel in node["encoding"]:
            if self.attrLabel[node["encoding"][channel]["field"]] == "T":
                attr += "T"
        fact = {"task": self.attr_task_mapping[attr], "vis": copy.deepcopy(node)}
        impact_value, significance_value = cal_each_fact(fact_ep=fact, data=self.table)
        score = impact_w * impact_value + significance_w * significance_value
        self.scores.sort(reverse=True)
        threshold = self.scores[int(len(self.scores) * 0.15)]
        if score > threshold:
            self.path.append({"vis": copy.deepcopy(node)})

# start = {"vis": {
#     "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
#     "mark": {"type": "line", "tooltip": True},
#     "encoding": {
#         "y": {
#             "field": "diseases",
#             "type": "quantitative",
#             "aggregate": "mean",
#             "axis": {"format": "s"}
#         },
#         "x": {"field": "year", "type": "temporal", "aggregate": None}
#     },
#     "transform": [
#         {
#             "filter": {
#                 "and": [
#                     {"field": "country", "oneOf": ["nepal"]},
#                     {"field": "diseases", "range": [14901, 181259]}
#                 ]
#             }
#         }
#     ],
#     "title": {
#         "text": ["country = nepal", "diseases = low level"],
#         "align": "center"
#     },
#     "data": {
#         "url": "../static/data/vaccine_correlation.csv",
#         "format": {"type": "csv"}
#     },
#     "width": 200,
#     "height": 200
# }}
# end = {"vis": {
#     "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
#     "mark": {"type": "point", "tooltip": True},
#     "encoding": {
#         "x": {
#             "field": "vaccine_rates",
#             "type": "quantitative",
#             "aggregate": None,
#             "axis": {"format": "s"}
#         },
#         "y": {
#             "field": "diseases",
#             "type": "quantitative",
#             "aggregate": None,
#             "axis": {"format": "s"}
#         }
#     },
#     "transform": [
#         {
#             "filter": {
#                 "and": [
#                     {"field": "year", "oneOf": [2004]},
#                     {"field": "diseases", "range": [14901, 181259]}
#                 ]
#             }
#         }
#     ],
#     "title": {"text": ["year = 2004", "diseases = low level"], "align": "center"},
#     "data": {
#         "url": "../static/data/vaccine_correlation.csv",
#         "format": {"type": "csv"}
#     },
#     "width": 200,
#     "height": 200
# }}
#
# s = Searcher(table_path="../data/vaccine_correlation.csv", facts=[], start=start, end=end, logical_weight=0,
#              encoding_weight=0, score_weight=0)
# s.difference()
# print(s.diff)
# s.pathGenerate()
# print("--------------------------------")
# for p in s.path:
#     print(p)
