import pandas as pd
# from vector_clean import merge_models 
# from final_json import apply_set_mappings
# import json


def extract_subject_data(mapping_file):

    df = pd.read_excel(mapping_file, header=None)
    # --- PHYSICS ---
    physics = df.iloc[1:21, [0, 2, 4]] 
    physics.columns = ["SET A", "SET B", "SET C"]
    physics.index = range(1, len(physics) + 1)

    # --- CHEMISTRY ---
    chem_start = df[df.astype(str)
                      .apply(lambda x: x.str.contains("CHEMISTRY", case=False, na=False))
                      .any(axis=1)].index[0]
    chemistry = df.iloc[chem_start + 2:chem_start + 22, [0, 2, 4]]
    chemistry.columns = ["SET A", "SET B", "SET C"]
    chemistry.index = range(1, len(chemistry) + 1)

    # --- MATHS ---
    math_start = df[df.astype(str)
                     .apply(lambda x: x.str.contains("MATHS", case=False, na=False))
                     .any(axis=1)].index[0]
    maths = df.iloc[math_start + 2:math_start + 22, [0, 2, 4]]
    maths.columns = ["SET A", "SET B", "SET C"]
    maths.index = range(1, len(maths) + 1)

    data = [physics, chemistry, maths]

    print("✅ DataFrames created for Physics, Chemistry, and Maths.")
    
    return data




# print("Data Extraction Module Loaded.")
# # mapping = extract_subject_data('AI-question-and-answers/answerkey.xlsx')
# print(vector_data)
# vector_data = merge_models(vector_data)
# print(vector_data)

# final_data = apply_set_mappings(vector_data, mapping)
# final_data =  json.dumps(final_data, ensure_ascii=False)

# print("Final Mapped Data:")
# print(final_data)





