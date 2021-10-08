# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
import json
from config import *
from flask import Flask, render_template,request,url_for, redirect, session
import TheoryDatabase
from TheoryDatabase import Theory, theories, Relation

import networkx as nx
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt



class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self._activate_background_job()

    def _activate_background_job(self):
        #index_dir = url_for('static', filename="index_dir")

        TheoryDatabase.setup()


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = FlaskApp(__name__)

app.secret_key=SECRET_KEY


def wrap_if_needed(string_val):
    if ":" in string_val:
        return( f'"{string_val}"')
    return(string_val)

def get_theory_visualisation_merged(theory_list):
    for theory_num in theories.keys():
        if theory_num in theory_list:
            theory = theories[theory_num]
            print("looking at theory: ", theory_num)
            G=nx.DiGraph()

            for triple in theory.triples:
                if triple.reified_rel is None:
                    G.add_node(wrap_if_needed(triple.const1.name))
                    G.add_node(wrap_if_needed(triple.const2.name))
                    G.add_edge(wrap_if_needed(triple.const1.name),wrap_if_needed(triple.const2.name),label=triple.relStr)
                else:
                    G.add_node(wrap_if_needed(triple.const1.name))
                    G.add_node(wrap_if_needed(triple.const2.name))
                    G.add_node(triple.reified_rel.name,label=triple.relStr)
                    G.add_edge(wrap_if_needed(triple.const1.name),triple.reified_rel.name,label=Relation.getStringForRelType(Relation.THROUGH))
                    G.add_edge(triple.reified_rel.name,wrap_if_needed(triple.const2.name),label=Relation.getStringForRelType(Relation.TO))

            pdot = nx.drawing.nx_pydot.to_pydot(G)

            for i, node in enumerate(pdot.get_nodes()):
                node_name = str(node).replace("\"","").replace(";","")
                if node_name in theory.constructs_by_name.keys():
                    node.set_shape('box')
                    node.set_fontcolor('black')
                    node.set_fillcolor('white')
                    node.set_style('rounded, filled')
                    node.set_color('black')
                else:
                    node.set_shape('ellipse')
                    node.set_fontcolor('black')
                    node.set_fontname('times italic')
                    node.set_fillcolor('white')
                    node.set_style('rounded, filled')
                    node.set_color('grey')

            #testing only:
            # png_path = "test/"+theory_num+".png"
            # pdot.write_png(png_path)
    return pdot

@app.route('/')
def display_home():
    num_theories = len(TheoryDatabase.theories)
    num_triples = sum([len(t.triples) for t in TheoryDatabase.theories.values()])
    num_constructs = len(set([c for t in TheoryDatabase.theories.values() for c in t.constructs_by_name.keys()]))
    return render_template('home.html',
        num_theories=num_theories,num_triples=num_triples, num_constructs=num_constructs, theories = sorted(TheoryDatabase.theories.values(),key=Theory.getNumber))


@app.route("/theory/name=<theory_name>",methods=['GET', 'POST'])
@app.route("/theory/<theory_number>",methods=['GET', 'POST'])
def displayTheory(theory_number=None,theory_name=None):
    if theory_number is not None:
        theory = TheoryDatabase.theories[theory_number]
    if theory_name is not None:
        theory_num = TheoryDatabase.theory_names_to_ids[theory_name]
        theory = TheoryDatabase.theories[theory_num]

    #print('GOT THEORY: ',theory.name,theory.number)
    net_image_file = url_for('static', filename=theory.number+".png")
    wc_image_file = url_for('static', filename=theory.number+"-wc.png")
    return render_template('theory.html',theory=theory,net_image_file=net_image_file,wc_image_file=wc_image_file)


@app.route("/searchConstruct",methods=['GET', 'POST'])
@app.route("/searchConstruct/<string>",methods=['GET', 'POST'])
def searchConstructResult(string=None):
    if request.method == 'POST':
        searchstr = request.form['searchconstruct']
        #print("GOT SEARCH STRING: ",searchstr)
        index_dir = "static/index/"
        results = TheoryDatabase.searchForConstruct(searchstr,index_dir)
        len_results = len(results)
        return render_template('searchConstruct.html',string=searchstr,results=results,len_results=len_results)
    # Display the search results for a given search string (theories)
    else:
        results = TheoryDatabase.searchForConstruct(string,index_dir)
        len_results = len(results)
        return render_template('searchConstruct.html',string=string,results=results,len_results=len_results)

@app.route("/searchTheory",methods=['GET', 'POST'])
@app.route("/searchTheory/<string>",methods=['GET', 'POST'])
def searchTheoryResult(string=None):
    if request.method == 'POST':
        searchtheory = request.form['searchtheory']
        index_dir = "static/index/"
        results = TheoryDatabase.searchForTheory(searchtheory,index_dir)
        len_results = len(results)
        return render_template('searchTheory.html',string=searchtheory,results=results,len_results=len_results)
    # Display the search results for a given search string (theories)
    else:
        results = TheoryDatabase.searchForTheory(string,index_dir)
        len_results = len(results)
        return render_template('searchTheory.html',string=string,results=results,len_results=len_results)


@app.route("/searchRelation",methods=['GET', 'POST'])
@app.route("/searchRelation/<string>",methods=['GET', 'POST'])
def searchRelationResult(string=None):
    if request.method == 'POST':
        searchstr = request.form['searchrelation']
        #print("GOT SEARCH STRING: ",searchstr)
        index_dir = "static/index/"
        results = TheoryDatabase.searchForRelation(searchstr,index_dir)
        len_results = len(results)
        return render_template('searchRelation.html',string=searchstr,results=results,len_results=len_results)
    # Display the search results for a given search string (theories)
    else:
        results = TheoryDatabase.searchForRelation(string,index_dir)
        len_results = len(results)
        return render_template('searchRelation.html',string=string,results=results,len_results=len_results)

@app.route("/show_theory_consistency", methods=['GET', 'POST'])
def show_theory_consistency():
    if request.method == 'POST':
        theories = request.form.get('theories')
        # get_theory_visualisation(theories)
        # print("GOT THEORIES for consistency: ",theories)
        session['theories'] = theories
        return redirect('/theoryConsistency')
        # return("success")

@app.route("/show_merged_theories", methods=['GET', 'POST'])
def show_merged_theories():
    if request.method == 'POST':
        theories = request.form.get('theories')        
        # print("GOT THEORIES for merged: ",theories)
        session['theories'] = theories
        return redirect('/mergedTheories')

@app.route("/theoryConsistency")
def theoryConsistency():
    if 'theories' in session:
        theories = session['theories']
        print("GOT THEORIES: ",theories)
        session.pop('theories', None)
        return render_template('theoryConsistency.html',theories=theories)
    # return render_template('theoryConsistency.html')
        
@app.route("/mergedTheories")
def mergedTheories():
    if 'theories' in session:
        theories = session['theories']
        print("GOT THEORIES: ",theories)
        result = get_theory_visualisation_merged(theories).to_string()
        session.pop('theories', None)
        return render_template('mergedTheories.html',theories=theories, dotStr=result)
    # return render_template('mergedTheories.html')
       
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=3000, debug=True)
# [END gae_python37_app]
