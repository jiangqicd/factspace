from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from utils import constants
from utils.designSpace import designSpace
from visGenerate.generator import Generator
import csv
import pandas as pd
from itertools import combinations
from functools import reduce
import copy
import json
import scipy.stats as stats
import copy
import heapq
import random
from random import shuffle


class Extractor:

    # variable list

    def __init__(self, table_path, vis_table_path, train_data_path, vis_data_path, encoding_input_path):
        # variable list#

        # table path
        self.table_path = table_path

        # Path to data recorded in vega-lite
        self.vis_table_path = vis_table_path

        # train_data_path, Used to train to generate vege-lita embedding
        self.train_data_path = train_data_path

        # Record the path where the vega-lite visualization dataset is stored
        self.vis_data_path = vis_data_path

        # table entity
        self.table = pd.read_csv(self.table_path)

        # define types for attributes, e.g.,{'Model': 'N', 'MPG': 'Q', 'Year': 'T'}
        self.attrLabel = dict()

        # subspaceSlice
        self.slice = []

        # subspace num
        self.num = []

        # slice data
        self.slice_data = []

        # all_subspaceSlice
        self.all_slice = []

        # fact data space
        self.factData = []

        # all fact data space
        self.all_factData = []

        # encoding input data path
        self.encoding_input_path = encoding_input_path

    def printTablePath(self):
        print(self.table_path)

    # 数据预处理
    def dataPreprocessing(self):

        attributes = self.table.columns
        self.getLabelAttr(attributes)
        # print(self.attrLabel)
        self.getSubspace()
        self.all_slice = self.slice
        print(self.slice)
        # self.all_slice = self.getSubspace()
        # self.all_slice = self.get_all_Subspace()
        self.factData, self.all_factData = self.getFactData()
        # print(self.factData)

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

    # to get subspace set
    def getSubspace(self):

        # Threshold for number of items
        threshold = 2

        # print(self.table['MPG'])
        # Equally spaced binning of numeric data
        # print(pd.cut(self.table['MPG'],4,labels=['Q1','Q2','Q3','Q4']))

        # key_list = list(
        #     filter(lambda key: self.attrLabel.get(key) == "N" or self.attrLabel.get(key) == "T", self.attrLabel.keys()))

        key_list = self.table.columns

        # for key in key_list:
        #     for value in set(list(self.table[key])):
        #         if self.table.groupby([key]).size()[value] > threshold:
        #             slice.append([{key: value}])

        for key in key_list:
            if self.attrLabel.get(key) == "Q":
                table = copy.deepcopy(self.table)
                table["binned" + key] = pd.cut(table[key], 3, labels=['Q1', 'Q2', 'Q3'])
                if key=="Range":
                    print(table)
                    print(table.groupby(["binned" + key]).size()["Q1"])
                    print(table.groupby(["binned" + key]).size()["Q2"])
                    print(table.groupby(["binned" + key]).size()["Q3"])

                if table.groupby(["binned" + key]).size()["Q1"] > threshold:
                    self.slice.append([{key: "Q1"}])
                    self.num.append(table.groupby(["binned" + key]).size()["Q1"])
                    Table = copy.deepcopy(table[table["binned" + key] == "Q1"])
                    self.slice_data.append(Table)
                if table.groupby(["binned" + key]).size()["Q2"] > threshold:
                    self.slice.append([{key: "Q2"}])
                    Table = copy.deepcopy(table[table["binned" + key] == "Q2"])
                    self.slice_data.append(Table)
                    self.num.append(table.groupby(["binned" + key]).size()["Q2"])
                if table.groupby(["binned" + key]).size()["Q3"] > threshold:
                    self.slice.append([{key: "Q3"}])
                    Table = copy.deepcopy(table[table["binned" + key] == "Q3"])
                    self.slice_data.append(Table)
                    self.num.append(table.groupby(["binned" + key]).size()["Q3"])
            else:
                for value in set(list(self.table[key])):
                    table = copy.deepcopy(self.table)
                    if table.groupby([key]).size()[value] > threshold:
                        self.slice.append([{key: value}])
                        table = table[table[key] == value]
                        self.slice_data.append(table)
                        self.num.append(self.table.groupby([key]).size()[value])

        # pairwise combination of properties
        for keyBinary in combinations(key_list, 2):
            valueBinary = []
            for key in keyBinary:
                elements = []
                if self.attrLabel.get(key) == "Q":
                    elements.append({key: "Q1"})
                    elements.append({key: "Q2"})
                    elements.append({key: "Q3"})
                    valueBinary.append(elements)
                else:
                    for value in set(list(self.table[key])):
                        elements.append({key: value})
                    valueBinary.append(elements)
            # Pairwise combination of slices
            combin = lambda x: reduce(lambda x, y: [[i, j] for i in x for j in y], x)
            for fs in combin(valueBinary):
                flag = 0
                table = copy.deepcopy(self.table)
                column = ""
                for f in fs:
                    k = list(f.keys())[0]
                    column = k
                    v = list(f.values())[0]
                    if self.attrLabel.get(k) == "Q":
                        table["binned" + k] = pd.cut(table[k], 3, labels=['Q1', 'Q2', 'Q3'])
                for f in fs:
                    k = list(f.keys())[0]
                    v = list(f.values())[0]
                    if self.attrLabel.get(k) == "Q":
                        if v == "Q1":
                            table = table[table["binned" + k] == "Q1"]
                        elif v == "Q2":
                            table = table[table["binned" + k] == "Q2"]
                        elif v == "Q3":
                            table = table[table["binned" + k] == "Q3"]
                        else:
                            flag = 1
                    else:
                        if k in list(table.columns):
                            table = table[table[k] == v]
                        else:
                            flag = 1
                if len(list(table[column])) > threshold and flag == 0:
                    self.slice.append(fs)
                    self.slice_data.append(table)
                    self.num.append(len(list(table[column])))

    # to get subspace set
    def get_all_Subspace(self):

        # Threshold for number of items
        threshold = 0

        slice = []
        # print(self.table['MPG'])
        # Equally spaced binning of numeric data
        # 通过如下cut函数，可以实现将MPG列装到4个区间,4个区间分别为['Q1','Q2','Q3','Q4']
        # pd.cut(self.table['MPG'],4,labels=['Q1','Q2','Q3','Q4'])

        key_list = list(
            filter(lambda key: self.attrLabel.get(key) == "N" or self.attrLabel.get(key) == "T", self.attrLabel.keys()))

        for key in key_list:
            for value in set(list(self.table[key])):
                if self.table.groupby([key]).size()[value] > threshold:
                    slice.append([{key: value}])

        # pairwise combination of properties
        for keyBinary in combinations(key_list, 2):
            valueBinary = []
            for key in keyBinary:
                elements = []
                for value in set(list(self.table[key])):
                    elements.append({key: value})
                valueBinary.append(elements)
            # Pairwise combination of slices
            combin = lambda x: reduce(lambda x, y: [[i, j] for i in x for j in y], x)
            for fs in combin(valueBinary):
                flag = 0
                table = self.table
                for f in fs:
                    if list(f.keys())[0] in list(table.columns):
                        table = table[table[list(f.keys())[0]] == list(f.values())[0]]
                    else:
                        flag = 1
                if len(table) > threshold and flag == 0:
                    slice.append(fs)
        return slice

    # Get the data composition space for each data fact
    def getFactData(self):
        factData = []
        all_factData = []
        # ---to get fact {"obversed attr":[slice1,slice2.....]}----

        # Two layers of observation attributes
        obverAttr = []
        for attr in self.table.columns:
            if len(set(list(self.table[attr]))) >= 2:
                obverAttr.append([attr])
        # for comb in list(combinations(self.table.columns, 2)):
        #     obverAttr.append(list(comb))

        # Combining observation attributes and subspace slices
        id = 0
        for attr in obverAttr:
            for i in range(len(self.slice)):
                slice = self.slice[i]
                keys = []
                values = []
                for element in slice:
                    keys.extend(list(element.keys()))
                    values.extend(list(element.values()))
                # Judging that observation attributes and subspaces do not coincide
                if len(set(attr) & set(keys)) == 0:
                    # table = self.table.copy()
                    # # Filter out factdata with empty data
                    # for key, value in zip(keys, values):
                    #     table = table[table[key] == value]
                    # if len(list(filter(lambda x: len(list(table[x])) > 0, attr))) == len(attr):
                    # Defining the type of observation attributes data, e.g., QQ, QN, QT
                    new_attr = attr + keys
                    Attr = []
                    type = ""
                    for key in new_attr:
                        if self.attrLabel.get(key) == "Q":
                            type += self.attrLabel.get(key)
                            Attr.append(key)
                    for key in new_attr:
                        if self.attrLabel.get(key) == "N":
                            type += self.attrLabel.get(key)
                            Attr.append(key)
                    for key in new_attr:
                        if self.attrLabel.get(key) == "O":
                            type += self.attrLabel.get(key)
                            Attr.append(key)
                    for key in new_attr:
                        if self.attrLabel.get(key) == "T":
                            type += self.attrLabel.get(key)
                            Attr.append(key)
                    factData.append({"id": id, "type": type, "obverAttr": Attr, "slice": slice, "num": self.num[i],
                                     "slice_data": self.slice_data[i]})
                    id += 1
        # id = 0
        # for attr in obverAttr:
        #     for slice in self.all_slice:
        #         keys = []
        #         values = []
        #         for element in slice:
        #             keys.extend(list(element.keys()))
        #             values.extend(list(element.values()))
        #         # Judging that observation attributes and subspaces do not coincide
        #         if len(set(attr) & set(keys)) == 0:
        #             table = self.table
        #             # Filter out factdata with empty data
        #             for key, value in zip(keys, values):
        #                 table = table[table[key] == value]
        #             if len(list(filter(lambda x: len(list(table[x])) > 0, attr))) == len(attr):
        #                 # Defining the type of observation attributes data, e.g., QQ, QN, QT
        #                 type = ""
        #                 for key in attr:
        #                     type += self.attrLabel.get(key)
        #                 all_factData.append({"id": id, "type": type, "obverAttr": attr, "slice": slice})
        #                 id += 1
        # print("factData Size: ", len(factData))
        return factData, factData

    def checkFactType(self, factdata):
        type = factdata['type']
        slice = factdata['slice']
        if type == 'QN':
            for s in slice:
                if self.attrLabel[list(s.keys())[0]] == 'N':
                    factdata['type'] = factdata['type'].replace('N', '', 1)
                    factdata['obverAttr'].remove(list(s.keys())[0])
        elif type == 'QT':
            for s in slice:
                if self.attrLabel[list(s.keys())[0]] == 'T':
                    factdata['type'] = factdata['type'].replace('T', '', 1)
                    factdata['obverAttr'].remove(list(s.keys())[0])
        elif type == 'QNN':
            for s in slice:
                if self.attrLabel[list(s.keys())[0]] == 'N':
                    factdata['type'] = factdata['type'].replace('N', '', 1)
                    factdata['obverAttr'].remove(list(s.keys())[0])
        elif type == 'QQT':
            for s in slice:
                if self.attrLabel[list(s.keys())[0]] == 'T':
                    factdata['type'] = factdata['type'].replace('T', '', 1)
                    factdata['obverAttr'].remove(list(s.keys())[0])
        elif type == 'QNT':
            for s in slice:
                if self.attrLabel[list(s.keys())[0]] == 'T':
                    factdata['type'] = factdata['type'].replace('T', '', 1)
                    factdata['obverAttr'].remove(list(s.keys())[0])
                elif self.attrLabel[list(s.keys())[0]] == 'N':
                    factdata['type'] = factdata['type'].replace('N', '', 1)
                    factdata['obverAttr'].remove(list(s.keys())[0])
        return factdata

    def checkFactTask(self, task, factdata):
        slice_data = factdata['slice_data']
        obverAttr = factdata['obverAttr']
        if task == 'proportion':
            for k in obverAttr:
                if self.attrLabel[k] == 'N':
                    data = set(list(slice_data[k]))
                    if len(data) <= 1 or len(data) >= 8:
                        return False
                    else:
                        return True
        return True

    def getVisList(self):
        visList = {}
        # encoding_visList={}
        for factdata in self.factData:

            factdata = self.checkFactType(factdata)
            # For each combination, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
            # type = ""
            # if factdata.get('type') in designSpace:
            #     type = factdata.get('type')
            # else:
            #     type = ''.join(reversed(factdata.get('type')))
            #     factdata['obverAttr'] = list(reversed(factdata.get('obverAttr')))

            # For each datafact, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute

            if factdata.get('type') in designSpace:
                type = factdata.get('type')
                for d_counter in range(len(designSpace[type]["designs"])):
                    # Create reference to a design that matches the attribute combination.
                    design = copy.deepcopy(designSpace[type]["designs"][d_counter])

                    task = design["task"]

                    if self.checkFactTask(task, factdata):
                        # Generate Vega-Lite specification along with it"s relevance score for the attribute and task combination.
                        vl_genie = self.getVis(design, type, factdata.get('obverAttr'), factdata.get('slice'))
                        text = self.getText(design, type, factdata.get('obverAttr'), factdata.get('slice'))
                        visList[str(factdata.get('id')) + '-' + str(d_counter)] = {"task": task,
                                                                                   "vis": vl_genie.vl_spec,
                                                                                   "text": text}
                    # encoding_visList[str(factdata.get('id')) + '-' + str(d_counter)] = {"task": task, "vis": vl_genie.vl_spec}
        # for factdata in self.all_factData:
        #     vis_objects = list()
        #     # For each combination, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
        #     type = ""
        #     if factdata.get('type') in designSpace:
        #         type = factdata.get('type')
        #     else:
        #         type = ''.join(reversed(factdata.get('type')))
        #         factdata['obverAttr'] = list(reversed(factdata.get('obverAttr')))
        #
        #     # For each datafact, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
        #     for d_counter in range(len(designSpace[type]["designs"])):
        #         # Create reference to a design that matches the attribute combination.
        #         design = copy.deepcopy(designSpace[type]["designs"][d_counter])
        #
        #         task = design["task"]
        #         # Generate Vega-Lite specification along with it"s relevance score for the attribute and task combination.
        #         vl_genie = self.getVis(design, type, factdata.get('obverAttr'), factdata.get('slice'))
        #         train_visList[str(factdata.get('id')) + '-' + str(d_counter)] = {"task": task, "vis": vl_genie.vl_spec}
        #         # encoding_visList[str(factdata.get('id')) + '-' + str(d_counter)] = {"task": task, "vis": vl_genie.vl_spec}
        # # Shuffle the data
        # dict_key_ls = list(visList.keys())
        # random.shuffle(dict_key_ls)
        # new_visList = {}
        # for key in dict_key_ls:
        #     new_visList[key] = visList.get(key)
        # Generate datasets for visualization

        train_visList = copy.deepcopy(visList)
        new_visList = json.dumps(visList, indent=4)
        with open(self.vis_data_path, 'w') as vis_file:
            vis_file.write(new_visList)

        # Generate datasets for variational coding
        # print(len(visList))
        with open(self.encoding_input_path, 'w') as vae_file:
            for key in visList:
                spec = visList.get(key)["vis"]

                # Delete useless encoding information
                del spec["$schema"]
                del spec["data"]
                del spec["title"]

                spec = {key: {"task": visList.get(key)["task"], "vis": spec}}
                vae_file.write(json.dumps(spec) + "\n")

        # Generate datasets for variational coding training
        # print(train_visList)
        with open(self.train_data_path, 'w') as vae_file:
            for key in train_visList:
                spec = train_visList.get(key)["vis"]

                # Delete useless encoding information
                del spec["$schema"]
                del spec["data"]
                del spec["title"]

                spec = {key: {"task": train_visList.get(key)["task"], "vis": spec}}
                vae_file.write(json.dumps(spec) + "\n")

    def getVis(self, design, type, obverAttr, slice):

        # craet a new Vega-Lite spec
        vl_genie = Generator(self.table, self.attrLabel)

        # MAP the attributes to the DESIGN spec.
        for index, attr in enumerate(obverAttr):
            dim = design["priority"][index]  # Dimension: x, y, color, size, tooltip, ...
            agg = design[dim]["agg"]  # Aggregate: sum, mean, ...
            datatype = type[index]

            # Update the design with the attribute. It could be referenced later.
            design[dim]["attr"] = attr
            design[dim]["is_defined"] = True

            # Set the default VIS mark type. Note: Can be overridden later.
            vl_genie.set_vis_type(design["vis_type"])

            # Set the encoding Note: Can be overridden later.
            vl_genie.set_encoding(dim, attr, datatype, agg)

        # If an attribute is dual-encoded e.g. x axis as well as count of y axis, the attribute is supposed to be encoded to both channels.
        for encoding in design["mandatory"]:
            if not design[encoding]["is_defined"]:
                attr_reference = design[encoding]["attr_ref"]
                attr = design[attr_reference]["attr"]
                datatype = self.attrLabel.get(attr)
                agg = design[encoding]["agg"]
                vl_genie.set_encoding(encoding, attr, datatype, agg)

        # Set slice subspace
        vl_genie.setSlice(slice)

        # Set title
        vl_genie.setTitle(slice)

        # AESTHETICS
        # ------------------
        # Format ticks (e.g. 10M, 1k, ... ) for Quantitative axes
        vl_genie.add_tick_format()
        # ------------------

        # Enable Tooltips
        # ------------------
        vl_genie.add_tooltip()
        # ------------------

        #  Finally, let"s set the data and Rock"n Roll!
        # ------------------
        vl_genie.set_data(self.vis_table_path)
        # ------------------

        return vl_genie

    def getText(self, design, type, obverAttr, slices):
        tabletext = ''  # 描述图表的文本
        f = ""
        filters = []
        for slice in slices:
            key = list(slice.keys())[0]
            value = list(slice.values())[0]
            if self.attrLabel.get(key) == "Q":
                table = self.table.copy()
                table["binned"] = pd.cut(table[key], 3, labels=['Q1', 'Q2', 'Q3'])
                table = table[table["binned"] == value]
                data = list(table[key])
                if value == "Q1":
                    f += key + " = " + "low level, "
                elif value == "Q2":
                    f += key + " = " + "medium  level, "
                elif value == "Q3":
                    f += key + " = " + "high level, "
                filters.append({key: [min(data), max(data)]})
            else:
                f += key + " = " + str(value) + ", "
                filters.append({key: value})

        table = self.table.copy()
        for fl in filters:
            if isinstance(list(fl.values())[0], list):
                key = list(fl.keys())[0]
                value = list(fl.values())[0]
                table = table[table[key] >= value[0]]
                table = table[table[key] <= value[1]]
            else:
                key = list(fl.keys())[0]
                value = list(fl.values())[0]
                table = table[table[key] == value]
        if design['task'] == 'distribution':
            if type[0] == 'Q':
                insight = "in " + obverAttr[0] + ", the maximum is " + str(
                    round(max(list(table[obverAttr[0]])), 2)) + ", the minimum is " + str(
                    round(min(list(table[obverAttr[0]])), 2))
                tabletext += f
                tabletext += insight
            elif type[0] == 'N':
                insight = "in " + obverAttr[0] + ", the most is " + str(
                    round(max(list(table[obverAttr[0]].value_counts())), 2)) + ", the least is " + str(
                    round(min(list(table[obverAttr[0]].value_counts())), 2))
                tabletext += f
                tabletext += insight


        elif design['task'] == 'proportion':
            if type[0] == 'Q':
                insight = "in " + obverAttr[0] + ", the largest proportion is " + str(
                    round(max(list(table[obverAttr[0]])) / sum(
                        list(table[obverAttr[0]])), 2)) + ", the smallest proportion is " + str(
                    round(min(list(table[obverAttr[0]])) / sum(list(table[obverAttr[0]])), 2))
                tabletext += f
                tabletext += insight
            elif type[0] == 'N':
                insight = "in " + obverAttr[0] + ", the largest proportion is " + str(
                    round(max(list(table[obverAttr[0]].value_counts())) / sum(
                        list(table[obverAttr[0]].value_counts())), 2)) + ", the smallest proportion is " + str(
                    round(min(list(table[obverAttr[0]].value_counts())) / sum(list(table[obverAttr[0]].value_counts())),
                          2))
                tabletext += f
                tabletext += insight
        elif design['task'] == 'trend':
            if type == 'QT':
                # This is very interesting about the changes in regional trends after using the country as the filter condition, the highest point is 1, the lowest point is 1, and the average is 1.
                # tabletext = 'This ' + design['vis_type'] + ',filtered by ' + str_slcie + ',shows the distribution by ' + str_obat + ' as some attributes where the maximum value is '+ str(heapq.nlargest(1, df[obverAttr[0]])[0])+' and the minimum value is '+ str(heapq.nsmallest(1, df[obverAttr[0]])[0])+ ' and the average value is '+ str( round(df[obverAttr[0]].mean(axis=0),5))
                tabletext = "trend"


        elif design['task'] == 'correlation':
            if type[:2] == 'QQ':
                A = list(table[obverAttr[0]])
                B = list(table[obverAttr[1]])
                if len(A) >= 2:
                    var = list(stats.pearsonr(A, B))[0]
                else:
                    var = 0
                insight = "the correlation coefficient between " + obverAttr[0] + " and " + obverAttr[1] + " is " + str(
                    round(var, 2))
                tabletext += f
                tabletext += insight


        elif design['task'] == 'derived_value':
            if type[0] == 'Q':
                insight = "in " + obverAttr[0] + ", the maximum is " + str(
                    round(max(list(table[obverAttr[0]])), 2)) + ", the minimum is " + str(
                    round(min(list(table[obverAttr[0]])), 2))
                tabletext += f
                tabletext += insight
            elif type[0] == 'N':
                insight = "in " + obverAttr[0] + ", the most is " + str(
                    round(max(list(table[obverAttr[0]].value_counts())), 2)) + ", the least is " + str(
                    round(min(list(table[obverAttr[0]].value_counts())), 2))
                tabletext += f
                tabletext += insight

        return tabletext


if __name__ == '__main__':
    path = "happiness"
    table_path = "../data/" + path + ".csv"
    vis_table_path = "../static/data/" + path + ".csv"
    encoding_input_data_path = "../data/" + path + ".txt"
    encoding_train_data_path = "../data/train_" + path + ".txt"
    vis_display_vegalite_data_path = "../server/static/vis/" + path + ".json"
    extractor = Extractor(table_path=table_path,
                          vis_table_path=vis_table_path,
                          train_data_path=encoding_train_data_path,
                          vis_data_path=vis_display_vegalite_data_path,
                          encoding_input_path=encoding_input_data_path)
    extractor.dataPreprocessing()
    extractor.getVisList()
