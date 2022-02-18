import pandas as pd
import json
from flask import Flask, jsonify, request, Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

from logic_distence.get_logic_dis import logic_dis_extractor
from gvae.data_utils import visvae
from factExtract.extractor import Extractor
from sklearn.decomposition import PCA
from sklearn import preprocessing

# Import our Example Applications

# Initialize the app
app = Flask(__name__)
app.jinja_env.auto_reload = True


# Initialize parse variable
@app.route('/init', methods=['POST'])
def init():
    return jsonify({"message": "Datafact Initialized"})


@app.route('/vis', methods=['POST'])
def vis():
    return jsonify({"message": "NL4DV Initialized"})


@app.route('/setData', methods=['POST'])
def setData():
    dataset = request.form['dataset']
    print(dataset)
    path = "static/data/" + dataset
    ex = Extractor(path, "", "", "")
    attributes = ex.table.columns
    ex.getLabelAttr(attributes)
    Q = []
    T = []
    N = []
    print(ex.attrLabel)
    for k in ex.attrLabel:
        if ex.attrLabel[k] == "Q":
            Q.append(k)
        elif ex.attrLabel[k] == "T":
            T.append(k)
        elif ex.attrLabel[k] == "N":
            N.append(k)
    return json.dumps({"Q": Q, "T": T, "N": N})


@app.route('/scatter', methods=['POST'])
def scatter():
    print("--Computing the scatterplot distance matrix--")
    dataset = request.form['dataset']
    fact = json.loads(request.form['fact'])
    attribute = json.loads(request.form['attribute'])
    wwll = request.form['wl']
    wwee = request.form['we']
    print(dataset)
    print(fact)
    print(attribute)
    print(wwll, wwee)

    # the weight of the logical distance
    wl = 0.5
    # the weight of the encoding distance
    we = 0.5

    path = "static/vis/happiness.json"

    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)

    # get logical distance
    lde = logic_dis_extractor(load_dict)

    logic_distence_matrix = lde.logic_detect()

    standard = preprocessing.MinMaxScaler()

    logic_distence_matrix = standard.fit_transform(logic_distence_matrix)

    pca = PCA(n_components=2)

    ld = pca.fit_transform(logic_distence_matrix)

    ld = list(standard.fit_transform(ld))

    # get encoding distance

    # model_path
    model_path = "../gvae/trained/happiness/vae_H256_D256_C888_333_L20_B200.hdf5"
    # rule_path
    rule_path = "../gvae/trainingdata/happiness/rules-cfg.txt"
    # encoding data
    encoding_data = []
    with open('../data/happiness.txt', 'r') as inputs:
        for line in inputs:
            line = line.strip()
            encoding_data.append(line)

    outputspec, z, id = visvae(encoding_data, rule_path, model_path)

    ed = pca.fit_transform(z)

    ed = list(standard.fit_transform(ed))

    out = []
    for i, k in enumerate(load_dict):
        out.append({"id": k, "task": load_dict[k]["task"], "vis": load_dict[k]["vis"], "ex": str(ed[i][0]), "ey": str(ed[i][1]),
                    "lx": str(ld[i][0]), "ly": str(ld[i][1])})
    for i in out:
        print(i)
    return json.dumps({"data": out})


@app.route('/', methods=['GET'])
def application_homepage():
    try:
        return render_template('datafact.html')
    except TemplateNotFound:
        abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True, port=7001)
    # scatter()
