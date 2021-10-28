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
from ast import parse
import json
from config import *
from flask import Flask, render_template,request,url_for, redirect, session
import TheoryDatabase
from TheoryDatabase import Theory, theories, Relation

import networkx as nx
import pydot 
from PIL import Image
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pprint as pp
from itertools import chain
import os


from constructs.parse_constructs import parseConstructs
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

data_path = 'constructs/ConstructsOntologyMappingTemplate-JH.xlsx'
combined_data_path = os.path.join(os.path.dirname(__file__), data_path)

combined_data = parseConstructs(combined_data_path)
# combined_data = parseConstructs("/home/tom/Documents/PROGRAMMING/Python/theory-database/constructs/ConstructsOntologyMappingTemplate-JH.xlsx")

def wrap_if_needed(string_val):
    if ":" in string_val:
        return( f'"{string_val}"')
    return(string_val)

def get_theory_visualisation_merged_boxes(theory_list):
    # print("theory_list is: ", theory_list)
    # print("using combined_data: ", combined_data)
    clustered_list_of_all_values = {}
    all_ids_base = []
    for sub in combined_data:
        # print(sub["Theory_ID"])
        if str(sub["Theory_ID"]) in theory_list: 
            # print("got sub: ", sub["Theory_ID"])
            all_ids_base.append(sub["Ontology_ID"].strip()) 
    # print("all_ids_base: ", all_ids_base) # working
    unique_ids_base = list(set(sub for sub in all_ids_base)) 
    # print("unique ids base: ", unique_ids_base) # working
    # lots of attributes for pydot here: https://github.com/pydot/pydot/blob/90936e75462c7b0e4bb16d97c1ae7efdf04e895c/src/pydot/core.py
    callgraph = pydot.Dot(graph_type='digraph',fontname="Verdana", fontcolor="green", fontsize="12")
        
    for s in unique_ids_base:
        for d in combined_data:
            # print("checking: ", d["Construct"])
            # print(str(d["Theory_ID"]), " is it in ", theory_list) #theory_list is strings only
            if str(d["Theory_ID"]) in theory_list:
                # print("got d")
                if d["Ontology_ID"] == s:
                    fixed_id = d["Ontology_ID"].replace("_",":")
                    # print("got a match", s)
                    s_label = "         " + d["Label"] + " (" + fixed_id + ")" + "         " #spacing is important!
                    try:
                        clustered_list_of_all_values[s]["alldata"].append(d)
                    except:
                        clustered_list_of_all_values[s] = {}
                        clustered_list_of_all_values[s]["alldata"] = []
                        clustered_list_of_all_values[s]["alldata"].append(d)
        try: 
            clustered_list_of_all_values[s]["cluster"] = pydot.Cluster(s,label=s_label, color='green', fillcolor='green')
        except: 
            pass
    # print("clustered list: ", clustered_list_of_all_values)
    complete_theory_node_name_dict = {}
    for theory_num in theories.keys():        
        if theory_num in theory_list: 
            complete_theory_node_name_dict[theory_num] = []
            theory = theories[theory_num]
            # print("looking at theory: ", theory_num)
            
            for triple in theory.triples: 
                #add cluster nodes:
                for ID in unique_ids_base:  
                    #check in alldata: 
                    try:
                        for i in clustered_list_of_all_values[ID]["alldata"]:
                            # print("checking i")
                            if triple.const1.name in i['Construct']:
                                # print("adding to cluster", triple.const1.name)
                                complete_theory_node_name_dict[theory_num].append(triple.const1.name)
                                clustered_list_of_all_values[ID]["cluster"].add_node(pydot.Node(wrap_if_needed(triple.const1.name)))
                        for i in clustered_list_of_all_values[ID]["alldata"]:
                            if triple.const2.name in i['Construct']:
                                # print("adding to cluster", triple.const2.name)
                                complete_theory_node_name_dict[theory_num].append(triple.const2.name)
                                clustered_list_of_all_values[ID]["cluster"].add_node(pydot.Node(wrap_if_needed(triple.const2.name)))
                    except Exception as error:
                        pass
                        # print(error)
                # add normal graph nodes and edges:     
                if triple.reified_rel is None:
                    callgraph.add_node(pydot.Node(wrap_if_needed(triple.const1.name)))
                    callgraph.add_node(pydot.Node(wrap_if_needed(triple.const2.name)))
                    callgraph.add_edge(pydot.Edge(wrap_if_needed(triple.const1.name),wrap_if_needed(triple.const2.name),label=triple.relStr))
                else:
                    callgraph.add_node(pydot.Node(wrap_if_needed(triple.const1.name)))
                    callgraph.add_node(pydot.Node(wrap_if_needed(triple.const2.name)))
                    callgraph.add_node(pydot.Node(triple.reified_rel.name,label=triple.relStr))
                    callgraph.add_edge(pydot.Edge(wrap_if_needed(triple.const1.name),triple.reified_rel.name,label=Relation.getStringForRelType(Relation.THROUGH)))
                    callgraph.add_edge(pydot.Edge(triple.reified_rel.name,wrap_if_needed(triple.const2.name),label=Relation.getStringForRelType(Relation.TO)))
    
    # add all subgraphs:
    for ID in unique_ids_base:  
        try: 
            sub = clustered_list_of_all_values[ID]["cluster"]
            # if ID == "BCIO_006059":
            #     snodes_list = sub.get_nodes()
            #     snode_names_list = []
            #     for snode in snodes_list:
            #         snode_names_list.append(snode.get_name())
            #     for node in list(set(snode_names_list)):
            #         print("WHY? ",snode.get_name())
            snodes_list = sub.get_nodes()
            snode_names_list = []
            for snode in snodes_list:
                snode_names_list.append(snode.get_name())
            snode_names_list = list(set(snode_names_list)) 
            # for node in snode_names_list:
                # print("got node: ", node, ", ", len(snode_names_list))
            # for node in list(set(snode_names_list)):
            #     print(ID, " : ", node, ", ", len(list(set(snode_names_list))))
                
                
                
            if len(snode_names_list) > 1: #only for clusters with more than one node
                #check for cross-theory boxes here because I can't go back 
                # print("compare with: ", complete_theory_node_name_dict)
                some = False # going to be true if we find name in any theory
                more = False # going to be true if name in more than one theory. 
                for name in snode_names_list:
                    for listA in complete_theory_node_name_dict: # per theory check - don't add if nodes not present across theories
                        if name in complete_theory_node_name_dict[listA]:
                            if some == True: # already found this name before, so:
                                more = True
                            some = True
                            # print("got a match: ", name)
                print("got length: ", len(snode_names_list))
                if more:
                    callgraph.add_subgraph(sub)
                # if ID == "BCIO_006059": #todo: test case with two nodes but only one showing up
                #     print("got here", snode_names_list)
            # callgraph.add_subgraph(sub)
            # print("added subgraph!", ID)
        except KeyError:
            pass 
            # print(ID)

    
    callgraph.set_graph_defaults(compound='True')
    # print(callgraph)
    return callgraph    
    

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
        theories = theories.replace("\"", "")
        theories = theories.replace("[", "").replace("]", "")
        theory_list = theories.split(",")
        result = get_theory_visualisation_merged_boxes(theory_list)
        # print("result is: ", result)
        session.pop('theories', None)
        return render_template('mergedTheories.html',theories=theories, dotStr=result)
    # return render_template('mergedTheories.html')
       
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=3000, debug=True)
# [END gae_python37_app]
