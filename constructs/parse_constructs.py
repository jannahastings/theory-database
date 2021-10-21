 import openpyxl

combined_data = []

def parseConstructs(constructs_file):
    num = 0
    wb = openpyxl.load_workbook(constructs_file, data_only=True)
    sheet = wb['Sheet1']
    for row in sheet.iter_rows(min_row=2, min_col=0, max_row=1466, max_col=10):
        theory_num = row[0].value
        construct_defn = row[2].value
        ontology_id = row[4].value
        ontology_label = row[5].value
        alt_ontology_id = row[6].value
        alt_ontology_label = row[7].value
        alt_ontology_id2 = row[8].value
        alt_ontology_label2 = row[9].value

        if not(theory_num == None or construct_defn == None):
            if not(ontology_id == None or ontology_label == None):
                # print("looking at theory_num", theory_num)
                theory_dict = {
                        "Theory_ID": theory_num, 
                        "Construct": construct_defn, 
                        "Label": ontology_label,
                        "Ontology_ID": ontology_id.replace(":","_")
                        }
                combined_data.append(theory_dict)
            
            #additional ids
            if not(alt_ontology_id == None or alt_ontology_label == None):
                alt_theory_dict = {
                    "Theory_ID": theory_num, 
                    "Construct": construct_defn, 
                    "Label": alt_ontology_label,
                    "Ontology_ID": alt_ontology_id.replace(":","_")
                    }
                combined_data.append(alt_theory_dict)

            if not(alt_ontology_id2 == None or alt_ontology_label2 == None):
                alt_theory_dict2 = {
                    "Theory_ID": theory_num, 
                    "Construct": construct_defn, 
                    "Label": alt_ontology_label2,
                    "Ontology_ID": alt_ontology_id2.replace(":","_")
                    }
                combined_data.append(alt_theory_dict2)

    # print(combined_data)
    return(combined_data)



        