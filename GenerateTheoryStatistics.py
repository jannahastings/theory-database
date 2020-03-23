
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
import statistics
import networkx as nx

theory_names = sorted(theories.keys())


# Table of constructs vs. number of theories that those constructs appear (are mentioned) in

construct_names = set([c.name.lower() for theory in theories.values() for c in theory.constructs.values() if len(c.name)>4])

construct_counts = np.zeros((len(construct_names)))
for i,c in zip(range(len(construct_names)),construct_names):
    n=0
    for j,theory in zip(range(len(theory_names)),[theories[t] for t in theory_names]):
        theory_desc = " ".join([c.name.lower() for c in theory.constructs.values()])
        if c.lower() in theory_desc:
            n=n+1
    construct_counts[i]=n

Names = [x for _,x in sorted(zip(construct_counts,construct_names),reverse=True)]
Counts = [x for x,_ in sorted(zip(construct_counts,construct_names),reverse=True)]

fig,ax = plt.subplots()
ax.bar(Names[0:25],Counts[0:25])
plt.xticks(rotation=90)
fig.subplots_adjust(bottom=0.3)
plt.show()

plt.close('all')


# Table of relations vs. number of theories that those relations appear in (or perhaps rather, usages across theories)
# Need relation (type) counts per theory and those then can be summed up to an overall statistic
relation_names = set([triple.relStr for theory in theories.values() for triple in theory.triples])

relation_counts = np.zeros((len(relation_names)))
relation_counts_across = np.zeros((len(relation_names)))

for i,r in zip(range(len(relation_names)),relation_names):
    n=0
    counts_across = 0
    for j,theory in zip(range(len(theory_names)),[theories[t] for t in theory_names]):
        theory_rels = [triple.relStr for triple in theory.triples]
        if r in theory_rels:
            n=n+1
            counts_across = counts_across + theory_rels.count(r)
    relation_counts[i]=n
    relation_counts_across[i]=counts_across

Names = [x for _,x in sorted(zip(relation_counts_across,relation_names),reverse=True)]
Counts = [x for x,_ in sorted(zip(relation_counts_across,relation_names),reverse=True)]

fig,ax = plt.subplots()
ax.bar(Names,Counts)
plt.xticks(rotation=90)
fig.subplots_adjust(bottom=0.3)
plt.show()



# Calculate 'percentage containment'
match_counts = np.zeros((len(theory_names), len(theory_names)))

for i,theory1 in zip(range(len(theory_names)),[theories[t] for t in theory_names]):
    for j,theory2 in zip(range(len(theory_names)),[theories[t] for t in theory_names]):
        theory_desc = " ".join([c.name.lower() for c in theory2.constructs.values()])
        n=0
        for construct in theory1.constructs.values():
            if construct.name.lower() in theory_desc:
                n=n+1
        match_counts[i,j]= (n*100)/len(theory1.constructs)


df = pd.DataFrame(match_counts, columns=theory_names, index=theory_names)


# Display a clustered heatmap of 'percentage containment'
#plt.pcolor(df)
plt.rcParams["axes.labelsize"] = 10
b = sns.clustermap(df, cmap='RdYlGn_r',row_cluster=True,yticklabels=True,xticklabels=True)
plt.show()
plt.close('all')


# Display a scatter plot of number of constructs vs. number of triples

x = [theories[t].getNumConstructs() for t in theory_names]
y = [theories[t].getNumTriples() for t in theory_names]


# Plot
fig, ax = plt.subplots()

ax.scatter(x, y)
plt.title('Number of constructs vs. number of triples per theory')
plt.xlabel('Number of constructs')
plt.ylabel('Number of triples')

for i, name in zip(range(len(theory_names)),theory_names):
    if x[i]>40 or y[i] > 80:
        ax.annotate(name, (x[i], y[i]))

plt.show()



# Build a composite graph of the immediate network neighbourhood of the constructs 'self-efficacy' and 'motivation' across all theories

G=nx.DiGraph()

names_of_interest = ['beliefs','attitudes'] # ,'motivation', 'self-efficacy'

for theory_num in theories.keys():
    theory = theories[theory_num]

    for triple in theory.triples:
        if (triple.const1.name.lower() in names_of_interest or triple.const2.name.lower() in names_of_interest) and 'influences' in triple.relStr.lower():
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

png_path = "network-neighbourhood.png"
pdot.write_png(png_path)


#nx.readwrite.gml.write_gml(G, 'network-neighbourhood.gml')