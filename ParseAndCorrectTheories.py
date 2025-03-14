import os
import csv
import codecs
import copy

import ontoutils
from ontoutils.lucid_chart import Relation

os.chdir('/Users/hastingj/Work/Projects/100 Behaviour Change/Theory Specification/Automated Parsing of Theories')


junctions = []
containers = []
theory_row_dicts = {}

directory = "theories-may2020"

theory_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
model_filenames = {}

for f in theory_files:
    with codecs.open(directory+"/"+str(f), mode='r', encoding="utf-8") as csv_file:
        model_num = str(f).split('.')[0]
        model_filenames[model_num] = str(f)
        model_name = str(f).split('.')[1]

        theory_row_dicts[model_num] = {}
        
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            id = row['Id']
            type = row['Name']
            label = str(row['Text Area 1']).strip()
            line_source = row['Line Source']
            line_dest = row['Line Destination']
            source_arrow = row['Source Arrow']
            dest_arrow = row['Destination Arrow']
            
            theory_row_dicts[model_num][id] = row
            
            if type in ['Process','Text','Rectangle','Terminator']:
                
                if type == 'Text' and label.startswith(model_num): # model name. Ignore
                    continue
                
                if type in ['Text','Rectangle','Terminator']:
                    print ("In model",model_num,"updating construct entity",id,"of type",type,"to Process")
                    theory_row_dicts[model_num][id]['Name']='Process'
                    theory_row_dicts[model_num][id]['Shape Library']='Flowchart Shapes'

            elif type == 'Line':
                #if len(label)>0: print("Relation label: ",label)
                # Some CSVs may contain lines for which the line source and line destination are the wrong way around. If ‘Source Arrow’ field contains Arrow and ‘Destination Arrow’ field contains None then ‘Line Source’ and ‘Line Destination’ need to be reversed. ‘Source Arrow’ and ‘Destination Arrow’ also need to be reversed. It is permissible that ‘Source Arrow’ and ‘Destination Arrow’ both contain Arrow. It is an error if ‘Source Arrow’ and ‘Destination Arrow’ both contain None; this should be flagged so a researcher can check the diagram. 
                if source_arrow == 'Arrow' and dest_arrow == 'None': 
                    print("In model",model_num,"Reversing direction of arrow id",id)
                    theory_row_dicts[model_num][id]['Line Source']=line_dest
                    theory_row_dicts[model_num][id]['Line Destination']=line_source
                    theory_row_dicts[model_num][id]['Source Arrow']='None'
                    theory_row_dicts[model_num][id]['Destination Arrow']='Arrow'
                if source_arrow == 'None' and dest_arrow == 'None':
                    print("Model:",model_num,"ERROR: NO-DIRECTION ARROW")
            elif type in ['Summing Junction', 'Connector', 'Or','Merge','Isosceles Triangle','Circle']:
                # Replace the circle and triangle
                if type == 'Circle':
                    #print("In model:",model_num," updating Circle with id",id,"to Connector")
                    theory_row_dicts[model_num][id]['Name']='Connector'
                    theory_row_dicts[model_num][id]['Shape Library']='Flowchart Shapes'
                if type == 'Isosceles Triangle':
                    #print("In model:",model_num," updating Isosceles Triangle with id",id,"to Merge")
                    theory_row_dicts[model_num][id]['Name']='Merge'
                    theory_row_dicts[model_num][id]['Shape Library']='Flowchart Shapes'
                junctions.append(str(model_num)+":"+id+":"+type)
            elif type == 'Rectangle Container':
                # A few CSVs may include Container Rectangles which contain other constructs. In these cases there will be data in the ‘Contained By’ field. Any constructs ‘contained by’ another construct should inherit the relationships of the container and the container should be deleted. 
                containers.append(str(model_num)+":"+id)
                #print("Got container: ",id)
            elif type == 'Page': # ignore
                continue
            else:
                print("ERROR: UNKNOWN TYPE: ",type)
            
# Process the junctions and containers out of the relations list by connecting all sources to all targets. Assign the relations the type corresponding to the type of the junction. 

ids_to_remove = {}

for strId in junctions: 
    [model_num,conn_id,type] = strId.split(":")
    if model_num not in ids_to_remove.keys():
        ids_to_remove[model_num] = []
    ids_to_remove[model_num].append(conn_id)  # Remove the connector
    print (f"Processing theory {model_num}")
    maxTheoryId = max( map(int, theory_row_dicts[model_num].keys()) )
    nextId = maxTheoryId+1
    
    if type in ['Merge','Isosceles Triangle']:
        type_str = 'Type of'
    if type == 'Summing Junction':
        type_str = '*'
    if type in ['Connector','Circle']:
        type_str = 'Part of'
    if type == 'Or':
        type_str = '+'
    
    jnc_srcs = []
    map_srcs = {}
    jnc_tars = []
    map_tars = {}
    
    # This works per model
    all_dests = {id:theory_row_dicts[model_num][id]['Line Destination'] for id in theory_row_dicts[model_num] if len(theory_row_dicts[model_num][id]['Line Destination'])>0 }
    
    for id in theory_row_dicts[model_num]:
        if theory_row_dicts[model_num][id]['Name'] == 'Line':
            line_to_copy = theory_row_dicts[model_num][id]
            source_id = theory_row_dicts[model_num][id]['Line Source']
            target_id = theory_row_dicts[model_num][id]['Line Destination']
            if source_id == conn_id:
                jnc_tars.append(target_id)
                ids_to_remove[model_num].append(id)
                # Check if any rels end on this rel
                if id in set(all_dests.values()): 
                    map_tars[target_id]=id
            if target_id == conn_id:
                jnc_srcs.append(source_id)
                ids_to_remove[model_num].append(id)
                if id in set(all_dests.values()):
                    map_srcs[source_id]=id
    
    if len(map_srcs)>0: 
        print ("Sources to be mapped: ",map_srcs)
    if len(map_tars)>0:
        print ("Targets to be mapped: ",map_tars)
            
    rels_to_add = []
    for s in jnc_srcs:
        for t in jnc_tars:
            rels_to_add.append((s,t))
            
    for (s,t) in rels_to_add:
        rel = copy.deepcopy(line_to_copy)
        rel['Id']=str(nextId)
        rel['Line Source'] = s
        rel['Line Destination'] = t
        rel['Text Area 1'] = type_str
        theory_row_dicts[model_num][str(nextId)] = rel
        if s in map_srcs.keys(): 
            oldId = map_srcs[s]
            for arrowToOldId in  [k for (k,v) in all_dests.items() if v==oldId ]:
                if arrowToOldId not in theory_row_dicts[model_num]:
                    print("ERROR! Can't find original arrow",arrowToOldId,"In model ",model_num)
                else: 
                    theory_row_dicts[model_num][arrowToOldId]['Line Destination'] = str(nextId)
                print ("In model",model_num,"Mapped arrow",arrowToOldId," that ended on ",oldId,"to end on",str(nextId))
        if t in map_tars.keys(): 
            oldId = map_tars[t]
            for arrowToOldId in [k for (k,v) in all_dests.items() if v==oldId ]:
                theory_row_dicts[model_num][arrowToOldId]['Line Destination'] = str(nextId)
                print ("In model",model_num,"Mapped arrow",arrowToOldId," that ended on ",oldId,"to end on",str(nextId))
        nextId = nextId+1
        print("Added expanded arrow ",rel['Id'],"to model",model_num,"relating",s,"to",t)
    
for strId in containers: 
    [model_num,con_id] = strId.split(":")
    if model_num not in ids_to_remove.keys():
        ids_to_remove[model_num] = []
    ids_to_remove[model_num].append(con_id)
    print("Got container",con_id,"in model",model_num)
    
    maxTheoryId = 1
    for id in theory_row_dicts[model_num]:
        if int(id) > maxTheoryId:
            maxTheoryId = int(id)
    nextId = maxTheoryId+1
    
    contained = []
    rel_tars = []
    
    for id in theory_row_dicts[model_num]:
        source_id = theory_row_dicts[model_num][id]['Line Source']
        target_id = theory_row_dicts[model_num][id]['Line Destination']
        contained_by = theory_row_dicts[model_num][id]['Contained By']
            
        if contained_by == con_id:
            contained.append(id)
            theory_row_dicts[model_num][id]['Contained By'] = ''
            
        if source_id == con_id: # only ever this direction
            line_to_copy = theory_row_dicts[model_num][id]
            rel_tars.append(target_id)
            ids_to_remove[model_num].append(id)
                
    rels_to_add = []
    for c in contained:
        for t in rel_tars:
            rels_to_add.append((c,t))
            
    for (s,t) in rels_to_add:
        rel = copy.deepcopy(line_to_copy)
        rel['Id']=str(nextId)
        rel['Line Source'] = s
        rel['Line Destination'] = t
        theory_row_dicts[model_num][str(nextId)] = rel
        nextId = nextId+1
        print("Added expanded arrow ",rel['Id'],"to model",model_num,"relating",s,"to",t)

    
# Remove the junctions and arrows to the junctions
for model_num in ids_to_remove.keys():
    ids = set(ids_to_remove[model_num])
    print ("Going to remove ",ids," from model ",model_num)
    for id in ids:
        del theory_row_dicts[model_num][id]
        
        
        
# Check for arrows that start on other arrows and correct them
for model_num in theory_row_dicts.keys():
    for row in theory_row_dicts[model_num].keys():
        if theory_row_dicts[model_num][row]['Name'] == 'Line':
            line_source = theory_row_dicts[model_num][row]['Line Source']
            if line_source == '':
                print ("Error! No line source found for line ",row," in theory ",model_num)
                continue
            if line_source not in theory_row_dicts[model_num].keys():
                print ("Error! Line source no longer exists for line ",row,"in theory ",model_num)
                continue
            line_source_type = theory_row_dicts[model_num][line_source]['Name']
            if line_source_type == 'Line':
                orig_source = theory_row_dicts[model_num][line_source]['Line Source']
                print("Arrow starting on arrow: ",row," starts on ",line_source," in theory ",model_num, "...Updating to original source",orig_source)
                theory_row_dicts[model_num][row]['Line Source'] = orig_source
            


# Check for arrows that end on other arrows and correct them
tofix = {}
for model_num in theory_row_dicts.keys():
    for row in theory_row_dicts[model_num].keys():
        if theory_row_dicts[model_num][row]['Name'] == 'Line':
            line_dest = theory_row_dicts[model_num][row]['Line Destination']
            if line_dest == '':
                print ("Error! No line destination found for line ",row," in theory ",model_num)
                continue
            if line_dest not in theory_row_dicts[model_num].keys():
                print ("Error! Line destination no longer exists for line ",row,"in theory ",model_num)
                continue
            line_dest_type = theory_row_dicts[model_num][line_dest]['Name']
            if line_dest_type == 'Line':
                rel_type = theory_row_dicts[model_num][row]['Text Area 1']
                orig_rel_type = theory_row_dicts[model_num][line_dest]['Text Area 1'].strip()
                #print("Arrow ending on arrow: ",row," ends on ",line_dest," in theory ",model_num,", this rel type: ",rel_type,", orig rel type: ",orig_rel_type)
                if model_num not in tofix.keys():
                    tofix[model_num] = {}
                if line_dest not in tofix[model_num].keys():
                    tofix[model_num][line_dest] = []
                tofix[model_num][line_dest].append(row)
                

for model_num in tofix.keys():
    dests = tofix[model_num].keys()
    for line_dest in dests: 
        # A list of rows that have to be updated 
        rows = tofix[model_num][line_dest]
        
        maxTheoryId = max( map(int, theory_row_dicts[model_num].keys()) )
        nextId = maxTheoryId+1
        
        # Replace the original arrow with a reified class and two arrows
        # Class name: "the X-Y <type> relationship"
        # Then relate the third arrow to this class
        # 1. Copy the original source to make the new entity: 
        orig_source_id = theory_row_dicts[model_num][line_dest]['Line Source']
        orig_dest_id = theory_row_dicts[model_num][line_dest]['Line Destination']
        print ("Modifying line from ",orig_source_id,"to",orig_dest_id)
        orig_source_name = theory_row_dicts[model_num][orig_source_id]['Text Area 1'].strip()
        orig_dest_name = theory_row_dicts[model_num][orig_dest_id]['Text Area 1'].strip()
        orig_rel_type = theory_row_dicts[model_num][line_dest]['Text Area 1'].strip()
    
        relEntity = copy.deepcopy(theory_row_dicts[model_num][orig_source_id])
        relEntity['Id']=str(nextId)
        relEntity['Name']='Terminator' # rounded box
        relLabel = Relation.getFullLabelForShortLabel(orig_rel_type)
        if relLabel is None:
            relLabel = orig_rel_type
        relEntity['Text Area 1'] = f"the '{orig_source_name}' to '{orig_dest_name}' {relLabel} relationship"
        print(relEntity['Text Area 1'])
        theory_row_dicts[model_num][str(nextId)] = relEntity
        # Map all the arrows that ended on an arrow on to the new entity
        for row in rows: 
            theory_row_dicts[model_num][row]['Line Destination'] = str(nextId)
        # Create one more relation to connnect the new entity to its original dest
        relEntity = copy.deepcopy(theory_row_dicts[model_num][line_dest])
        relEntity['Line Source'] = str(nextId)
        
        # Map the original relation onto this new entity
        theory_row_dicts[model_num][line_dest]['Line Destination'] = str(nextId)
        theory_row_dicts[model_num][line_dest]['Text Area 1'] = "relates through"

        nextId = nextId+1
        relEntity['Id']=str(nextId)
        relEntity['Text Area 1'] = "relates to"
        theory_row_dicts[model_num][str(nextId)] = relEntity
        print ("Fixed ",line_dest,"in",model_num)

        
                
        

# write the files out again, fixed
for model_num in theory_row_dicts.keys():
    model_filename = model_filenames[model_num]+"MODIFIED"
    with codecs.open("test-output/"+model_filename+".csv",mode='w', encoding="utf-8") as outfile:
        fieldNames = [k for k in theory_row_dicts[model_num]['1'].keys()]
        #print (model_num,fieldNames)
        writer = csv.DictWriter(outfile,fieldNames)
        writer.writeheader()
        for rowId in theory_row_dicts[model_num].keys():
            writer.writerow(theory_row_dicts[model_num][rowId])
        







