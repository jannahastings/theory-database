import os
#os.chdir('/Users/hastingj/Work/Python/TheoryDatabase/definitions')
import openpyxl
import difflib

### Parse theory definitions

def parseTheoryDefinitions(definition_file):
    wb = openpyxl.load_workbook(definition_file, data_only=True)
    sheet = wb['Sheet1']
    for row in sheet.iter_rows(min_row=2, min_col=0, max_row=1466, max_col=10):
        theory_num = row[0].value
        if str(theory_num) not in theories.keys():
            print("Unknown theory num",theory_num)
        else:
            theory_name = row[1].value
            construct_label = row[2].value.strip().replace("(constraints)","").lower().capitalize()
            construct_def = row[3].value
            if construct_def and construct_def.strip():
                if construct_label not in theories[str(theory_num)].constructs_by_name.keys():
                    theory_constructs = theories[str(theory_num)].constructs_by_name.keys()
                    similarities = [difflib.SequenceMatcher(None, c,construct_label).ratio() for c in theory_constructs]
                    zipped_lists = zip(similarities,theory_constructs)
                    sorted_zipped_lists = sorted(zipped_lists, reverse=True)
                    construct_label = sorted_zipped_lists[0][1]
                theories[str(theory_num)].constructs_by_name[construct_label].definition = construct_def





