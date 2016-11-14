# Brian Blaylock
# Version 2 update
# 14 November 2016

"""
Converts MesoWest date strings to python datetime objects
"""

def MWdate_to_datetime(x):
    """
    Converts a MesoWest date string to a python datetime object
    So far only works for summer months (daylight savings time). Best if you
    make all your MesoWest API calls in UTC time.

    For fastest calculations, vectorize this function before using:
    Example:
        vectorized_convert_time_function = np.vectorize(MWdate_to_datetime)
        DATES = vectorized_convert_time_function(dates)

    As my personal notation:
        DATES = list or array of python datetime object
        dates = native dates format, typically a string or number in epoch time
    """

    try:
        # print 'Times are in UTC'
        return datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')

    except:
        # print 'Times are in Local Time'
        return datetime.strptime(x, '%Y-%m-%dT%H:%M:%S-0600')
        