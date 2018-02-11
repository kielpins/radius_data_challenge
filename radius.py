import os, json, re, copy
import pandas as pd

raw_data_file = r'/Users/dave/Documents/GitHub/radius/data_analysis.json'

with open(raw_data_file) as fp:
    raw_data = json.load(fp)

data = pd.DataFrame.from_records(raw_data)

# address question 1
print('Number of non-null records in each field:')
print(data.count(axis=0))

# address question 2
# define filtering for the various fields

# regex looks for basic (123) 456-7890 format with variations in use of parentheses, dashes, and whitespace 
phone_regex_string = '\(*\s*([0-9]{3})\s*\)*\-*\s*\-*([0-9]{3})\s*\-*\s*([0-9]{4})'
# compile regex for efficiency since we will use it many times
phone_re = re.compile(phone_regex_string)

def find_bad_phone(val):
    if not pd.isnull(val):
        try:
            if not str.isnumeric(val):
                m = re.match(phone_re, val)
                if m is None:
                    return val
        except TypeError:
            return val
    else:
        return None

def is_valid_phone(val):
    if pd.isnull(val):
        return False
    if type(val) is int:
        val = str(val)
    elif not str.isnumeric(val): # use regex to extract numeric string from value
        m = re.match(phone_re, val)
        try:
            if len(m.groups()) == 4:
                val = ''.join([g for g in m.groups()[1:]])
        except AttributeError:
            return False
    if len(val) == 10: # phone number should have 10 digits
        return True
    else:
        return False

def find_bad_zip(val):
    if pd.isnull(val):
        return None
    if type(val) is int:
        val = str(val)
    if str.isnumeric(val) and len(val) != 5:
        return val
    return None
        
def is_valid_zip(val):
    if pd.isnull(val):
        return False
    if type(val) is int:
        val = str(val)
    if str.isnumeric(val) and len(val) == 5:
        return True
    else:
        return False
    
is_valid = {
    'phone': is_valid_phone,
    'zip': is_valid_zip,
}

data_is_valid = copy.deepcopy(data)
cols_to_validate = ['phone', 'zip'] 
for c in cols_to_validate:
    data_is_valid[c] = data[c].apply(is_valid[c])


phu = pd.Series(list(filter(check_phone, data['phone']))).unique()


# address question 3
print('Cardinality of')
    