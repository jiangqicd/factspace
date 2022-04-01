#!/usr/bin/env python
# encoding: utf-8
# @author: jiangqi
# @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
# @contact: jiangqi@zjut.edu.com
# @file: generator.py
# @time: 2022/1/9 20:21
from utils.constants import vl_attribute_types
import pandas as pd

class Generator:
    # todo vis Generation
    def __init__(self, table, attrLabel):
        self.attrLabel = attrLabel
        self.table = table
        self.vl_spec = dict()
        self.vl_spec['$schema'] = 'https://vega.github.io/schema/vega-lite/v4.json'
        self.vl_spec['mark'] = dict()
        self.vl_spec['encoding'] = dict()
        self.vl_spec['transform'] = list()
        self.vl_spec['title'] = dict()
        self.bin = False

    def set_vis_type(self, vis):

        if vis == 'histogram':
            self.vl_spec['mark']['type'] = 'bar'
            self.bin = True

        elif vis == 'barchart':
            self.vl_spec['mark']['type'] = 'bar'

        elif vis == 'linechart':
            self.vl_spec['mark']['type'] = 'line'

        elif vis == 'areachart':
            self.vl_spec['mark']['type'] = 'area'

        elif vis == 'scatterplot':
            self.vl_spec['mark']['type'] = 'point'

        elif vis == 'boxplot':
            self.vl_spec['mark']['type'] = 'boxplot'

        elif vis == 'stripplot':
            self.vl_spec['mark']['type'] = 'tick'

        elif vis == 'piechart':
            self.vl_spec['mark']['type'] = 'arc'

        elif vis == 'donutchart':
            self.vl_spec['mark']['type'] = 'arc'
            # ToDo:- Smartly set the below value depending on the chart
            # The below value is in Pixels and independent of the generated chart dimensions which can be problematic when there are single v/s multiple donut charts.
            # Thus, setting the innerRadius value to 50 for now. Developers will have to override it downstream.
            self.vl_spec['mark']['innerRadius'] = 40

        elif vis == 'datatable':
            # Remove unneeded encodings
            del self.vl_spec['mark']
            del self.vl_spec['encoding']

            # Derive a new "row_number" variable with a sequence of numbers (used as index / counter later on)
            self.vl_spec["transform"] = [{
                "window": [{"op": "row_number", "as": "row_number"}]
            }]

            # Horizontally concatenate each attribute's column (VIS with mark type = text)
            self.vl_spec["hconcat"] = []

    def set_encoding(self, dim, attr, attr_type, aggregate=None):

        self.vl_spec['encoding'][dim] = dict()
        self.vl_spec['encoding'][dim]['field'] = attr
        self.vl_spec['encoding'][dim]['type'] = vl_attribute_types[attr_type]
        self.vl_spec['encoding'][dim]['aggregate'] = aggregate

        if dim == 'x':
            if self.bin:
                self.vl_spec['encoding'][dim]['bin'] = True

    def set_data(self, dataUrl):
        # type: (list) -> None
        """
        Set domain data for the visualization

        """
        self.vl_spec['data'] = {'url': dataUrl, 'format': {'type': 'csv'}}

    def add_tick_format(self):
        for dim in self.vl_spec['encoding']:
            if dim in ['x', 'y'] and self.vl_spec['encoding'][dim]['type'] == 'quantitative':
                if 'axis' not in self.vl_spec['encoding'][dim]:
                    self.vl_spec['encoding'][dim]['axis'] = dict()
                self.vl_spec['encoding'][dim]['axis']["format"] = "s"

    def add_tooltip(self):
        self.vl_spec['mark']['tooltip'] = True

    def get_encoding(self, dim):
        return self.vl_spec['encoding'][dim]

    def unset_encoding(self, dim):
        if dim in self.vl_spec['encoding']:
            del self.vl_spec['encoding'][dim]

    def setSlice(self, slices):
        filters = []
        for slice in slices:
            key = list(slice.keys())[0]
            value = list(slice.values())[0]
            if self.attrLabel.get(key) == "Q":
                table = self.table.copy()
                table["binned"] = pd.cut(table[key], 3, labels=['Q1', 'Q2', 'Q3'])
                data = list(table[table["binned"] == value][key])
                filters.append({"field": key, "range": [min(data), max(data)]})
            else:
                filters.append({"field": key, "oneOf": [value]})
        if len(filters) == 1:
            self.vl_spec['transform'].append({'filter': filters[0]})
        else:
            self.vl_spec['transform'].append({'filter': {'and': filters}})

    def setTitle(self, slices):
        filters = []
        for slice in slices:
            key = list(slice.keys())[0]
            value = list(slice.values())[0]
            if self.attrLabel.get(key) == "Q":
                table = self.table.copy()
                table["binned"] = pd.cut(table[key], 3, labels=['Q1', 'Q2', 'Q3'])
                data = list(table[table["binned"] == value][key])
                # filters.append(str(key) + " = " + "[" + str(min(data)) + " , " + str(max(data)) + "]")
                if value=="Q1":
                    filters.append(str(key) + " = " + "low level")
                elif value=="Q2":
                    filters.append(str(key) + " = " + "medium level")
                elif value=="Q3":
                    filters.append(str(key) + " = " + "high level")

            else:
                filters.append(str(key) + " = " + str(value))
        if len(filters) == 1:
            self.vl_spec['title']['text'] = filters[0]
        else:
            title = []
            for i in range(len(filters)):
                title.append(filters[i])
            self.vl_spec['title']['text'] = title
        self.vl_spec['title']['align'] = "center"
