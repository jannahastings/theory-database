# Parse the theories from the CSV files and consolidate information about them

import os
# os.chdir('/Users/hastingj/Work/Python/TheoryDatabase')
import csv
import codecs
import pandas
import os.path
import re
from whoosh import index
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
import ontoutils
from ontoutils.lucid_chart import ParseLucidChartCsv

exec(open('definitions/ParseDefinitions.py').read())


theory_dir = 'theories'

theory_files = [file for file in os.listdir(theory_dir) if file.endswith(".csv")]


class Theory:
    def __init__(self,number,name):
        self.number = number
        self.name = name
        self.constructs = {}
        self.constructs_by_name = {}
        self.reified_rels = {}
        self.triples = []
        self.taken_from = []
        self.supplemented_by = []
    def getNumConstructs(self):
        return(len(self.constructs.keys()))
    def getNumTriples(self):
        return(len(self.triples))
    def getNumber(self):
        return(int(self.number))
    def getCountReferences(self):
        return ( len(self.taken_from) + len(self.supplemented_by) )

class Construct:
    def __init__(self,number,name):
        self.number = number
        self.name = name
        self.definition = None
        self.annotations = []

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


# TODO implement a proper dictionary of variants of names for labels in lucid_wrapper

    def getRelTypeForLabelString(label):
        if label.lower() == "influences" or label == "" or label == "+/-" or label == 'Bi-directional influence':
            return (Relation.INFLUENCES)
        if label.lower() == "positively influences" or label == "+":
            return (Relation.POS_INFLUENCES)
        if label.lower() == "negatively influences" or label == "-":
            return (Relation.NEG_INFLUENCES)
        if label.lower() == "may be influenced by" or label == "?" or label == "+?" or label == "May influence":
            return (Relation.MAY_INFLUENCE)
        if label.lower() == "is influenced (*) by" or label == "*" or label == "Influences (*)":
            return (Relation.INFLUENCE_MULT)
        if label.lower() == "is influenced (+) by" or label.lower() == "is influenced (sum) by" or label == "Sum":
            return (Relation.INFLUENCE_SUM)
        if label.lower() == "correlates with" or label == "Correlation" or label == "Correlations":
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
        if label == "Transition" or label == "Transitions to":
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
            relstr = "Influences (+)"
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
    def __init__(self,const1,rel,const2,reified_rel=None):
        self.const1 = const1
        self.rel = rel
        self.const2 = const2
        self.relStr = Relation.getStringForRelType(self.rel)
        self.reified_rel = reified_rel

    def __str__(self):
        return(", ".join([self.const1.name,self.relStr,self.const2.name]))

class Annotation: 
    def __init__(self,id,label):
        self.id = id
        self.label = label
    def __str__(self):
        return(self.label)
    

### Program execution:

theories = {}
theory_names_to_ids = {}
relations = []
row_data = []
rel_types = {}
ix = None


def setup():
    for f in theory_files:
        model_num = str(f).split('.')[0]
        model_name = str(f).split('.')[1].strip()
        model_name = model_name.replace(' - FINAL','')
        model_name = model_name.replace('FINAL','')
        model_name = model_name.replace('corrections May2020','')
        model_name = model_name.replace('+','')
        model_name = model_name.replace(' - RW','')
        model_name = model_name.strip()
        #print(model_name)
        theory_names_to_ids[model_name] = model_num

        theory = Theory(model_num,model_name)
        theories[model_num] = theory

        print("About to parse theory: ",model_num,model_name)
        (entities, relations) = ParseLucidChartCsv.parseCsvEntityData(theory_dir+"/"+f)

        r_pattern = re.compile("the .+? relationship$")
        r_search = re.compile("the \'(.+?)\' to \'(.+?)\' (.+?) relationship")

        for e_id in entities:
            e = entities[e_id]
            construct = Construct(e_id,e.name)
            


            if re.match(r_pattern, e.name):
                theory.reified_rels[e.id] = construct
            else:
                #todo: add and test Annotations: 
                annotation = Annotation(e_id,e.name)
                construct.annotations.append(annotation)
                
                theory.constructs[e.id] = construct
                theory.constructs_by_name[e.name] = construct

        for r in relations:
            rel_type = Relation.getRelTypeForLabelString(r.relType)
            if rel_type == Relation.THROUGH:
                # Find the REIFIED RELATIONAL ENTITY. There should be just one.
                constr1 = theory.constructs[r.entity1.id]
                reified_rel = theory.reified_rels[r.entity2.id]
                target_name = r.entity2.name
                m = re.search(r_search, target_name)
                if m:
                    entity1_name = m.group(1)
                    entity2_name = m.group(2).strip()
                    rel_name = m.group(3)
                    real_rel_type = Relation.getRelTypeForLabelString(rel_name)
                    if entity2_name in theory.constructs_by_name:
                        real_entity_2 = theory.constructs_by_name[entity2_name]
                        triple = Triple(constr1,real_rel_type,real_entity_2,reified_rel)
                        theory.triples.append(triple)
                    else:
                        print("Name",entity2_name,"not found in theory",theory.number)
                else:
                    print("Error parsing",target_name)
            elif rel_type == Relation.TO:
                pass
            else:
                constr1 = theory.constructs[r.entity1.id]
                type = Relation.getRelTypeForLabelString(r.relType)
                if r.entity2.id in theory.constructs:
                    constr2 = theory.constructs[r.entity2.id]
                elif r.entity2.id in theory.reified_rels:
                    constr2 = theory.reified_rels[r.entity2.id]

                triple = Triple(constr1,type,constr2)
                theory.triples.append(triple)

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

# load theory references.
    with open('references/OBMS References.csv','r') as csvrefsfile:
        reader = csv.reader(csvrefsfile)

        header = next(reader)
        for row in reader:
            #print(row)
            theory_name = row[0]
            if len(theory_name) > 0: # ignore blank lines
                theory_num = theory_name.split(":")[0]
                if theory_num not in theories.keys():
                    print("Could not find theory for ",theory_num," from ",theory_name)
                theory = theories[theory_num]
                for i in [1,2,3]:
                    taken_from = row[i]
                    if taken_from is not None and len(taken_from)>0:
                        theory.taken_from.append(taken_from)
                for i in [4,5]:
                    supplemented_by = row[i]
                    if supplemented_by is not None and len(supplemented_by)>0:
                        theory.supplemented_by.append(supplemented_by)

# parse theory construct definitions
    parseTheoryDefinitions("definitions/Final Constructs (Across Theory Mapping).xlsx")


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

# setup()