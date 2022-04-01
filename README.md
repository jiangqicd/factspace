# FactExplorer: Towards Better Narrative for Tabular Data through Interactive Fact Embedding

This repository contains source code used to explore and analyze the fact space in tabular data!

## Introduction
In FactExplorer, what users need to do is not low-level data analysis, but advanced fact space exploration. The workflow of the system is as follow.
![](https://github.com/jiangqicd/factspace/blob/main/pipline.png)
FactExplorer, a system designed to help users efficiently and conveniently explore and analyze fact space. In this system, entire facts are automatically extracted from tabular data. A two-factor (visual style and contextual logic) fact embedding approach is introduced to embed facts into the fact space, which provides an overview of all facts and the context of each fact. A multi-perspective storyline generation algorithm is also designed to generate multiple perspectives storylines. The whole facts are well organized to promote exploration and deepen the impression of the fact space for users. Certain interactive components are also implemented to support users to flexibly edit facts and storylines.

## **Function description**
factExtract: data fact extraction, scoring, and filtering.  
gvae: visual encoding embedding.  
logic_distence: contextual logic embedding.  
searchPath: transition path search.  
server: Front-end system interface.  
storylineGenerate: multi-perspective storyline generation.  
visGenerate: data fact expression.  
## **Install**
The FactExplorer code has a few dependencies that can be installed using the requirement.txt file.

## **How to use**
(1) Install and configure the development environment according to requirement.txt.

(2) Run preprocessing.py, then system automatically extracts data facts, measures fact similarity.

(3) Run app.py, start the front-end web service。

