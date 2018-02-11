import re
import pandas as pd

# load US geographical data, sourced from GeoNames.org
# Puerto Rico and Virgin Islands are referenced in data, make sure these are appended
col_names = ['zip', 'city', 'state', 'state_abbrev']
us_geonames = pd.read_csv('US.txt', sep='\t', usecols=[1,2,3,4], names=col_names)
puerto_rico_geonames = pd.read_csv('PR.txt', sep='\t', usecols=[1,2,3,4], names=col_names)
virgin_islands_geonames = pd.read_csv('VI.txt', sep='\t', usecols=[1,2,3,4], names=col_names)
us_geonames = us_geonames.append(puerto_rico_geonames).append(virgin_islands_geonames)

# load NACIS category code values
category_codes = pd.read_csv('NAICS_codes_2-6.csv', usecols=[1], names=['code'], skiprows=2, dtype=str).values.flatten().tolist()
catcode_re = re.compile('([0-9]{2})-([0-9]{2})')
for c in category_codes:
    if '-' in c: # faster than full regex match
        m = re.match(catcode_re, c)
        range_ends = list(map(int, m.groups()))
        category_codes += list(map(str, list(range(range_ends[0], range_ends[1] + 1))))
        category_codes.remove(c)
category_codes = set(category_codes)

## filter for valid names

bad_names = ['none', 'null', ' ']

def find_bad_name(val):
    if pd.isnull(val):
        return None
    if type(val) is not str:
        return val
    if val.lower() in bad_names:
        return val
    return None

def is_valid_name(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    if val.lower() in bad_names:
        return False
    return True

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

## filter for valid time in business - this is an easy one

def is_valid_time(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    return 'year' in val

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

## filter for valid category code

def find_bad_catcode(val):
    if pd.isnull(val):
        return None
    val = str(val)
    if len(val) < 8:
        return val
    else:
        testval = val[:-1]
        while True:
            if testval in category_codes:
                return None
            if len(testval) < 3:
                return val
            testval = testval[:-1]
    return None

def is_valid_catcode(val):
    if pd.isnull(val):
        return False
    val = str(val)[:6]
    while True:
        if val in category_codes:
            return True
        if len(val) < 3:
            return False
        val = val[:-1]
    return False

## filter for valid headcount

headcount_regex_string = '[0-9]+ to [0-9]+'
headcount_re = re.compile(headcount_regex_string)
headcount_special_cases = ['over 1,000']

def is_valid_headcount(val):
    if pd.isnull(val):
        return False
    if type(val) is not str:
        return False
    m = re.match(headcount_re, val)
    if m is not None:
        return True
    else:
        return val.lower() in headcount_special_cases
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
        


is_valid = {
    'name': is_valid_name,
    'address': is_valid_address,
    'city': is_valid_city,
    'state': is_valid_state,
    'zip': is_valid_zip,    
    'phone': is_valid_phone,
    'time_in_business': is_valid_time,
    'category_code': is_valid_catcode,
    'headcount': is_valid_headcount,
    'revenue': is_valid_revenue,
}