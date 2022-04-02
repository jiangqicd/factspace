# FactExplorer: Towards Better Narrative for Tabular Data through Interactive Fact Embedding

This repository contains source code used to explore and analyze the fact space in tabular data!

## Introduction
In FactExplorer, what users need to do is not low-level data analysis, but advanced fact space exploration. The workflow of the system is as follow.
![](https://github.com/jiangqicd/factspace/blob/main/pipline.png)
FactExplorer, a system designed to help users efficiently and conveniently explore and analyze fact space. In this system, entire facts are automatically extracted from tabular data. A two-factor (visual style and contextual logic) fact embedding approach is introduced to embed facts into the fact space, which provides an overview of all facts and the context of each fact. A multi-perspective storyline generation algorithm is also designed to generate multiple perspectives storylines. The whole facts are well organized to promote exploration and deepen the impression of the fact space for users. Certain interactive components are also implemented to support users to flexibly edit facts and storylines.

## **Function description**
1. Data fact Extraction

   select PUBG’s firearm performance statistics data  as the analysis example.

   | Weapon Name |  Weapon Type   | ...  | Bullet Speed | ...  | HDMG_3 |
   | :---------: | :------------: | :--: | :----------: | :--: | :----: |
   |     AKM     | Assault Rifle  | ...  |     710      | ...  |  51.8  |
   |     Uzi     | Submachine Gun | ...  |     300      | ...  |   21   |
   |     ...     |      ...       | ...  |     ...      | ...  |  ...   |
   |     AWM     |  Sniper Rifle  | ...  |     910      | ...  | 118.1  |

   ```json
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
   }
   ```

   

2. gvae: visual encoding embedding.  

3. logic_distence: contextual logic embedding.  

4. searchPath: transition path search.  

5. server: Front-end system interface.  

6. storylineGenerate: multi-perspective storyline generation.  

7. visGenerate: data fact expression.  

## **Install**
The FactExplorer code has a few dependencies that can be installed using the requirement.txt file.

## **How to use**
(1) Install and configure the development environment according to requirement.txt.

(2) Run preprocessing.py, then system automatically extracts data facts, measures fact similarity.

(3) Run app.py, start the front-end web service。
