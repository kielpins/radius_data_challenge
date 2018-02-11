import re
import pandas as pd

# load US geographical data, sourced from GeoNames.org
# Puerto Rico and Virgin Islands are referenced in data, make sure these are appended
col_names = ['zip', 'city', 'state', 'state_abbrev']
us_geonames = pd.read_csv('US.txt', sep='\t', usecols=[1,2,3,4], names=col_names)
puerto_rico_geonames = pd.read_csv('PR.txt', sep='\t', usecols=[1,2,3,4], names=col_names)
virgin_islands_geonames = pd.read_csv('VI.txt', sep='\t', usecols=[1,2,3,4], names=col_names)
us_geonames = us_geonames.append(puerto_rico_geonames).append(virgin_islands_geonames)

## filter for valid address

address_stemmer_string = '([0-9a-z ]*) ste'
address_stemmer_re = re.compile(address_stemmer_string)

def find_bad_address(val):
    if pd.isnull(val):
       return None
    if type(val) is not str:
        return val
    if len(val) < 1:
        return val
    if not str.isnumeric(val[0]):
        return val
    return None

def is_valid_address(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    if len(val) < 1:
        return False
    if not str.isnumeric(val[0]):
        return False
    return True

## filter for valid category code

catvals = None

def find_bad_catcode(val):
    if pd.isnull(val):
        return None
    val = str(val)
    if len(val) < 8:
        return val
    else:
        val = val[:-2]
        if val not in catvals:
            return val
    return None

def is_valid_catcode(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    if val not in catvals:
        return False
    return True

## filter for valid cities
    
cityvals = set(list(map(lambda x: x.lower(), us_geonames['city'].values)))

def find_bad_city(val):
    if pd.isnull(val):
        return None
    if type(val) is not str:
        return val
    if val.lower() not in cityvals:
        return val
    return None

def is_valid_city(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    if val.lower() not in cityvals:
        return False
    return True

## filter for valid names

def find_bad_name(val):
    if pd.isnull(val):
        return None
    if type(val) is not str:
        return val
    return None

def is_valid_name(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    return True

## filter for valid phone numbers

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

## filter for valid revenue

revenue_regex_string = '\$*([0-9.]*\,*[0-9]+) to \$*([0-9.]+) million'
revenue_re = re.compile(revenue_regex_string)
revenue_special_cases = ['less than $500,000', 'over $1 billion', 'over $500 million']

def find_bad_revenue(val):
    if pd.isnull(val):
       return None
    if type(val) is str:
        m = re.match(revenue_re, val.lower())
        if m is None:
            for rsc in revenue_special_cases:
                if val.lower() == rsc:
                    return None
            return val
    else:
        return val

def is_valid_revenue(val):
    if pd.isnull(val):
        return False
    if type(val) is str:
        m = re.match(revenue_re, val.lower())
        if m is not None:
            return True
        else:
            for rsc in revenue_special_cases:
                if val.lower() == rsc:
                    return True
            return False
    return False
        

## filter for valid states
    
statevals = set(us_geonames['state_abbrev'].values)

def find_bad_state(val):
    if pd.isnull(val):
        return None
    if type(val) is not str:
        return val
    if val not in statevals:
        return val
    return None

def is_valid_state(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    if val not in statevals:
        return False
    return True

## filter for valid zip codes
    
zipvals = set(us_geonames['zip'].astype(int).values)

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
        if int(val) in zipvals:
            return True
    else:
        return False

is_valid = {
    'city': is_valid_city,
    'name': is_valid_name,
    'phone': is_valid_phone,
    'revenue': is_valid_revenue,
    'state': is_valid_state,
    'zip': is_valid_zip,
}