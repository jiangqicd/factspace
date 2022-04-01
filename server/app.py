import pandas as pd
import json
from flask import Flask, jsonify, request, Blueprint, render_template, abort, send_from_directory
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
from sklearn import preprocessing
from collections import Counter
import warnings

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
    encoding = float(request.form['encoding'])
    logical = float(request.form['logical'])
    score = float(request.form['score'])
    coordinate = []
    for el in dataset:
        coordinate.append([el["cx"], el["cy"]])
    coordinate = np.array(coordinate)
    labels = list(KMeans(n_clusters=11).fit_predict(coordinate))

    # labels = list(DBSCAN(eps=20, min_samples=10).fit_predict(coordinate))
    print("-----------------------------------", len(set(labels)))
    for i in range(len(labels)):
        dataset[i]["label"] = labels[i]
    search = Searcher(facts=dataset, start=start, end=end, encoding_weight=encoding, logical_weight=logical,
                      score_weight=score)
    search.compute()
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
        coordinate.append([el["cx"], el["cy"]])
    coordinate = np.array(coordinate)

    labels = list(KMeans(n_clusters=11).fit_predict(coordinate))

    # labels = list(DBSCAN(eps=20, min_samples=10).fit_predict(coordinate))
    print("-----------------------------------", len(set(labels)))
    for i in range(len(labels)):
        dataset[i]["label"] = labels[i]

    storyline = StoryGenerator("static/data/happiness.csv", dataset, "static/data/happiness_js_divergence.json",
                               cluster_data=dataset, level=level, custom=custom)

    storyline.generateStorylines()

    print(storyline.storyline)

    # result = list(DBSCAN(eps=10, min_samples=4).fit_predict(dataset))
    # for i in result:
    #     out.append(int(i))

    data = str(storyline.storyline)
    data = eval(data)
    dataset = str(dataset)
    dataset = eval(dataset)
    return json.dumps({"storyline": data, "dataset": dataset})


@app.route('/scatter', methods=['POST'])
def scatter():
    dataset = request.form['dataset']

    dataset = dataset.split(".")[0]

    path = "static/vis/" + dataset + ".json"

    table_path = "static/data/" + dataset + ".csv"

    table = pd.read_csv(table_path)

    columns = [""]

    columns.extend(list(table.columns))

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
        out.append({"id": k, "task": load_dict[k]["task"], "mark": load_dict[k]["vis"]["mark"]["type"],
                    "vis": load_dict[k]["vis"], "ex": distance[k]["ed"][0],
                    "ey": distance[k]["ed"][1], "lx": distance[k]["ld"][0], "ly": distance[k]["ld"][1],
                    "score": str(fact_score[k]), "text": load_dict[k]["text"]})
    for i in out:
        print(i)
    return json.dumps({"data": out, "columns": columns, "tasks": tasks, "subspace": columns})


@app.route('/', methods=['GET'])
def application_homepage():
    try:
        return render_template('datafact.html')
    except TemplateNotFound:
        abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True, port=7001)
