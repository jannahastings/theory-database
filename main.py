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
import pydot 
from PIL import Image
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pprint as pp
from itertools import chain

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

class add_subnodes():
    def __init__(self, all_data):
        self.all_data = all_data
        self.all_ids = [ sub['Ontology_ID'] for sub in all_data ]
        self.unique_ids = list(set(sub for sub in self.all_ids))        

    def get_unique_IDs(self):
        return self.unique_ids

    def build(self):
        self.cluster_list = []
        self.cluster_output = []
        num = 0
        
        for s in self.unique_ids:
            self.cluster_list.append(pydot.Cluster(s,label=s))
            
            for data in self.all_data:
                theory_num = data["Theory_ID"]
                construct_name = data["Construct"]
                ontology_id = data["Ontology_ID"]
                if(ontology_id == s):
                    self.cluster_list[num].add_node(pydot.Node(theory_num, label=construct_name))
            #todo: below is a hack but example of how to use invisible edges for layout..
            if(num > 0):
                self.cluster_list[num].add_edge(pydot.Edge(self.all_data[0]["Theory_ID"], self.all_data[num-1]["Theory_ID"], color="white"))
            self.cluster_output.append(self.cluster_list[num])
            num = num+1
        return self.cluster_output
            
        


def testCommonIDs():
    test_data = [
            {
            "Theory_ID": "1", 
            "Construct": "a", 
            "Ontology_ID": "BCIO_1"
            }, 
            {
            "Theory_ID": "2", 
            "Construct": "b", 
            "Ontology_ID": "BCIO_1"
            }, 
            {
            "Theory_ID": "3", 
            "Construct": "c", 
            "Ontology_ID": "BCIO_1"
            }, 
            {
            "Theory_ID": "4", 
            "Construct": "d", 
            "Ontology_ID": "BCIO_2"
            }, 
            {
            "Theory_ID": "5", 
            "Construct": "e", 
            "Ontology_ID": "BCIO_2"
            }, 
            {
            "Theory_ID": "6", 
            "Construct": "f", 
            "Ontology_ID": "BCIO_3"
            }, 
            {
            "Theory_ID": "7", 
            "Construct": "g", 
            "Ontology_ID": "BCIO_3"
            }, 
            {
            "Theory_ID": "8", 
            "Construct": "h", 
            "Ontology_ID": "BCIO_3"
            }, 
            {
            "Theory_ID": "9", 
            "Construct": "i", 
            "Ontology_ID": "BCIO_4"
            }, 
            {
            "Theory_ID": "10", 
            "Construct": "j", 
            "Ontology_ID": "BCIO_4"
            }, 
            {
            "Theory_ID": "11", 
            "Construct": "k", 
            "Ontology_ID": "BCIO_4"
            }, 
            {
            "Theory_ID": "12", 
            "Construct": "l", 
            "Ontology_ID": "BCIO_5"
            }, 
            {
            "Theory_ID": "13", 
            "Construct": "m", 
            "Ontology_ID": "BCIO_7"
            }, 
            {
            "Theory_ID": "14", 
            "Construct": "n", 
            "Ontology_ID": "BCIO_7"
            }, 
            {
            "Theory_ID": "15", 
            "Construct": "o", 
            "Ontology_ID": "BCIO_6"
            }, 
            {
            "Theory_ID": "16", 
            "Construct": "p", 
            "Ontology_ID": "BCIO_6"
            }, 
            

            
        ]
   
    #new pydot version: 
    callgraph = pydot.Dot(graph_type='digraph',fontname="Verdana", compound='true')
    sn = add_subnodes(test_data) #add_subnodes class creates boxes around same 'Ontology_ID'
    sn_list = sn.build() #build returns the dot graph
    sn_unique = sn.get_unique_IDs() #not important, just for testing
    print("got unique ID's: ", sn_unique)
    # print(a)
    for sub in sn_list:
        callgraph.add_subgraph(sub)
        print(sub)

    # callgraph.add_subgraph(s)
    # Use pydot.Cluster to render boundary around subgraph
    #todo: build these from unique Ontology_ID test_data values - https://www.geeksforgeeks.org/python-get-unique-values-from-list-of-dictionary/
    # cluster_foo=pydot.Cluster('foo',label=test_data[0]['Ontology_ID'])

    #
    # pydot.Node(name,attrib=''')
    # Assign unique name to each node, but labels can be arbitrary
    # cluster_foo.add_node(pydot.Node('foo_method_1',label=test_data[0]['Construct']))
    # cluster_foo.add_node(pydot.Node('foo_method_2',label=test_data[1]['Construct']))
    # cluster_foo.add_node(pydot.Node('foo_method_3',label=test_data[2]['Construct']))
    
    #todo: filter test_data by combining compatible ontology_id into subgraph on unique ID
    # for data in test_data:
    #     theory_num = data["Theory_ID"]
    #     construct_name = data["Construct"]
    #     ontology_id = data["Ontology_ID"]
    #     cluster_foo.add_node(pydot.Node(theory_num, label=construct_name))

    #
    # in order to get node in parent graph to point to
    # subgraph, need to use Graph.add_subgraph()
    # calling Subgraph.add_parent() doesn't seem to do anything.
    # callgraph.add_subgraph(cluster_foo)

    # cluster_bar=pydot.Cluster('bar')
    # cluster_bar.add_node(pydot.Node('bar_method_a'))
    # cluster_bar.add_node(pydot.Node('bar_method_b'))
    # cluster_bar.add_node(pydot.Node('bar_method_c'))
    # cluster_bar.add_node(pydot.Node('bar_method_d'))
    # callgraph.add_subgraph(cluster_bar)

    # cluster_baz=pydot.Cluster('baz')
    # cluster_baz.add_node(pydot.Node('baz_method_1'))
    # cluster_baz.add_node(pydot.Node('baz_method_b'))
    # cluster_baz.add_node(pydot.Node('baz_method_3'))
    # cluster_baz.add_node(pydot.Node('baz_method_c'))
    # callgraph.add_subgraph(cluster_baz)

    # create edge between two main nodes:
    # when creating edges, don't need to
    # predefine the nodes
    #
    # callgraph.add_edge(pydot.Edge("main","sub"))

    # #
    # # create edge to subgraph
    # callgraph.add_edge(pydot.Edge("main","bar_method_a"))

    # callgraph.add_edge(pydot.Edge("bar_method_a","bar_method_c"))
    # callgraph.add_edge(pydot.Edge("bar_method_a","foo_method_2"))

    # callgraph.add_edge(pydot.Edge("foo_method_2","baz_method_3"))

    # callgraph.add_edge(pydot.Edge("bar_method_b","foo_method_1"))
    # callgraph.add_edge(pydot.Edge("bar_method_b","foo_method_2"))
    # callgraph.add_edge(pydot.Edge("baz_method_b","baz_method_1"))

    # callgraph.add_edge(pydot.Edge("foo_method_2","foo_method_3"))
    # callgraph.add_edge(pydot.Edge("bar_method_c","baz_method_c"))
    # callgraph.add_edge(pydot.Edge("bar_method_b","baz_method_b"))
    
    #layout: https://www.graphviz.org/pdf/dotguide.pdf
    # callgraph.set_graph_defaults(rankdir='LR', center='True')
    callgraph.set_graph_defaults(compound='True')
    # callgraph.set_graph_defaults(ratio="fill",ranksep='equally', compound='true', rankdir='LR', center='True')
    # my_networkx_graph = nx.drawing.nx_pydot.from_pydot(callgraph)

    return callgraph


def get_theory_visualisation_merged_boxes(theory_list):
    # print("theory_list is: ", theory_list)
    test_data = [
            {
            "Theory_ID": "2", 
            "Construct": "Dispositions", 
            "Label":"personal disposition",
            "Ontology_ID": "BCIO_050002"
            }, 
            {
            "Theory_ID": "14", 
            "Construct": "Cognitive factors (intrapersonal) / cognitive arm of the model", 
            "Label":"personal disposition",
            "Ontology_ID": "BCIO_050002"
            },
            {
            "Theory_ID": "14", 
            "Construct": "Attitudes", 
            "Label":"test1",
            "Ontology_ID": "BCIO_0511111"
            }, 
            {
            "Theory_ID": "14", 
            "Construct": "Beliefs and knowledge", 
            "Label":"test1",
            "Ontology_ID": "BCIO_0511111"
            },
            {
            "Theory_ID": "2", 
            "Construct": "Internal incentive", 
            "Label":"test1",
            "Ontology_ID": "BCIO_0511111"
            }           
        ]
    list_of_all_values = [value for elem in test_data for value in elem.values()]
    clustered_list_of_all_values = {}
    # print("got list_of_all_values", list_of_all_values)
    all_ids = [ (sub['Label'] + " (" + sub['Ontology_ID'] + ")") for sub in test_data ]
    unique_ids = list(set(sub for sub in all_ids)) 

    all_ids_base = [ (sub['Ontology_ID']) for sub in test_data ]
    unique_ids_base = list(set(sub for sub in all_ids_base)) 

    cluster_list = []
    num = 0 #for multiple
    callgraph = pydot.Dot(graph_type='digraph',fontname="Verdana")
    
    for s in unique_ids_base:
        for d in test_data:
            print("checking: ", d["Construct"])
            if d["Ontology_ID"] == s:
                s_label = d["Label"] + " (" + d["Ontology_ID"] + ")"
                try:
                    clustered_list_of_all_values[s]["alldata"].append(d)
                except:
                    clustered_list_of_all_values[s] = {}
                    clustered_list_of_all_values[s]["alldata"] = []
                    clustered_list_of_all_values[s]["alldata"].append(d)
        clustered_list_of_all_values[s]["cluster"] = pydot.Cluster(s,label=s_label, color='red')
                # clustered_list_of_all_values

        # append dict to clustered_list_of_all_values
        # num?, s, Label, Constructs, Theories ...?
        cluster_list.append(pydot.Cluster(s,label=s, color='red'))
    total_num = len(unique_ids)
    # print("total_num = ", total_num)

    for theory_num in theories.keys():        
        if theory_num in theory_list: 
            theory = theories[theory_num]
            # print("looking at theory: ", theory_num)
            
            for triple in theory.triples: 

                #clusters:
                for ID in unique_ids_base:  
                    #check in alldata: 
                    for i in clustered_list_of_all_values[ID]["alldata"]:
                        if triple.const1.name in i['Construct']:
                            clustered_list_of_all_values[ID]["cluster"].add_node(pydot.Node(wrap_if_needed(triple.const1.name)))
                    for i in clustered_list_of_all_values[ID]["alldata"]:
                        if triple.const2.name in i['Construct']:
                            clustered_list_of_all_values[ID]["cluster"].add_node(pydot.Node(wrap_if_needed(triple.const2.name)))

                    # print(clustered_list_of_all_values[ID]["alldata"][0]['Ontology_ID'])
                    # print("ID CLUSTER: ", clustered_list_of_all_values[ID]["alldata"])                
                    # if triple.const1.name in clustered_list_of_all_values[ID]["alldata"][0]['Construct']:

                    #     print("CLUSTERED_LIST_OF_ALL_VALUES")
                    #     print(clustered_list_of_all_values[ID]["alldata"])

                # clusters: 
                # while num < total_num:
                #     print("NUM: ", num)
                #     num = num + 1
                # if triple.const1.name in list_of_all_values: 
                #     cluster_list[num-1].add_node(pydot.Node(wrap_if_needed(triple.const1.name)))
                #     # print("adding to cluster_list: ", triple.const1.name)
                # elif triple.const2.name in list_of_all_values:
                #     cluster_list[num-1].add_node(pydot.Node(wrap_if_needed(triple.const2.name)))
                    # print("adding to cluster_list: ", triple.const2.name)  

                # # clusters: 
                # while num < total_num:
                #     print("NUM: ", num)
                #     num = num + 1
                # if triple.const1.name in list_of_all_values: 
                #     cluster_list[num-1].add_node(pydot.Node(wrap_if_needed(triple.const1.name)))
                #     # print("adding to cluster_list: ", triple.const1.name)
                # elif triple.const2.name in list_of_all_values:
                #     cluster_list[num-1].add_node(pydot.Node(wrap_if_needed(triple.const2.name)))
                #     # print("adding to cluster_list: ", triple.const2.name)  
                    
                # normal graph nodes and edges:     
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
    
    # new test add all subgraphs:
    for ID in unique_ids_base:  
        sub = clustered_list_of_all_values[ID]["cluster"]
        callgraph.add_subgraph(sub)
    
    
    #test add to cluster_list
    # cluster_list.append(pydot.Cluster("test",label="test", color='blue'))
    # cluster_list[1].add_node(pydot.Node(wrap_if_needed("Attitudes")))           
    
    # for sub in cluster_list: #testing only, adding all subgraphs - do we need check for none?
    #     callgraph.add_subgraph(sub)
    callgraph.set_graph_defaults(compound='True')
    # for i, g in enumerate(callgraph.get_subgraphs()): 
    #     print(i, g)   
        
    return callgraph    
    

def get_theory_visualisation_merged(theory_list):
    G=nx.DiGraph()
    for theory_num in theories.keys():
        if theory_num in theory_list:
            theory = theories[theory_num]
            print("looking at theory: ", theory_num)
            # G=nx.DiGraph()

            for triple in theory.triples:
                # pp.pprint(triple.const1.name)
                # pp.pprint(triple.const2.name)
                # # pp.pprint(triple.const3.name)
                # pp.pprint(triple.relStr)
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
    # print(pdot)
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
        theories = theories.replace("\"", "")
        theories = theories.replace("[", "").replace("]", "")
        theory_list = theories.split(",")
        result = get_theory_visualisation_merged_boxes(theory_list)
        # result = get_theory_visualisation_merged(theories).to_string()
        # result = testCommonIDs()
        session.pop('theories', None)
        return render_template('mergedTheories.html',theories=theories, dotStr=result)
    # return render_template('mergedTheories.html')
       
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=3000, debug=True)
# [END gae_python37_app]
