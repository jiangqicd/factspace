import pandas as pd
import json
from flask import Flask, jsonify, request, Blueprint, render_template, abort, send_from_directory,current_app
from jinja2 import TemplateNotFound
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans, SpectralClustering
import numpy as np
from logic_distence.get_logic_dis import logic_dis_extractor
from gvae.data_utils import visvae
from factExtract.extractor import Extractor
from searchPath.search_path import Searcher
from factExtract.score import cal_each_fact
from storylineGenerate.storyGenerator import StoryGenerator
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.manifold import MDS
from umap import UMAP
from sklearn import preprocessing
from collections import Counter
import warnings
from procrustes import orthogonal
from pandas.api.types import is_numeric_dtype

# Import our Example Applications

# Initialize the app
app = Flask(__name__)
app.jinja_env.auto_reload = True


@app.route('/searchpath', methods=['POST'])
def search_path():
    dataset = request.form['dataset']
    dataset = json.loads(dataset)
    start = request.form['start']
    end = request.form['end']
    # encoding = float(request.form['encoding'])
    # logical = float(request.form['logical'])
    # score = float(request.form['score'])
    encoding = 0
    logical = 0
    score = 0
    table = request.form['table']
    table = table.split(".")[0]
    table_path = "static/data/" + table + ".csv"
    start_fact = {}
    end_fact = {}
    for n in dataset:
        if n["id"] == start:
            start_fact = n
        if n["id"] == end:
            end_fact = n
    print(start_fact)
    print(end_fact)
    search = Searcher(facts=dataset,
                      table_path=table_path,
                      start=start_fact,
                      end=end_fact,
                      encoding_weight=encoding,
                      logical_weight=logical,
                      score_weight=score)
    search.difference()
    print(search.diff)
    search.pathGenerate()
    path = search.path
    path = eval(str(path))
    return json.dumps({"data": path})


@app.route('/storyline', methods=['POST'])
def storyline():
    dataset = request.form['dataset']
    dataset = json.loads(dataset)

    level = request.form['level']
    custom = request.form['custom']
    print(level)
    # print(dataset)
    coordinate = []
    for el in dataset:
        coordinate.append([el["x"], el["y"]])
    coordinate = np.array(coordinate)

    labels = list(KMeans(n_clusters=11).fit_predict(coordinate))

    # labels = list(DBSCAN(eps=20, min_samples=10).fit_predict(coordinate))
    # print(labels)
    # print("-----------------------------------", len(set(labels)))
    for i in range(len(labels)):
        dataset[i]["label"] = labels[i]

    storyline = StoryGenerator("static/data/happiness.csv", dataset, "static/data/happiness_js_divergence.json",
                               cluster_data=dataset, level=level, custom=custom)

    # storyline.generateStorylines()
    storyline.getTopicFacts()
    storyline.getTok_K_Facts()

    # print(storyline.storyline)

    # data = str(storyline.storyline)
    # data = eval(data)
    # top_k = str(storyline.key_nodes)
    # top_k = eval(top_k)
    # print(top_k)
    dataset = str(dataset)
    dataset = eval(dataset)
    print(dataset)
    return json.dumps({"storyline": [], "dataset": dataset, "top_k": []})


@app.route('/scatter', methods=['POST'])
def scatter():
    time = ['year', 'time', 'date', 'day', 'week', 'month']

    dataset = request.form['dataset']

    dataset = dataset.split(".")[0]

    path = "static/vis/" + dataset + ".json"

    table_path = "static/data/" + dataset + ".csv"

    table = pd.read_csv(table_path)

    columns = [""]

    columns.extend(list(table.columns))

    array = []
    label = []

    subspace = {}
    map_attr_type = {}
    for attr in table.columns:
        label.append(attr)
        array.append(list(table[attr]))
        Tokens = attr.split(" ")
        for token in Tokens:
            if token.lower() in time:
                map_attr_type[attr] = "T"
                subspace[attr] = list(set(list(table[attr])))
        if attr not in map_attr_type:
            if is_numeric_dtype(table[attr]):
                map_attr_type[attr] = "Q"
                subspace[attr] = ["low level", "medium level", "high level"]
            else:
                map_attr_type[attr] = "N"
                subspace[attr] = list(set(list(table[attr])))

    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)

    # # t = StoryGenerator("static/data/happiness.csv", load_dict, "static/data/happiness_js_divergence.json", load_dict)
    # # t.get_JS_divs()
    # # print(t.JS_divs)
    #
    # # get logical distance
    # lde = logic_dis_extractor(load_dict)
    #
    # logic_distence_matrix = lde.logic_detect()
    #
    # standard = preprocessing.MinMaxScaler()
    #
    # logic_distence_matrix = standard.fit_transform(logic_distence_matrix)
    #
    # pca = PCA(n_components=2)
    # tsne = TSNE(n_components=2)
    #
    # ld = pca.fit_transform(logic_distence_matrix)
    #
    # ld = list(standard.fit_transform(ld))
    #
    # # get encoding distance
    #
    # # model_path
    # model_path = "../gvae/trained/happiness/vae_H256_D256_C888_333_L20_B200.hdf5"
    # # rule_path
    # rule_path = "../gvae/trainingdata/happiness/rules-cfg.txt"
    # # encoding data
    # encoding_data = []
    # with open('../data/happiness.txt', 'r') as inputs:
    #     for line in inputs:
    #         line = line.strip()
    #         encoding_data.append(line)
    #
    # outputspec, z, id = visvae(encoding_data, rule_path, model_path)
    #
    # ed = tsne.fit_transform(z)
    #
    # ed = list(standard.fit_transform(ed))

    dis_path = "static/data/distance_" + dataset + ".json"
    with open(dis_path, 'r') as load_f:
        distance = json.load(load_f)
    dis_path = "static/data/logical_distance_" + dataset + ".json"
    with open(dis_path, 'r') as load_f:
        logical_distance = json.load(load_f)
    dis_path = "static/data/visual_distance_" + dataset + ".json"
    with open(dis_path, 'r') as load_f:
        visual_distance = json.load(load_f)
    dis_path = "static/data/" + dataset + "_score.json"
    with open(dis_path, 'r') as load_f:
        fact_score = json.load(load_f)
    out = []
    tasks = []
    tasks.append("")
    for i in load_dict:
        if load_dict[i]["task"] not in tasks:
            tasks.append(load_dict[i]["task"])
    for i, k in enumerate(load_dict):
        # out.append({"id": k, "task": load_dict[k]["task"], "mark": load_dict[k]["vis"]["mark"]["type"],
        #             "vis": load_dict[k]["vis"], "ex": distance[k]["ed"][0],
        #             "ey": distance[k]["ed"][1], "lx": distance[k]["ld"][0], "ly": distance[k]["ld"][1],
        #             "ld_vec": distance[k]["ld_vec"], "ed_vec": distance[k]["ed_vec"],
        #             "score": str(fact_score[k]), "text": load_dict[k]["text"]})
        out.append({"id": k, "task": load_dict[k]["task"], "mark": load_dict[k]["vis"]["mark"]["type"],
                    "ex": visual_distance[k]["ex"],
                    "ey": visual_distance[k]["ey"], "lx": logical_distance[k]["lx"], "ly": logical_distance[k]["ly"],
                    "vis": load_dict[k]["vis"], "x": distance[k]["x"], "y": distance[k]["y"],
                    "score": str(fact_score[k]), "text": load_dict[k]["text"]})
    for i in out:
        print(i)
    return json.dumps(
        {"data": out, "columns": columns, "tasks": tasks, "subspace": subspace, "map_attr_type": map_attr_type,
         "array": array, "label": label})


@app.route('/adjustscatter', methods=['POST'])
def adjust_scatter():
    dataset = request.form['dataset']

    data = request.form['data']

    data = json.loads(data)

    wl = float(request.form['wl'])

    we = float(request.form['we'])

    dataset = dataset.split(".")[0]

    vec_path = "static/data/vec_" + dataset + ".json"

    with open(vec_path, 'r') as load_f:
        vec = json.load(load_f)
    standard = preprocessing.MinMaxScaler()
    ed_vec = []
    ld_vec = []
    for id in vec:
        ed_vec.append(eval(vec[id]["ed_vec"]))
        ld_vec.append(eval(vec[id]["ld_vec"]))
    comb_dis = np.concatenate((np.array(ed_vec) * we, np.array(ld_vec) * wl), axis=1)
    tsne = TSNE(n_components=2, perplexity=25)
    d = tsne.fit_transform(comb_dis)
    # umap = UMAP(random_state=42)
    # d = umap.fit_transform(comb_dis)
    # mds = MDS(n_components=2)
    # d = mds.fit_transform(comb_dis)
    # pca = PCA(n_components=2)
    # d = pca.fit_transform(comb_dis)
    d = list(standard.fit_transform(d))

    for i, k in enumerate(vec):
        data[i]["x"] = str(d[i][0])
        data[i]["y"] = str(d[i][1])

    return json.dumps(data)


@app.route('/', methods=['GET'])
def application_homepage():
    try:
        return render_template('datafact.html')
        # return render_template('baseline.html')
    except TemplateNotFound:
        abort(404)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True, port=7001)
