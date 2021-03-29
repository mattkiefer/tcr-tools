"""
Given table, get
data by community
area report
"""
import requests, csv, math, os

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

### START CONFIG ###
variable_metadata_path   = dir_path + 'variables.csv' # from acs api docs
tract_ca_map_loc         = dir_path + 'CensusTractsTIGER2010.csv' # from data portal
tract_ca_map_tract_field = 'TRACTCE10'
tract_ca_map_ca_field    = 'COMMAREA'
ca_name_number_map_loc   = dir_path + 'hardship.csv' # from data portal
base                     = 'https://api.census.gov/data/'
year                     = '2014'
#dataset                  = '/acs5' # see https://census.gov/content/dam/Census/data/developers/acs/Guide%20to%20the%20ACS%20API%20Updates%20to%20the%20Character%20and%20Numeric%20Data%20Variables.pdf?eml=gd&utm_medium=email&utm_source=govdelivery
dataset                  = '/acs/acs5'
tract                    = '*' # all
state                    = '17' # Illinois
county                   = '031' # Cook
key                      = 'd182265a1eea731fd4de2ef89b9f2f0163c95822'
max                      = 49 # can't request 50 tables from API
ca_geography_path        = dir_path + 'CommAreas.csv' 
geo                      = False # include geometries?
moe                      = False # include margins of error?
table                    = '' 
output_dir               = '/tmp/'
### END CONFIG ###

s = requests.Session()

def setup_ca_name_map():
    """
    return a dict with
    community area
    IDs keyed to names
    """
    ca_name_number_map = open(ca_name_number_map_loc)
    ca_name_number_csv = csv.DictReader(ca_name_number_map)
    return dict((x['Community Area Number'],x['COMMUNITY AREA NAME']) for x in ca_name_number_csv)


def setup_tract_ca_map():
    """
    return a dict with
    tracts keyed to community
    area IDs
    """
    tract_ca_map = open(tract_ca_map_loc)
    tract_ca_csv = csv.DictReader(tract_ca_map)
    return dict((fix_tract_no(x[tract_ca_map_tract_field]),x[tract_ca_map_ca_field]) for x in tract_ca_csv)


def fix_tract_no(tract):
    """
    fix census tracts so
    that five-character IDs
    get leading zero
    """
    if len(tract) == 5:
        tract = '0' + tract
    if len(tract) == 6:
        return tract


def aggregate_cas(payloads,table):
    """
    given a payload,
    return a dict of CAs
    tallying values

    ex:
        {
         # community area
         'Albany Park': {
                         'ca_number'  : 1,
                         # census variable
                         'B08124_001E': {
                                         # tract : value
                                         '010100': 123,
                                         '010200': 456,
                                         '010300': 789,
                                        },
                         'B08124_001M': {
                                         '010100': 987,
                                         '010200': 654,
                                         '010300': 321,
                                        }
                        },
         
         'Archer Heights': ...
        }

    """
    cas = {}
    # multiple API calls require collect all headers in one set
    all_headers = set() 
    # we have support multiple payloads due to api limitations
    for payload in payloads:
        # first row of the payload is headers
        headers = payload[0]
        # table_headers specify the actual data points, i.e. those fields with table name in header
        table_headers = [x for x in headers if table in x]
        for table_header in table_headers:
            # build this set this to get table schema for final output file
            all_headers.add(table_header)
        for row in payload[1:]: # skip the first header row
            row_dict = dict(zip(headers,row))
            tract = row_dict['tract'] 
            if tract not in tract_ca_map: 
                # skip suburban Cook 
                continue
            # get the community area name where this tract belongs ...
            ca = ca_name_map[tract_ca_map[tract]]
            ca_number = tract_ca_map[tract]
            # ... and add all the data to this dict.
            if ca not in cas:
                cas[ca] = {'ca_number': ca_number}
            # finally, check if this data variable is keyed in the community area ...
            for table_header in table_headers:
                if table_header not in cas[ca]:
                    # ... and add it if it's not.
                    cas[ca][table_header] = {}
                    #cas[ca][table_header] = []
                # add this tract's value to the list keyed by CA, variable
                if row_dict[table_header]: # can't do math with NoneTypes
                    #cas[ca][table_header].append(int(row_dict[table_header]))
                    try:
                        cas[ca][table_header][tract] = int(row_dict[table_header])
                    except Exception, e:
                        print e
                        import ipdb; ipdb.set_trace()
    return cas, list(all_headers)


def get_child_tables(table):
    """
    return list(s) of the
    tables parented to the
    specified table
    """
    batches = []
    table_list = []
    child_tables = sorted([x for x in variable_metadata.keys() if table in x])
    # skip margin of error fields
    if not moe: child_tables = [x for x in child_tables if x[-1] != 'M']
    for child_table in child_tables:
        table_list.append(child_table)
        # api will only take 50 variables so we have to batch them
        if len(table_list) == max:
            batches.append(','.join(table_list))
            table_list = []
    if table_list:# and not batches: # when less than 50 variables
        batches.append(','.join(table_list))
    return batches


def load_variable_metadata():
    """
    lookup table to
    get human-readable names
    for variable codes
    
    NOTE THAT YOU CAN GET THIS FROM API! e.g.:
    https://api.census.gov/data/2014/acs5/variables/B24011_001E.json
    """
    variable_metadata_file = open(variable_metadata_path)
    variable_metadata_csv = csv.DictReader(variable_metadata_file)
    return dict((x['Name'], x['Name'] + ': ' + x['Label']) for x in variable_metadata_csv)

variable_metadata = load_variable_metadata() # build lookup for variable IDs->label/concept metadata 

def build_outfile(cas, all_headers, output_dir, output_file):
    """
    write a csv
    of community area
    data with headers
    """
    # we're gonna swap out the ACS codes for human-readable headers via variable_metadata dict
    outfile_headers = ['Community Area ID', 'Community Area Name'] + [variable_metadata[x] for x in sorted(all_headers)]
    outfile_loc = output_dir + output_file
    if geo:
        outfile_headers.append('geo')
        outfile_loc += '_geo'
    if moe:
        outfile_loc += '_moe'
    outfile_loc += '.csv'
    outfile = open(outfile_loc,'w')
    outcsv = csv.DictWriter(outfile, outfile_headers)
    outcsv.writeheader()

    for ca in sorted(cas):
        # build a row for outputting
        row = {'Community Area Name': ca, 'Community Area ID': cas[ca]['ca_number']}
        # using all_headers because that's what's keyed in the cas dict ...
        # ... but we use variable_metadata to write the human-readable headers.
        for header in all_headers:
            # tract:value pairs for each community area, variable
            ca_var_tracts = cas[ca][header]
            variable_type = header[-1] # options: E, M, PE, PM
            # test to make sure this isn't a percent ... we don't support that yet
            percent = header[-2] == 'P'
            assert not percent, 'This data table is measured in percent and we do not support that yet'
            if variable_type == 'E': # this is a straight estimate (count), so we can sum it
                row[variable_metadata[header]] = sum(ca_var_tracts[x] for x in ca_var_tracts) or 'NA'
            elif variable_type == 'M': # this a margin of error ... do some math on it
                row[variable_metadata[header]] = moe(ca_var_tracts[x] for x in ca_var_tracts) or 'NA'
            if geo:
                row['geo'] = get_geo(row['Community Area ID'])
        outcsv.writerow(row)
    print 'outfile_loc =', outfile_loc
    outfile.close()


def get_geo(ca_number):
    """
    look up community
    area id to get
    its geography
    """
    return [x['the_geom'] for x in ca_geographies if x['AREA_NUMBE'] == ca_number][0]


def moe(vals):
    """
    do math to get the 
    margin of error grouped by
    larger geography
    """
    return int(round(math.sqrt(sum(x*x for x in vals)),0)) 


def init(table_arg=None, output_dir_arg=None): # TODO: rename args to exclude _arg suffix
    """
    initialize call
    to API, write data
    to file by CA
    """
    # go get all the variables related to this one by name/numbering convention
    # get table passed in as argument if any
    this_table = table_arg if table_arg else table
    batch = get_child_tables(this_table)
    payloads = []
    for tables in batch:
        # assemble an api request using configs above
        url = build_req_url(tables)
        print 'requesting', url 
        payload = s.get(url).json() 
        # collect multiple payloads to accomodate 50-variable API limit
        payloads.append(payload)

    # get data grouped by community area, plus headers
    cas, all_headers = aggregate_cas(payloads,this_table)

    this_output_dir = output_dir_arg + '/' if output_dir_arg else output_dir

    # write results to csv
    build_outfile(cas, all_headers, this_output_dir, this_table) 



def build_req_url(tables):
    """
    return url
    to request data from the 
    census API
    """
    return base + year + dataset + '?get=NAME,' + tables + '&for=tract:' + tract + '&in=state:' + state + '+county:' + county + '&key=' + key


# SETUP
# build lookups for tract->community area ID ...
tract_ca_map = setup_tract_ca_map()
# and community area ID->community area name.
ca_name_map = setup_ca_name_map()
# build lookup for CA_IDs->geographies
ca_geographies           = [x for x in csv.DictReader(open(ca_geography_path))]


if __name__ == '__main__':

    # API call and writeout
    init()
