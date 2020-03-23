# Parse the theories from the CSV files and consolidate information about them

import os
import csv
import codecs
import pandas
import os.path
from whoosh import index
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer

# os.chdir('/Users/hastingj/Work/Python/TheoryDatabase')

theory_dir = 'theories'

theory_files = [file for file in os.listdir(theory_dir) if file.endswith(".csv")]


class Theory:
    def __init__(self,number,name):
        self.number = number
        self.name = name
        self.constructs = {}
        self.triples = []
    def getNumConstructs(self):
        return(len(self.constructs.keys()))
    def getNumTriples(self):
        return(len(self.triples))

class Construct:
    def __init__(self,number,name):
        self.number = number
        self.name = name

class Relation:
    INFLUENCES = 0
    POS_INFLUENCES = 1
    NEG_INFLUENCES = 2
    TYPE_OF = 3
    PART_OF = 4
    MAY_INFLUENCE = 5
    INFLUENCE_MULT = 6
    INFLUENCE_SUM = 7
    CORR_WITH = 8
    VALUE_OF = 9
    HAS_ATTRIBUTE = 10
    HAS_START = 11
    HAS_END = 12
    TRANSITION = 13
    THROUGH = 14
    TO = 15

    def getRelTypeForLabelString(label):
        if label == "influences" or label == "" or label == "+/-" or label == 'Bi-directional influence':
            return (Relation.INFLUENCES)
        if label == "positively influences" or label == "+":
            return (Relation.POS_INFLUENCES)
        if label == "negatively influences" or label == "-":
            return (Relation.NEG_INFLUENCES)
        if label == "may be influenced by" or label == "?" or label == "+?":
            return (Relation.MAY_INFLUENCE)
        if label == "is influenced (*) by" or label == "*":
            return (Relation.INFLUENCE_MULT)
        if label == "is influenced (sum) by" or label == "Sum":
            return (Relation.INFLUENCE_SUM)
        if label == "correlates with" or label == "Correlation" or label == "Correlations":
            return (Relation.CORR_WITH)
        if label == "Type of":
            return (Relation.TYPE_OF)
        if label == "Part of":
            return (Relation.PART_OF)
        if label == "Value of":
            return (Relation.VALUE_OF)
        if label == "Has attribute":
            return (Relation.HAS_ATTRIBUTE)
        if label == "Has start":
            return (Relation.HAS_START)
        if label == "Has end":
            return (Relation.HAS_END)
        if label == "Transition":
            return (Relation.TRANSITION)
        if label == "relates through":
            return (Relation.THROUGH)
        if label == "relates to":
            return (Relation.TO)
        print ("Label not recognised: ",label)
        return (None)
    def getStringForRelType(reltype):
        relstr = "Related to"
        if reltype==Relation.INFLUENCES:
            relstr = "Influences"
        if reltype==Relation.POS_INFLUENCES:
            relstr = "Positively influences"
        if reltype==Relation.NEG_INFLUENCES:
            relstr = "Negatively influences"
        if reltype==Relation.MAY_INFLUENCE:
            relstr = "May influence"
        if reltype==Relation.INFLUENCE_MULT:
            relstr = "Influences (*)"
        if reltype==Relation.INFLUENCE_SUM:
            relstr = "Influences (sum)"
        if reltype==Relation.CORR_WITH:
            relstr = "Correlates with"
        if reltype==Relation.TYPE_OF:
            relstr = "Type of"
        if reltype==Relation.PART_OF:
            relstr = "Part of"
        if reltype==Relation.VALUE_OF:
            relstr = "Value of"
        if reltype==Relation.HAS_ATTRIBUTE:
            relstr = "Has attribute"
        if reltype==Relation.HAS_START:
            relstr = "Has start"
        if reltype==Relation.HAS_END:
            relstr = "Has end"
        if reltype==Relation.TRANSITION:
            relstr = "Transitions to"
        if reltype==Relation.THROUGH:
            relstr = "Relates through"
        if reltype==Relation.TO:
            relstr = "To"
        return (relstr)

class Triple:
    def __init__(self,const1,rel,const2):
        self.const1 = const1
        self.rel = rel
        self.const2 = const2
        self.relStr = Relation.getStringForRelType(self.rel)

    def __str__(self):
        return(", ".join([self.const1.name,self.relStr,self.const2.name]))


### Program execution:

theories = {}
theory_names_to_ids = {}
id_labels = {}
relations = []
row_data = []
rel_types = {}
ix = None

def setup():
    for f in theory_files:
        with codecs.open(theory_dir+'/'+str(f), mode='r', encoding="utf-8") as csv_file:
            model_num = str(f).split('.')[0]
            model_name = str(f).split('.')[1].strip()
            model_name = model_name.replace(' - FINAL','')
            model_name = model_name.replace('FINAL','')
            model_name = model_name.replace(' - RW','')
            theory_names_to_ids[model_name] = model_num

            theory = Theory(model_num,model_name)
            theories[model_num] = theory

            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                id = row['Id']
                type = row['Name']
                label = str(row['Text Area 1']).strip()
                line_source = row['Line Source']
                line_dest = row['Line Destination']

    #            print(f"Model: {model_num}, Object Id: {id}, Drawing type: {type}, Label: {label}, Line source: {line_source}, destination {line_dest}")

                if type in ['Process','Text','Rectangle','Terminator']:
                    construct = Construct(name=label,number=id)
                    theory.constructs[id] = construct
                    id_labels[str(model_num)+":"+id]=label

                if type == 'Line':
                    rel_type = Relation.getRelTypeForLabelString(label)
                    relations.append(str(model_num)+":"+line_source+":"+line_dest+":"+str(rel_type))

    # Build the triples
    for rel in relations:
        [mod_id,src_id,tar_id,type] = rel.split(":")
        theory = theories[mod_id]
        if (src_id in theory.constructs):
            constr1 = theory.constructs[src_id]
            if (tar_id in theory.constructs):
                constr2 = theory.constructs[tar_id]
                triple = Triple(constr1,int(type),constr2)
                theory.triples.append(triple)
                #print(str(triple),f"Theory {mod_id}")
            else:
                print("Target "+tar_id+"not recognised in theory "+mod_id)
        else:
            print("Source "+src_id+"not recognised in theory "+mod_id)

    # get a table of counts for theories

    for t_id in theories:
        theory = theories[t_id]
        t_name = theory.name
        num_constructs = len(theory.constructs)
        num_triples = len(theory.triples)
        row_data.append({"Theory":t_id,"TheoryName":t_name,"Constructs":num_constructs,"Triples":num_triples})

#    table = pandas.DataFrame(row_data)
#    table = table[["Theory","TheoryName","Constructs","Triples"]]
#    table.to_csv("theory-counts.csv")


# get a table of counts for distinct relation types
    for t_id in theories:
        theory = theories[t_id]
        triples = theory.triples
        for t in triples:
            rel_type = t.rel
            if rel_type not in rel_types:
                rel_types[rel_type] = []
            rel_types[rel_type].append(t)

#table = pandas.DataFrame([ (Relation.getStringForRelType(rid), len(relations[rid])) for rid in relations])
#table.columns = ["Relation","Count"]
#table.to_csv("relation-counts.csv")



def rebuildIndex(index_dir):

    schema = Schema(doc_type = ID(stored=True),
                    theory_id = ID(stored=True),
                    theory_name = TEXT(stored=True),
                    construct_id = ID(stored=True),
                    construct_name = TEXT(stored=True),
                    relation_id = ID(stored=True),
                    relation_name = TEXT(stored=True),
                    triple_construct_two_id = ID(stored=True),
                    triple_construct_two_name = TEXT(stored=True))

    ix = index.create_in(index_dir, schema)

    writer = ix.writer()

    for t_id in theories:
        theory = theories[t_id]
        t_name = theory.name
        writer.add_document(doc_type="Theory",
                            theory_id=t_id,
                            theory_name=t_name)

    for theory in theories.values():
        for construct in theory.constructs.values():
            writer.add_document(doc_type="Construct",
                            theory_id=theory.number,
                            theory_name=theory.name,
                            construct_id=construct.number,
                            construct_name=construct.name)

        for triple in theory.triples:
            writer.add_document(doc_type = "Triple",
                            theory_id = theory.number,
                            theory_name = theory.name,
                            construct_id = triple.const1.number,
                            construct_name = triple.const1.name,
                            relation_id = str(triple.rel),
                            relation_name = triple.relStr,
                            triple_construct_two_id = triple.const2.number,
                            triple_construct_two_name = triple.const2.name)

    writer.commit()

def searchForTheory(theory,index_dir):
    ix = open_dir(index_dir)
    qp = QueryParser("theory_name", schema=ix.schema)
    q = qp.parse("doc_type:Theory and theory_name:"+theory)
    returned_values = {}
    with ix.searcher() as s:
        results = s.search(q,limit=None)
        print("search for theory name",theory,"matched",len(results),"results:")
        for h in results:
            theory_name = h['theory_name']
            theory_id = h['theory_id']
            returned_values[theory_id]=theory_name
        return (returned_values)

def searchForConstruct(construct,index_dir):
    ix = open_dir(index_dir)
    qp = QueryParser("construct_name", schema=ix.schema)
    q = qp.parse("doc_type:Construct and construct_name:"+construct)
    returned_values = {}
    with ix.searcher() as s:
        results = s.search(q,limit=None)
        print("search for ",construct,"matched",len(results),"results:")
        for h in results:
            construct_name = h['construct_name']
            theory_name = h['theory_name']
            if construct_name not in returned_values:
                returned_values[construct_name] = []
            returned_values[construct_name].append(theory_name)
        return (returned_values)

def searchForRelation(relation,index_dir):
    ix = open_dir(index_dir)
    qp = QueryParser("relation_name", schema=ix.schema)
    q = qp.parse("doc_type:Triple and relation_name:"+relation)
    returned_values = {}
    with ix.searcher() as s:
        results = s.search(q,limit=None)
        print("search for ",relation,"matched",len(results),"results:")
        for h in results:
            theory_name = h['theory_name']
            relation_name = h['relation_name']
            const_1 = h['construct_name']
            const_2 = h['triple_construct_two_name']
            if relation_name not in returned_values:
                returned_values[relation_name]={}
            if theory_name not in returned_values[relation_name]:
                returned_values[relation_name][theory_name]=[]
            returned_values[relation_name][theory_name].append(" ".join([const_1,relation_name,const_2]))
        return (returned_values)
