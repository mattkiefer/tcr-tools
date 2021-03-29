import requests

### START CONFIG ###
# tamu
tamu_base_url         = 'https://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V04_01.aspx?'
tamu_rev_geo_base_url = 'https://geoservices.tamu.edu/Services/ReverseGeocoding/WebService/v04_01/Rest/?' 
tamu_api_key          = '058b7ce62ad64541b21d08264187bf72'
response_format       = 'json'
census                = 'false'
not_store             = 'false'
version               = '4.01'

# tribapps
tribapps_base_url     = 'http://boundaries.tribapps.com/1.0/boundary/?contains='

### END CONFIG ###

api               = '&apikey=' + tamu_api_key
response_format_q = '&format=' + response_format
census_q          = '&census=' + census
not_store_q       = '&notStore=' + not_store
version_q         = '&version=' + version
s                 = requests.Session()

def get_lat_lon(address='',city='',state='',zip='',debug=False,qual_type_reqs=['StreetSegmentInterpolation']):
    """
    get lat, lon pairs
    from posting address stuff to
    Texas A&M
    """
    # assemble query string
    address           = 'streetAddress=' + address.replace(' ','%20')
    city              = '&city=' + city.replace(' ','%20') if city else ''
    state             = '&state=' + state if state else ''
    zip               = '&zip=' + zip if zip else ''
    query_string      = tamu_base_url + address + city + state + zip + api + response_format_q + census_q + not_store_q + version_q
    print query_string
    latitude, longitude = None, None
    # get request
    try:
        results_j = s.get(query_string).json()
        if results_j:
            results_count = int(results_j['FeatureMatchingResultCount'])
        if results_count == 1:
            geocode = results_j['OutputGeocodes'][0]['OutputGeocode']
            qual_type = geocode['NAACCRGISCoordinateQualityType']
            # results should be specific to a certain geographic level, if specified
            if qual_type in qual_type_reqs or not qual_type_reqs:
                latitude = geocode['Latitude']
                longitude = geocode['Longitude']
    except Exception, e:
        print 'geocode failed:', address, city, state, e
    if debug and (not latitude or not longitude):
        import ipdb; ipdb.set_trace()
    return latitude, longitude

def get_city(zip=None,qual_type_reqs=[]):
    lat, lon = get_lat_lon(zip=zip,qual_type_reqs=qual_type_reqs)
    lat = 'lat=' + lat if lat else ''
    lon = '&lon=' + lon if lon else ''
    query_string = tamu_rev_geo_base_url + lat + lon + api + response_format_q + not_store_q + version_q
    print query_string
    results_j = s.get(query_string).json()
    if results_j.get('StreetAddresses') and len(results_j['StreetAddresses']) == 1:
        return results_j.get('StreetAddresses')[0]['City']

def get_tribapps_boundaries(lat=None,lon=None,boundary_sets=[]):
    """
    docs: http://boundaries.tribapps.com/api/
    sets: http://boundaries.tribapps.com/1.0/boundary-set/
        [
         '2010-police-areas',
         '2010-police-beats',
         '2010-police-districts',
         '2012-wards',
         'census-places',
         'census-tracts',
         'community-areas',
         'conservation-areas',
         'cook-county-board-of-commissioners-districts',
         'cook-county-board-of-review-districts',
         'cook-county-fire-protection-tax-districts',
         'cook-county-library-tax-districts',
         'cook-county-municipal-wards',
         'cook-county-park-tax-districts',
         'cook-judicial-subcircuits',
         'counties',
         'county-subdivisions',
         'dupage-county-board-districts',
         'elementary-school-districts',
         'empowerment-zones',
         ...
        ]
    TODO: get more boundary-sets documented:
    http://boundaries.tribapps.com/1.0/boundary-set/?limit=20&offset=20
    """
    req_url = tribapps_base_url + str(lat) + ',' + str(lon) + '&sets=' + ','.join(boundary_sets)
    print req_url
    results = s.get(req_url).json()
    return results
