# FactExplorer: Towards Better Narrative for Tabular Data through Interactive Fact Embedding

This repository contains source code used to explore and analyze the fact space in tabular data!

## Introduction
In FactExplorer, what users need to do is not low-level data analysis, but advanced fact space exploration. The workflow of the system is as follow.
![](https://github.com/jiangqicd/factspace/blob/main/pipline.png)
FactExplorer, a system designed to help users efficiently and conveniently explore and analyze fact space. In this system, entire facts are automatically extracted from tabular data. A two-factor (visual style and contextual logic) fact embedding approach is introduced to embed facts into the fact space, which provides an overview of all facts and the context of each fact. A multi-perspective storyline generation algorithm is also designed to generate multiple perspectives storylines. The whole facts are well organized to promote exploration and deepen the impression of the fact space for users. Certain interactive components are also implemented to support users to flexibly edit facts and storylines.

## **Function description**
1. ##### Data fact Extraction

   ###### select PUBG’s firearm performance statistics data  as input data

   | Weapon Name |  Weapon Type   | ...  | Bullet Speed | ...  | HDMG_3 |
   | :---------: | :------------: | :--: | :----------: | :--: | :----: |
   |     AKM     | Assault Rifle  | ...  |     710      | ...  |  51.8  |
   |     Uzi     | Submachine Gun | ...  |     300      | ...  |   21   |
   |     ...     |      ...       | ...  |     ...      | ...  |  ...   |
   |     AWM     |  Sniper Rifle  | ...  |     910      | ...  | 118.1  |

   ###### Extract data facts via extractor.py

    "794-0"  is the id number of each fact, "task"  indicates the fact type, "vis" indicates the fact visualization expression, and  "text" indicates the fact text description

   ```json
    "794-0": {
           "task": "correlation",
           "vis": {
               "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
               "mark": {
                   "type": "point",
                   "tooltip": true
               },
               "encoding": {
                   "x": {
                       "field": "Shots to Kill (Chest)",
                       "type": "quantitative",
                       "aggregate": null,
                       "axis": {
                           "format": "s"
                       }
                   },
                   "y": {
                       "field": "Damage",
                       "type": "quantitative",
                       "aggregate": null,
                       "axis": {
                           "format": "s"
                       }
                   },
                   "color": {
                       "field": "Bullet Speed",
                       "type": "quantitative",
                       "aggregate": null
                   }
               },
               "transform": [
                   {
                       "filter": {
                           "and": [
                               {
                                   "field": "Damage",
                                   "range": [
                                       23,
                                       79
                                   ]
                               },
                               {
                                   "field": "Bullet Speed",
                                   "range": [
                                       250,
                                       380
                                   ]
                               }
                           ]
                       }
                   }
               ],
               "title": {
                   "text": [
                       "Damage = low level",
                       "Bullet Speed = low level"
                   ],
                   "align": "center"
               },
               "data": {
                   "url": "../static/data/pubg.csv",
                   "format": {
                       "type": "csv"
                   }
               }
           },
           "text": "Damage = low level, Bullet Speed = low level, the correlation coefficient between Shots to Kill (Chest) and Damage is -0.77"
       },
   ```

   

2. ##### Data fact embedding

   ###### visual encoding embedding

   Extract visual encoding embedding via data_utils.visvae()

   Embed the visual encoding of data fact into a 20-dimensional latent vector via an GVAE

   ```python
   vector=[-0.08019961 -0.01171272  0.0085084   0.04091895  0.04713326  0.08277792
     0.03038397  0.04326406  0.07168297 -0.05542511 -0.06675147  0.05207219
    -0.02154189  0.02161633 -0.0244385  -0.04470274  0.08967581  0.08091462
     0.01759099  0.07417333]
   ```

   ###### logical embedding

   Extract logical embedding via get_logic_dis.py

   Get the logical distance among data facts through fcat logic detection. Four logical relationships are adopted: *Parallelism*,  *Granularity*,  *Temporal*, *Contrast*.

   ***Parallelism** (**D**<sub>p</sub>)* indicates that a fact pair are logically parallel, they are just the representations of same data items from different perspectives. Therefore, the judgment of this logical relationship is based on whether they have the same data subspace, and different observation dimensions or aggregation operations.

   ***Granularity** (**D**<sub>g</sub>)* reflects the number of data items in fact. A smaller granularity data subject can be obtained by adding a new filter. Similarly, removing a existing filter can get a larger granularity data subject. Therefore, whether there is granularity zoom-in or zoom-out on the premise of no other changes is used as a detection rule.

   ***Temporal** (**D**<sub>t</sub>)* is also an important contextual logic, which represents the time sequence of facts. The distinguishing feature of this logical is that facts have different temporal filter, which can be utilized as a detection rule.

   ***Contrast** (**D**<sub>c</sub>)* indicates comparison between two facts, are often used to observe the difference of the same fact type under different data items. In this contextual logic, facts have the same fact type and observation dimensions, and the data subspace as the subject of the comparison must be different.

   *logic(m,n)=[ **D**<sub>p</sub> , **D**<sub>g</sub> , **D**<sub>t</sub> , **D**<sub>c</sub>]*

   ```python
   logic_distence=[[0,1,0,1] , [0,1,1,0] , ... , [1,1,0,1]]
   ```

   Weight different logical relationships

   *logic(m,n)=[ **w**<sub>p</sub> x **D**<sub>p</sub> , **w**<sub>g</sub> x **D**<sub>g</sub> , **w**<sub>t</sub> x **D**<sub>t</sub> , **w**<sub>c</sub>x**D**<sub>c</sub>]*

   ```
   logic_distence=[[0,0.36,0,0.64] , [0,0.32,0.68,0] , ... , [0.33,0.37,0,0.3]]
   ```

   

3. ##### Storyline generation

   Extract logical embedding via storyGenerator.py

   The generated storyline structure is "perspective_1": ["source": fact_source, "target": fact_target, ...]

   ```
   [
     {"perspective_1": [
        {"source": fact_1, "target": fact_4}, 
        {"source": fact_7, "target": fact_3}, 
        {"source": fact_5, "target": fact_9}, 
           ...
        {"source": fact_4, "target": fact_2},]
     },
       {"perspective_2":[
        {"source": fact_4, "target": fact_6}, 
        {"source": fact_7, "target": fact_2}, 
        {"source": fact_3, "target": fact_9}, 
           ...
        {"source": fact_8, "target": fact_1},]
     },
     ...
   ]
   ```

## **Install**
The FactExplorer code has a few dependencies that can be installed using the requirement.txt file.

## **How to use**
(1) Install and configure the development environment according to requirement.txt.

(2) Run preprocessing.py, then system automatically extracts data facts, measures fact similarity.

(3) Run app.py, start the front-end web service.



