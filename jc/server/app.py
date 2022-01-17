import pandas as pd
import json
from flask import Flask, jsonify, request, Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound
# Import our Example Applications

# Initialize the app
app = Flask(__name__)
app.jinja_env.auto_reload = True


# Initialize parse variable
@app.route('/init', methods=['POST'])
def init():
    return jsonify({"message":"Datafact Initialized"})

@app.route('/vis', methods=['POST'])
def vis():
    return jsonify({"message":"NL4DV Initialized"})


@app.route('/scatter', methods=['POST'])
def scatter():
    print(request.form)
    dataset = request.form['dataset']
    fact=json.loads(request.form['fact'])
    attribute=json.loads(request.form['attribute'])
    print(fact)
    print(attribute)
    table_path = './assets/data/' + dataset
    table=pd.read_csv(table_path)
    a={"a":123}
    return json.dumps(a)

@app.route('/',methods=['GET'])
def application_homepage():
    try:
        return render_template('datafact.html')
    except TemplateNotFound:
        abort(404)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True, port=7001)
