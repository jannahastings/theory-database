

import networkx as nx
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

for theory_num in theories.keys():
    theory = theories[theory_num]
    G=nx.DiGraph()

    for triple in theory.triples:
        G.add_node(triple.const1.name)
        G.add_node(triple.const2.name)
        G.add_edge(triple.const1.name,triple.const2.name,label=triple.relStr)

    pdot = nx.drawing.nx_pydot.to_pydot(G)

    for i, node in enumerate(pdot.get_nodes()):
        node.set_shape('box')
        node.set_fontcolor('black')
        node.set_fillcolor('white')
        node.set_style('rounded, filled')
        node.set_color('black')

    png_path = "static/"+theory_num+".png"
    pdot.write_png(png_path)
