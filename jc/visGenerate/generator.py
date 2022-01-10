#!/usr/bin/env python
# encoding: utf-8
#@author: jiangqi
#@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
#@contact: jiangqi@zjut.edu.com
#@file: generator.py
#@time: 2022/1/9 20:21
import nl4dv

class Generator:
    #todo vis Generation
    def __init__(self):
        self.vl_spec = dict()
        self.vl_spec['$schema'] = 'https://vega.github.io/schema/vega-lite/v4.json'
        self.vl_spec['mark'] = dict()
        self.vl_spec['encoding'] = dict()
        self.vl_spec['transform'] = list()
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
            self.vl_spec['mark']['innerRadius'] = 50

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