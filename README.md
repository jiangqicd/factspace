# *FE<sup>2</sup>DA*: Fact Embedding-based Exploratory Data Analysis for Tabular Data

You can click the link below to watch the demo video!
[![FE2DA: Fact Embedding-based Exploratory Data Analysis for Tabular Data](https://github.com/jiangqicd/factspace/blob/main/overview.png)](https://youtu.be/2u1hItmd3Jg "FE2DA: Fact Embedding-based Exploratory Data Analysis for Tabular Data")
## Introduction
In FactExplorer, what users need to do is not low-level data analysis, but advanced data fact exploration. The framework of FactExplorer is as follow, which consists of threecore modules: fact extraction, fact embedding, and fact exploration.
![](https://github.com/jiangqicd/factspace/blob/main/pipline.png)
We present a fact-based frame-work for tabular data analysis. Such framework is top-down and adequately interacting, which allows users to perform an overview to detail data exploration. In particular, we first extract data facts from underlying tabular data. These facts are then embedded as semantic vectors and projected into a 2D scatterplot to provide an overview. Finally, FactExplorer also supports two powerful interactive exploration techniques to facilitate insight generation.
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
   Computing visual-based similarity matrix from GVAE-based features
   
$$
\left[
\begin{matrix}
    D_{V}(1,1) & D_{V}(1,2) & \cdots & D_{V}(1,N) \\\\
    D_{V}(2,1) & D_{V}(2,2) & \cdots & D_{V}(2,N) \\\\
    \vdots     & \vdots     & \ddots & \vdots     \\\\
    D_{V}(N,1) & D_{V}(N,2) & \cdots & D_{V}(N,N)
\end{matrix}
\right]
$$



   ###### logical embedding

   Extract logical embedding via get_logic_dis.py

   Get the logical distance among data facts through fcat logic detection. Four logical relationships are adopted: *Parallelism*,  *Granularity*,  *Temporal*, *Contrast*.

   ***Parallelism** (**D**<sub>p</sub>)* indicates that a fact pair are logically parallel, they are just the representations of same data items from different perspectives. Therefore, the judgment of this logical relationship is based on whether they have the same data subspace, and different observation dimensions or aggregation operations.

   ***Granularity** (**D**<sub>g</sub>)* reflects the number of data items in fact. A smaller granularity data subject can be obtained by adding a new filter. Similarly, removing a existing filter can get a larger granularity data subject. Therefore, whether there is granularity zoom-in or zoom-out on the premise of no other changes is used as a detection rule.

   ***Temporal** (**D**<sub>t</sub>)* is also an important contextual logic, which represents the time sequence of facts. The distinguishing feature of this logical is that facts have different temporal filter, which can be utilized as a detection rule.

   ***Contrast** (**D**<sub>c</sub>)* indicates comparison between two facts, are often used to observe the difference of the same fact type under different data items. In this contextual logic, facts have the same fact type and observation dimensions, and the data subspace as the subject of the comparison must be different.

   *logic(m,n)=[ **D**<sub>p</sub> , **D**<sub>g</sub> , **D**<sub>t</sub> , **D**<sub>c</sub>]*

   Logical similarity for each fact

   ```python
   logical_similarity=[[0,1,0,1] , [0,1,1,0] , ... , [1,1,0,1]]
   ```

   Weight different logical relationships

   *weighted_similarity(m,n)=[ **w**<sub>p</sub> x **S**<sub>p</sub> , **w**<sub>g</sub> x **S**<sub>g</sub> , **w**<sub>t</sub> x **S**<sub>t</sub> , **w**<sub>c</sub>x**S**<sub>c</sub>]*

   The weighted similarity for each fact

   ```
   weighted_similarity=[[0,0.36,0,0.64] , [0,0.42,0.78,0] , ... , [0.33,0.37,0,0.6]]
   ```

   Logical-based similarity matrix

$$
\left[
\begin{matrix}
    D_{L}(1,1) & D_{L}(1,2) & \cdots & D_{L}(1,N) \\\\
    D_{L}(2,1) & D_{L}(2,2) & \cdots & D_{L}(2,N) \\\\
    \vdots     & \vdots     & \ddots & \vdots     \\\\
    D_{L}(N,1) & D_{L}(N,2) & \cdots & D_{L}(N,N)
\end{matrix}
\right] 
$$

## **Install**
The FactExplorer code has a few dependencies that can be installed using the requirement.txt file.

## **How to use**
(1) Install and configure the development environment according to requirement.txt.

(2) Run preprocessing.py, then system automatically extracts data facts, measures fact similarity.

(3) Run app.py, start the front-end web service.



