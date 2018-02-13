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

# make `city` field upper-case for join to GeoNames data
def make_upper(val):
    try:
        return val.upper()
    except AttributeError:
        return val
data['city'] = data['city'].apply(make_upper)

## answer question 1
print('Number of non-null records in each field:')
print(data.count(axis=0))

## answer question 2
# duplicate 'name' entries are invalid from the start, remove them all
data_dedup = data.drop_duplicates('name', keep=False)
data_is_valid = copy.deepcopy(data_dedup) # to be used for counting valid entries
# get valid entries in city, state, zip fields
data_csz_good = pd.merge(data_dedup, validate.us_geonames)
# validate remaining fields
vk = list(validate.is_valid.keys())
for c in vk:
    # note validation is actually performed by the functions in the validate module, called through the registry validate.is_valid    
    data_is_valid[c] = data_dedup[c].apply(validate.is_valid[c])
print('Number of true-valued records:')
print(data_is_valid[vk].sum(axis=0).astype(int))
print('city/state/zip', len(data_csz_good))

## answer question 3
print('Cardinality of each field')
for c in data.columns:
    print('{}\t{}'.format(c, len(data[c].unique())))