import os, json, copy
import pandas as pd
import validate

reload_data = True
# load Radius data
if reload_data:
    raw_data_file = r'/Users/dave/Documents/GitHub/radius/data_analysis.json'
    with open(raw_data_file) as fp:
        raw_data = json.load(fp)
        data = pd.DataFrame.from_records(raw_data)

# answer question 1
print('Number of non-null records in each field:')
print(data.count(axis=0))

# answer question 2
data_is_valid = copy.deepcopy(data)
cols_to_validate = []
#cols_to_validate = ['name', 'address', 'city', 'phone', 'revenue', 'state', 'zip',] 
# note validation is actually performed by the function registry validate.is_valid
for c in cols_to_validate:
    data_is_valid[c] = data[c].apply(validate.is_valid[c])
print('Number of true-valued records:')
print(data_is_valid[cols_to_validate].sum(axis=0).astype(int))


rv = pd.Series(list(filter(validate.find_bad_catcode, data['category_code']))).unique()

# answer question 3
print('Cardinality of')

