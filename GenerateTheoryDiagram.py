

import networkx as nx
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import TheoryDatabase
from TheoryDatabase import Theory, theories, Relation

def wrap_if_needed(string_val):
    if ":" in string_val:
        return( f'"{string_val}"')
    return(string_val)

TheoryDatabase.setup()

for theory_num in theories.keys():
    theory = theories[theory_num]
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

    png_path = "static/"+theory_num+".png"
    pdot.write_png(png_path)


