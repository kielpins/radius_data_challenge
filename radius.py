import os, json, copy
import pandas as pd
import validate

reload_data = True
# load Radius data
if reload_data:
    raw_data_file = r'/Users/dave/Documents/GitHub/radius/data_analysis.json'
    with open(raw_data_file) as fp:
        raw_data = json.load(fp)
columns = ['name', 'address', 'city', 'state', 'zip', 'time_in_business', 'phone', 'category_code', 'headcount', 'revenue',] 
data = pd.DataFrame.from_records(raw_data, columns=columns)
def make_upper(val):
    try:
        return val.upper()
    except AttributeError:
        return val
data['city'] = data['city'].apply(make_upper) # comparison with GeoNames data should be case-independent

## answer question 1
print('Number of non-null records in each field:')
print(data.count(axis=0))

## answer question 2
# duplicate 'name' entries are invalid from the start, remove them all
data_dedup = data.drop_duplicates('name', keep=False)
data_is_valid = copy.deepcopy(data_dedup) # to be used for counting valid entries
# count valid entries in city, state, zip fields
data_csz_good = pd.merge(data_dedup, validate.us_geonames)
#cols_to_validate = columns
cols_to_validate = ['name', 'address', 'phone', 'category_code', 'revenue',]
for c in cols_to_validate:
    # note validation is actually performed by the functions in the validate module, called through the registry validate.is_valid    
    data_is_valid[c] = data_dedup[c].apply(validate.is_valid[c])
print('Number of true-valued records:')
print(data_is_valid[cols_to_validate].sum(axis=0).astype(int))
print('city/state/zip', len(data_csz_good))

## answer question 3
print('Cardinality of')

gn = copy.deepcopy(validate.us_geonames[['city', 'state', 'zip']])
gn = gn.drop_duplicates(keep=False)
gn['city'] = gn['city'].apply(lambda x: x.upper())