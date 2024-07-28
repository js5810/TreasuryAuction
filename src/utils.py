import re


def extract_time_units(input_string):
    pattern = r'(?P<years>\d+)-Year|(?P<months>\d+)-Month|(?P<weeks>\d+)-Week|(?P<days>\d+)-Day' # regex pattern to match "x-Year", "x-Month", "x-Week", "x-Day"
    matches = re.finditer(pattern, input_string)
    times = {'Year': None, 'Month': None, 'Week': None, 'Day': None}
    for match in matches:
        if match.group('years'):
            times['Year'] = int(match.group('years'))
        if match.group('months'):
            times['Month'] = int(match.group('months'))
        if match.group('weeks'):
            times['Week'] = int(match.group('weeks'))
        if match.group('days'):
            times['Day'] = int(match.group('days'))
    
    return times
