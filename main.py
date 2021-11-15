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
from flask import Flask, render_template, request, url_for, redirect, session
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
import py2cytoscape as cy
from py2cytoscape import util

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

app.secret_key = SECRET_KEY

data_path = 'constructs/ConstructsOntologyMappingTemplate-JH.xlsx'
combined_data_path = os.path.join(os.path.dirname(__file__), data_path)

combined_data = parseConstructs(combined_data_path)


def wrap_if_needed(string_val):
    if ":" in string_val:
        return(f'"{string_val}"')
    return(string_val)

def id_from_construct(const_str):
    ID = ""
    for sub in combined_data:
        if str(sub["Construct"]).strip().upper() == str(const_str).strip().upper():
            ID = sub["Ontology_ID"].strip()    
    return ID

def label_from_construct(const_str):
    label = ""
    for sub in combined_data:
        if str(sub["Construct"]).strip().upper() == str(const_str).strip().upper():
            label = sub["Label"].strip()    
    return label

def theory_from_construct(const_str):
    print(const_str)
    theory_num = ""
    for sub in combined_data:
        if str(sub["Construct"]).strip().upper() == str(const_str).strip().upper():
            theory_num = sub["Theory_ID"]  
    return theory_num

def get_theory_visualisation_merged_boxes(theory_list):
    clustered_list_of_all_values = {}
    all_ids_base = []
    for sub in combined_data:
        if str(sub["Theory_ID"]) in theory_list:
            all_ids_base.append(sub["Ontology_ID"].strip())
    unique_ids_base = list(set(sub for sub in all_ids_base))
    # lots of attributes for pydot here: https://github.com/pydot/pydot/blob/90936e75462c7b0e4bb16d97c1ae7efdf04e895c/src/pydot/core.py
    callgraph = pydot.Dot(graph_type='digraph',
                          fontname="Verdana", fontcolor="green", fontsize="12")
    
    for s in unique_ids_base:
        for d in combined_data:
            if str(d["Theory_ID"]) in theory_list:
                # print("got d")
                if d["Ontology_ID"] == s:
                    fixed_id = d["Ontology_ID"].replace("_", ":")
                    # spacing is important!
                    s_label = "         " + d["Label"] + \
                        " (" + fixed_id + ")" + "         "
                    try:
                        clustered_list_of_all_values[s]["alldata"].append(d)
                    except:
                        clustered_list_of_all_values[s] = {}
                        clustered_list_of_all_values[s]["alldata"] = []
                        clustered_list_of_all_values[s]["alldata"].append(d)
        try:
            clustered_list_of_all_values[s]["cluster"] = pydot.Cluster(
                s.upper(), label=s_label, color='green', fillcolor='green')
        except:
            pass

    complete_theory_node_name_dict = {}
    colour_list = ["orange", "yellow", "cyan", "red", "green", "purple"]  
    k = 0
    theory_name_colour_dict = {}
    for theory_num in theories.keys():
        if theory_num in theory_list:
            theory_name_colour_dict[theories[theory_num].name] = colour_list[k]
            # generate colour according to theory_num here
            node_colour = colour_list[k]
            k = k+1
            complete_theory_node_name_dict[theory_num] = []
            theory = theories[theory_num]

            for triple in theory.triples:
                # add cluster nodes:
                for ID in unique_ids_base:
                    # check in alldata:
                    try:
                        for i in clustered_list_of_all_values[ID]["alldata"]:
                            if triple.const1.name.upper() in i['Construct']:
                                complete_theory_node_name_dict[theory_num].append(
                                    str(theory_num) + wrap_if_needed(triple.const1.name))
                                callgraph.add_node(
                                    pydot.Node(str(theory_num) + wrap_if_needed(triple.const1.name), label = wrap_if_needed(triple.const1.name), color=node_colour))
                                clustered_list_of_all_values[ID]["cluster"].add_node(
                                    pydot.Node(str(theory_num) + wrap_if_needed(triple.const1.name), label = wrap_if_needed(triple.const1.name), color=node_colour))
                        for i in clustered_list_of_all_values[ID]["alldata"]:
                            if triple.const2.name.upper() in i['Construct']:
                                complete_theory_node_name_dict[theory_num].append(
                                    str(theory_num) + wrap_if_needed(triple.const2.name))
                                callgraph.add_node(
                                    pydot.Node(str(theory_num) + wrap_if_needed(triple.const2.name), label = wrap_if_needed(triple.const2.name), color=node_colour))
                                clustered_list_of_all_values[ID]["cluster"].add_node(
                                    pydot.Node(str(theory_num) + wrap_if_needed(triple.const2.name), label = wrap_if_needed(triple.const2.name), color=node_colour))
                    except Exception as error:
                        pass
                        # print(error)
                # add normal graph nodes and edges:
                if triple.reified_rel is None:
                    callgraph.add_node(pydot.Node(str(theory_num) + wrap_if_needed(triple.const1.name), label = wrap_if_needed(triple.const1.name), color=node_colour))
                    callgraph.add_node(pydot.Node(str(theory_num) + wrap_if_needed(triple.const2.name), label = wrap_if_needed(triple.const2.name), color=node_colour))
                    callgraph.add_edge(pydot.Edge(str(theory_num) + wrap_if_needed(triple.const1.name), str(theory_num) + wrap_if_needed(triple.const2.name), label=triple.relStr))
                else:
                    callgraph.add_node(pydot.Node(str(theory_num) + wrap_if_needed(triple.const1.name), label = wrap_if_needed(triple.const1.name), color=node_colour))
                    callgraph.add_node(pydot.Node(str(theory_num) + wrap_if_needed(triple.const2.name), label =  wrap_if_needed(triple.const2.name), color=node_colour))
                    callgraph.add_node(pydot.Node(str(theory_num) + triple.reified_rel.name, label=triple.relStr, color=node_colour))
                    callgraph.add_edge(pydot.Edge(str(theory_num) + wrap_if_needed(triple.const1.name), str(theory_num) + triple.reified_rel.name, label=Relation.getStringForRelType(Relation.THROUGH)))
                    callgraph.add_edge(pydot.Edge(str(theory_num) + triple.reified_rel.name, str(theory_num) + wrap_if_needed(triple.const2.name), label=Relation.getStringForRelType(Relation.TO)))

    # add all subgraphs: 
    for ID in unique_ids_base:
        try:
            multi_theory = False
            all_data_in_cluster = clustered_list_of_all_values[ID]['alldata']            
            thelist = [thelist['Theory_ID'] for thelist in all_data_in_cluster if 'Theory_ID' in thelist]
            theset = set(thelist)
            sub = clustered_list_of_all_values[ID]["cluster"]
            if(len(theset) > 1):
                multi_theory = True
            snodes_list = sub.get_nodes()            
            snode_names_list = []
            for snode in snodes_list:
                snode_names_list.append(snode.get_name().replace("\"", ""))
            snode_names_list = list(set(snode_names_list))

            if len(snode_names_list) > 1:  # only for clusters with more than one node
                #checking theories
                # check for cross-theory boxes here because I can't go back
                some = False  # going to be true if we find name in any theory
                # going to be true if name in more than one theory.
                more = False
                for name in snode_names_list:
                    # per theory check - don't add if nodes not present across theories 
                    for listA in complete_theory_node_name_dict:
                        currentTheory = None
                        oldTheory = None
                        if name in list(set(complete_theory_node_name_dict[listA])):
                            if some == True:  # already found this name before, so:
                                more = True                                
                            # some=True                            
                            for data_containing_theory in clustered_list_of_all_values[ID]['alldata']:
                                currentTheory = data_containing_theory['Theory_ID']
                                if currentTheory != oldTheory and oldTheory != None:
                                    some = True
                                oldTheory = currentTheory                           
        
                if more and multi_theory:
                    callgraph.add_subgraph(sub) 
    
        except KeyError:
            pass
            
    callgraph.set_graph_defaults(compound='True')   
    return callgraph, theory_name_colour_dict
    


@app.route('/')
def display_home():
    num_theories = len(TheoryDatabase.theories)
    num_triples = sum([len(t.triples)
                      for t in TheoryDatabase.theories.values()])
    num_constructs = len(set([c for t in TheoryDatabase.theories.values()
                         for c in t.constructs_by_name.keys()]))
    return render_template('home.html',
                           num_theories=num_theories, num_triples=num_triples, num_constructs=num_constructs, theories=sorted(TheoryDatabase.theories.values(), key=Theory.getNumber))


@app.route("/theory/name=<theory_name>", methods=['GET', 'POST'])
@app.route("/theory/<theory_number>", methods=['GET', 'POST'])
def displayTheory(theory_number=None, theory_name=None):
    if theory_number is not None:
        theory = TheoryDatabase.theories[theory_number]
    if theory_name is not None:
        theory_num = TheoryDatabase.theory_names_to_ids[theory_name]
        theory = TheoryDatabase.theories[theory_num]
    
    #get theory ids and labels here:
    ids_labels = {}        
    theory_constructs = []
    for triple in theory.triples:
        if triple.const1.name != None: 
            line_list = []
            line_list.append(wrap_if_needed(triple.const1.name) or "")
            line_list.append(triple.const1.definition or "")
            line_list.append(id_from_construct(triple.const1.name) or "")
            line_list.append(label_from_construct(triple.const1.name) or "") 
            if (theory_from_construct(triple.const1.name) != None) or (str(theory_from_construct(triple.const1.name) or "") != ""):
                print("theory: " + str(theory_from_construct(triple.const2.name) or ""))
                line_list.append(str(theory_from_construct(triple.const1.name) or ""))
            if line_list not in theory_constructs:
                theory_constructs.append(line_list)
            
        if triple.const2.name != None: 
            line_list = []
            line_list.append(wrap_if_needed(triple.const2.name) or "")
            line_list.append(triple.const2.definition or "")
            line_list.append(id_from_construct(triple.const2.name) or "")
            line_list.append(label_from_construct(triple.const2.name) or "")
            if (theory_from_construct(triple.const2.name) != None) or (str(theory_from_construct(triple.const1.name) or "") != ""):
                print("theory: " + str(theory_from_construct(triple.const2.name) or ""))
                line_list.append(str(theory_from_construct(triple.const2.name) or ""))
            if line_list not in theory_constructs:
                theory_constructs.append(line_list)
        # if triple.reified_rel != None: # is this relevant? 
        #     line_list = []
        #     line_list.append(wrap_if_needed(triple.reified_rel.name) or "")
        #     line_list.append(triple.relStr or "") #todo: not sure about this one..
        #     line_list.append(id_from_construct(triple.reified_rel.name) or "")
        #     line_list.append(label_from_construct(triple.reified_rel.name) or "")
        #     if line_list not in theory_constructs:
        #         theory_constructs.append(line_list)
            
    # print(theory_constructs)
        

    net_image_file = url_for('static', filename=theory.number+".png")
    wc_image_file = url_for('static', filename=theory.number+"-wc.png")
    
    return render_template('theory.html', theory=theory, net_image_file=net_image_file, wc_image_file=wc_image_file, theory_constructs=theory_constructs)


@app.route("/searchConstruct", methods=['GET', 'POST'])
@app.route("/searchConstruct/<string>", methods=['GET', 'POST'])
def searchConstructResult(string=None):
    if request.method == 'POST':
        searchstr = request.form['searchconstruct']
        index_dir = "static/index/"
        results = TheoryDatabase.searchForConstruct(searchstr, index_dir)
        len_results = len(results)
        return render_template('searchConstruct.html', string=searchstr, results=results, len_results=len_results)
    # Display the search results for a given search string (theories)
    else:
        results = TheoryDatabase.searchForConstruct(string, index_dir)
        len_results = len(results)
        return render_template('searchConstruct.html', string=string, results=results, len_results=len_results)


@app.route("/searchTheory", methods=['GET', 'POST'])
@app.route("/searchTheory/<string>", methods=['GET', 'POST'])
def searchTheoryResult(string=None):
    if request.method == 'POST':
        searchtheory = request.form['searchtheory']
        index_dir = "static/index/"
        results = TheoryDatabase.searchForTheory(searchtheory, index_dir)
        len_results = len(results)
        return render_template('searchTheory.html', string=searchtheory, results=results, len_results=len_results)
    # Display the search results for a given search string (theories)
    else:
        results = TheoryDatabase.searchForTheory(string, index_dir)
        len_results = len(results)
        return render_template('searchTheory.html', string=string, results=results, len_results=len_results)


@app.route("/searchRelation", methods=['GET', 'POST'])
@app.route("/searchRelation/<string>", methods=['GET', 'POST'])
def searchRelationResult(string=None):
    if request.method == 'POST':
        searchstr = request.form['searchrelation']
        index_dir = "static/index/"
        results = TheoryDatabase.searchForRelation(searchstr, index_dir)
        len_results = len(results)
        return render_template('searchRelation.html', string=searchstr, results=results, len_results=len_results)
    # Display the search results for a given search string (theories)
    else:
        results = TheoryDatabase.searchForRelation(string, index_dir)
        len_results = len(results)
        return render_template('searchRelation.html', string=string, results=results, len_results=len_results)


@app.route("/show_view_annotations", methods=['GET', 'POST'])
def show_view_annotations():
    if request.method == 'POST':
        theories = request.form.get('theories')
        session['theories'] = theories
        return redirect('/viewAnnotations')


@app.route("/show_theory_consistency", methods=['GET', 'POST'])
def show_theory_consistency():
    if request.method == 'POST':
        theories = request.form.get('theories')
        session['theories'] = theories
        return redirect('/theoryConsistency')
       


@app.route("/show_merged_theories", methods=['GET', 'POST'])
def show_merged_theories():
    if request.method == 'POST':
        theories = request.form.get('theories')
        session['theories'] = theories
        return redirect('/mergedTheories')


@app.route("/viewAnnotations")
def viewAnnotations():
    if 'theories' in session:
        theories = session['theories']
        theories = theories.replace("\"", "")
        theories = theories.replace("[", "").replace("]", "")
        theory_list = theories.split(",")
        result, theory_name_colour_dict = get_theory_visualisation_merged_boxes(
            theory_list)
        g = nx.drawing.nx_pydot.from_pydot(result)
        cyjs = util.from_networkx(g)
        nodes = cyjs['elements']
        session.pop('theories', None)
        colourKey = ""
        for item in theory_name_colour_dict:
            colourKey += item + ", "
        colourKey = colourKey[:-2]  # remove last ,
        return render_template('viewAnnotations.html', theories=theories, cyjs=nodes, colourKey=colourKey)
        #NetworkX: 
        # return render_template('mergedTheoriesNetworkX.html', theories=theories, dotStr=result, colourKey=colourKey)

@app.route("/theoryConsistency")
def theoryConsistency():
    if 'theories' in session:
        theories = session['theories']
        print("GOT THEORIES: ", theories)
        session.pop('theories', None)
        return render_template('theoryConsistency.html', theories=theories)
    # return render_template('theoryConsistency.html')


@app.route("/mergedTheories")
def mergedTheories():
    if 'theories' in session:
        theories = session['theories']
        # print("GOT THEORIES: ", theories)
        theories = theories.replace("\"", "")
        theories = theories.replace("[", "").replace("]", "")
        theory_list = theories.split(",")
        result, theory_name_colour_dict = get_theory_visualisation_merged_boxes(
            theory_list)

        slist = result.get_subgraph_list()        

        session.pop('theories', None)
        colourKey = ""
        for item in theory_name_colour_dict:
            colourKey += item + ", "
        colourKey = colourKey[:-2]  # remove last ,
        g = nx.drawing.nx_pydot.from_pydot(result)
        cyjs = util.from_networkx(g)
        nodes = cyjs['elements']
        for n in nodes['nodes']:
            # check for subgraph matches:
            for sg in slist: #slist is list of subgraphs
                for sn in sg.get_nodes():
                    if(n['data']['id'].replace(" ", "").replace("\"", "").lower() == sn.get_name().replace(" ", "").replace("\"", "").lower()): # is this not finding spaces?
                        parentLabel = sg.get_label()
                        nodes['nodes'].append({'data': {'color': 'white', 'id': parentLabel, 'name': parentLabel, 'label': parentLabel}})
                        #only if n['data'] doesn't contain 'parent'
                        if 'parent' not in n['data']:
                            n['data']['parent'] = []
                            n['data']['parent'].append( parentLabel )
                        else:
                            n['data']['parent'].append( parentLabel )
        #cytoscape:
        return render_template('mergedTheories.html', theories=theories, cyjs=nodes, colourKey=colourKey)

        #NetworkX: 
        # return render_template('mergedTheoriesNetworkX.html', theories=theories, dotStr=result, colourKey=colourKey)
    # return render_template('mergedTheories.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=3000, debug=True)
# [END gae_python37_app]
