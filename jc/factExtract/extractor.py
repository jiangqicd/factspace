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
import random
from random import shuffle


class Extractor:

    # variable list

    def __init__(self, table_path, vis_table_path, train_data_path, vis_data_path):
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

        # fact data space
        self.factData = dict()

    def printTablePath(self):
        print(self.table_path)

    # 数据预处理
    def dataPreprocessing(self):

        attributes = self.table.columns
        self.getLabelAttr(attributes)
        print(self.attrLabel)
        self.slice = self.getSubspace()
        self.factData = self.getFactData()
        print(self.factData)

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

        slice = []
        # print(self.table['MPG'])
        # # Equally spaced binning of numeric data
        # print(pd.cut(self.table['MPG'],4,labels=['Q1','Q2','Q3','Q4']))

        key_list = list(
            filter(lambda key: self.attrLabel.get(key) == "N" or self.attrLabel.get(key) == "T", self.attrLabel.keys()))

        for key in key_list:
            for value in set(list(self.table[key])):
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
            slice.extend(combin(valueBinary))

        return slice

    # Get the data composition space for each data fact
    def getFactData(self):
        factData = []
        # ---to get fact {"obversed attr":[slice1,slice2.....]}----

        # Two layers of observation attributes
        obverAttr = []
        for attr in self.table.columns:
            obverAttr.append([attr])
        for comb in list(combinations(self.table.columns, 2)):
            obverAttr.append(list(comb))

        # Combining observation attributes and subspace slices
        id = 0
        for attr in obverAttr:
            for slice in self.slice:
                keys = []
                values = []
                for element in slice:
                    keys.extend(list(element.keys()))
                    values.extend(list(element.values()))
                # Judging that observation attributes and subspaces do not coincide
                if len(set(attr) & set(keys)) == 0:
                    table = self.table
                    # Filter out factdata with empty data
                    for key, value in zip(keys, values):
                        table = table[table[key] == value]
                    if len(list(filter(lambda x: len(list(table[x])) > 0, attr))) == len(attr):
                        # Defining the type of observation attributes data, e.g., QQ, QN, QT
                        type = ""
                        for key in attr:
                            type += self.attrLabel.get(key)
                        factData.append({"id": id, "type": type, "obverAttr": attr, "slice": slice})
                        id += 1
        print("factData Size: ", len(factData))
        return factData

    def getVisList(self):
        visList = {}
        for factdata in self.factData:
            vis_objects = list()
            # For each combination, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
            type = ""
            if factdata.get('type') in designSpace:
                type = factdata.get('type')
            else:
                type = ''.join(reversed(factdata.get('type')))
                factdata['obverAttr'] = list(reversed(factdata.get('obverAttr')))

            # For each datafact, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
            for d_counter in range(len(designSpace[type]["designs"])):
                # Create reference to a design that matches the attribute combination.
                design = copy.deepcopy(designSpace[type]["designs"][d_counter])

                # Generate Vega-Lite specification along with it"s relevance score for the attribute and task combination.
                vl_genie = self.getVis(design, type, factdata.get('obverAttr'), factdata.get('slice'))
                visList[str(factdata.get('id')) + '-' + str(d_counter)] = vl_genie.vl_spec

        # Shuffle the data
        dict_key_ls = list(visList.keys())
        random.shuffle(dict_key_ls)
        new_visList = {}
        for key in dict_key_ls:
            new_visList[key] = visList.get(key)

        # Generate datasets for variational coding
        with open(self.train_data_path, 'w') as vae_file:
            for key in new_visList:
                spec = new_visList.get(key)

                # Delete useless encoding information
                # del spec["$schema"]
                # del spec["data"]
                # del spec["title"]

                spec = {key: spec}
                vae_file.write(json.dumps(spec) + "\n")

        # Generate datasets for visualization
        new_visList = json.dumps(new_visList, indent=4)
        with open(self.vis_data_path, 'w') as vis_file:
            vis_file.write(new_visList)

    def getVis(self, design, type, obverAttr, slice):

        # craet a new Vega-Lite spec
        vl_genie = Generator()

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


if __name__ == '__main__':
    extractor = Extractor("../data/happiness.csv", "../static/data/happiness.csv", "../data/happiness.txt",
                          "../server/static/vis/happiness.json")
    extractor.dataPreprocessing()
    extractor.getVisList()
