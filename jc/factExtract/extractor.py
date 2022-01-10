from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from jc.utils import constants
from jc.utils.designSpace import designSpace
from jc.visGenerate.generator import Generator
import csv
import pandas as pd
from itertools import combinations
from functools import reduce
import copy


class Extractor:

    # variable list

    def __init__(self, table_path):
        # variable list#

        # table path
        self.table_path = table_path

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
                    keys.extend(element.keys())
                    values.extend(element.values())
                # Judging that observation attributes and subspaces do not coincide
                if len(set(attr) & set(keys)) == 0:
                    table = self.table
                    # Filter out factdata with empty data
                    for key, value in zip(keys, values):
                        table = table[table[key] == value]
                    if len(list(filter(lambda x: len(list(self.table[x])) > 0, attr))) == len(attr):
                        # Defining the type of observation attributes data, e.g., QQ, QN, QT
                        type = ""
                        for key in attr:
                            type += self.attrLabel.get(key)
                        factData.append({"id": id, "type": type, "obverAttr": attr, "slice": slice})
                        id += 1
        return factData

    def getVisList(self):
        for factdata in self.factData:
            vis_objects = list()
            # For each combination, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
            type=""
            if factdata.get('type') in designSpace:
                type = factdata.get('type')
            else:
                type = ''.join(reversed(factdata.get('type')))

            # For each datafact, there are multiple design solutions, e.g. histogram or strip plot for a "quantitative (Q)" attribute
            for d_counter in range(len(designSpace[type]["designs"])):

                # Create reference to a design that matches the attribute combination.
                design = copy.deepcopy(designSpace[type]["designs"][d_counter])

                # Generate Vega-Lite specification along with it"s relevance score for the attribute and task combination.
                vl_genie = self.getVis(design, type, factdata.get('obverAttr'),factdata.get('slice'))

    def getVis(self,design, type,obverAttr,slice):
        # CREATE a new Vega-Lite Spec
        vl_genie = Generator()



extractor = Extractor("../data/cars-w-year.csv")
extractor.printTablePath()
extractor.dataPreprocessing()
extractor.getVisList()



