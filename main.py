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

def testCommonIDs():
    test_data = [
            {
            "Theory_ID": "2", 
            "Construct": "Dispositions", 
            "Ontology_ID": "BCIO_05002"
            }, 
            {
            "Theory_ID": "14", 
            "Construct": "Cognitive factors (intrapersonal) / cognitive arm of the model", 
            "Ontology_ID": "BCIO_05002"
            }, 
            {
            "Theory_ID": "20", 
            "Construct": "asdf", 
            "Ontology_ID": "BCIO_05002"
            }, 
            {
            "Theory_ID": "140", 
            "Construct": "cognitive arm of the model", 
            "Ontology_ID": "BCIO_05003"
            }
            
        ]
    
    #new pydot version: 
    callgraph = pydot.Dot(graph_type='digraph',fontname="Verdana")
    #
    # Use pydot.Cluster to render boundary around subgraph
    cluster_foo=pydot.Cluster('foo',label='foo')
    #
    # pydot.Node(name,attrib=''')
    # Assign unique name to each node, but labels can be arbitrary
    cluster_foo.add_node(pydot.Node('foo_method_1',label='method_1'))
    cluster_foo.add_node(pydot.Node('foo_method_2',label='method_2'))
    cluster_foo.add_node(pydot.Node('foo_method_3',label='method_3'))

    #
    # in order to get node in parent graph to point to
    # subgraph, need to use Graph.add_subgraph()
    # calling Subgraph.add_parent() doesn't seem to do anything.
    callgraph.add_subgraph(cluster_foo)

    cluster_bar=pydot.Cluster('bar')
    cluster_bar.add_node(pydot.Node('bar_method_a'))
    cluster_bar.add_node(pydot.Node('bar_method_b'))
    cluster_bar.add_node(pydot.Node('bar_method_c'))
    callgraph.add_subgraph(cluster_bar)

    cluster_baz=pydot.Cluster('baz')
    cluster_baz.add_node(pydot.Node('baz_method_1'))
    cluster_baz.add_node(pydot.Node('baz_method_b'))
    cluster_baz.add_node(pydot.Node('baz_method_3'))
    cluster_baz.add_node(pydot.Node('baz_method_c'))
    callgraph.add_subgraph(cluster_baz)

    # create edge between two main nodes:
    # when creating edges, don't need to
    # predefine the nodes
    #
    callgraph.add_edge(pydot.Edge("main","sub"))

    #
    # create edge to subgraph
    callgraph.add_edge(pydot.Edge("main","bar_method_a"))

    callgraph.add_edge(pydot.Edge("bar_method_a","bar_method_c"))
    callgraph.add_edge(pydot.Edge("bar_method_a","foo_method_2"))

    callgraph.add_edge(pydot.Edge("foo_method_2","baz_method_3"))

    callgraph.add_edge(pydot.Edge("bar_method_b","foo_method_1"))
    callgraph.add_edge(pydot.Edge("bar_method_b","foo_method_2"))
    callgraph.add_edge(pydot.Edge("baz_method_b","baz_method_1"))

    callgraph.add_edge(pydot.Edge("foo_method_2","foo_method_3"))
    callgraph.add_edge(pydot.Edge("bar_method_c","baz_method_c"))
    callgraph.add_edge(pydot.Edge("bar_method_b","baz_method_b"))
    
    #
    # output:
    # write dot file, then render as png
    # callgraph.write_raw('example_cluster2.dot')
    # print("wrote example_cluster2.dot")

    # callgraph.write_png('example_cluster2.png')
    # print("wrote example_cluster2.png")

    # im=Image.open('example_cluster2.png')
    # im.show()
    # G=nx.DiGraph()
    # F = None
    # H=nx.DiGraph()
    # node_list = []
    # edge_list = []
    # id_list = []
    
    # for data in test_data:
    #     theory_num = data["Theory_ID"]
    #     construct_name = data["Construct"]
    #     ontology_id = data["Ontology_ID"]
    #     G.add_node(construct_name)
    #     node_list.append(construct_name)
    #     G.add_edge(construct_name,ontology_id) 
    #     edge_list.append(G)
    #     # if F is not None:
    #     #     L = nx.subgraph(G, F)
    #     #     F = G
    #     # else: 
    #     #     F = G
    #     #     L = nx.subgraph(G, F)


    # # Create a subgraph SG based on a (possibly multigraph) G
    # ################################################################
    # SG = G.__class__()
    # SG.add_nodes_from((n, G.nodes[n]) for n in node_list)
    # if SG.is_multigraph():
    #     SG.add_edges_from((n, nbr, key, d)
    #         for n, nbrs in G.adj.items() if n in node_list
    #         for nbr, keydict in nbrs.items() if nbr in node_list
    #         for key, d in keydict.items())
    # else:
    #     SG.add_edges_from((n, nbr, d)
    #         for n, nbrs in G.adj.items() if n in node_list
    #         for nbr, d in nbrs.items() if nbr in node_list)
    # SG.graph.update(G.graph)
    # ################################################################


    # S = nx.subgraph(G, node_list)
    # print("node_list is: ", node_list)
    # print("edge_list is: ", edge_list)
    # T = G.subgraph(G)
    # print("T is: ", T)
    # # G.subgraph(edge_list)
    # for data in test_data2:
    #     theory_num = data["Theory_ID"]
    #     construct_name = data["Construct"]
    #     ontology_id = data["Ontology_ID"]
    #     H.add_node(construct_name)
    #     node_list.append(construct_name)
    #     H.add_edge(construct_name,ontology_id) 
    #     edge_list.append(G)
    # I = nx.subgraph(H, node_list)

    # F = nx.subgraph(G, H)
    # pdot = nx.drawing.nx_pydot.to_pydot(G)
    # pdot2 = nx.drawing.nx_pydot.to_pydot(T)
    # pdot3 = nx.drawing.nx_pydot.to_pydot(G)
    
    # for i, node in enumerate(pdot.get_nodes()):
    #             node_name = str(node).replace("\"","").replace(";","")
                
    #             node.set_shape('box')
    #             node.set_fontcolor('black')
    #             node.set_fillcolor('white')
    #             node.set_style('rounded, filled')
    #             node.set_color('black')         
    
    # pdot4 = """    digraph {
    # subgraph cluster0 {
    # node [style=filled,color=white];
    # style=filled;
    # color=lightgrey; 
    
    # a0 -> a1 -> a2 -> a3;
    # label = "process #1";
    # }
    # subgraph cluster1 {
    # node [style=filled];
    # b0 -> b1 -> b2 -> b3;
    # label = "process #2";
    # color=blue
    # }
    # start -> a0;
    # start -> b0;
    # a1 -> b3;
    # b2 -> a3;
    # a3 -> a0;
    # a3 -> end;
    # b3 -> end;
    # start [shape=Mdiamond];
    # end [shape=Msquare];
    # }
    # """
    # print(pdot)

    # pdot = nx.drawing.nx_pydot.to_pydot(G)
    # return pdot
    return callgraph


    
    

def get_theory_visualisation_merged(theory_list):
    for theory_num in theories.keys():
        if theory_num in theory_list:
            theory = theories[theory_num]
            print("looking at theory: ", theory_num)
            G=nx.DiGraph()

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
        # result = get_theory_visualisation_merged(theories).to_string()
        result = testCommonIDs()
        session.pop('theories', None)
        return render_template('mergedTheories.html',theories=theories, dotStr=result)
    # return render_template('mergedTheories.html')
       
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=3000, debug=True)
# [END gae_python37_app]
