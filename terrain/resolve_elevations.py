# encoding: utf-8
"""Resolve Metadata QC Issues"""

import ConfigParser
import getopt
import json
import sys
import urllib

import lib.one_km_dem as oneKm
from lib.google_elev import get_elev_from_google as gelev
from lib.mesonet_api import get_binned_stations
from lib.srtm import get_srtm_30m_elev, open_granule_30m


# =============================================================================
srtm_path_30m = '../DATASETS/SRTMv3'
# =============================================================================



# Read in configuration settings, keeping global since at least
# two functions are using it
CONFIG = ConfigParser.ConfigParser()
CONFIG.read('./config.conf')


def calc_stats(hits, misses):
    """Calculate the basic stats of hits vs. misses"""
    try:
        result = (float(misses) / float(hits)) * 100.0
    except ZeroDivisionError:
        if misses == 0:
            result = 0.0
        else:
            result = 100.0
    return result


def resolve_delta(obj):
    """Second guess attempt to resolve differences between API and truth"""
    # This is where we should add follow-up tests for corrections

    _node = obj['node']

    # Try and resolve with Google's elevation service.
    resolve_with_google = False
    if CONFIG.get("GOOGLE", "resolve_with_google") == "yes":
        resolve_with_google = True

    if resolve_with_google is True:
        obj['resolved_elev'] = gelev(float(_node['LATITUDE']), float(_node['LONGITUDE']))
        obj['resolve_method_used'] = "google_elevation_service"
        obj['delta_api'] = obj['api_elev'] - obj['resolved_elev']

    # Re-evaluate the station again, if we fail then make a new node and return
    if obj['delta_api'] > obj['delta_limit']:

        # For the user
        print "For " + _node['STID'] + ": " + \
            str(obj['api_elev']) + ", " + str(obj['resolved_elev']) \
            + " -> " + str(obj['delta_api']) + " in Ft! (" + \
            obj['resolve_method_used'] + ")"

        # Populate a new node in the delinquent stations dictionary
        key_to_add = {
            "stid": _node['STID'],
            "latitiude": _node['LATITUDE'],
            "longitude": _node['LONGITUDE'],
            "api_elev": obj['api_elev'],
            "resolved_elev": obj['resolved_elev'],
            "delta_api": obj['delta_api'],
            "resolve_method_used": obj['resolve_method_used']
        }
        return key_to_add

    # Send nothing back
    return None


def main(network_id):
    """Resolve Elevations"""

    # Let's do this!
    print "Resolving Mesonet elevations for network (" + str(network_id) + ")"

    # Retrieve a query (by network) from the API and then process the
    # elevation heights in terms of each granule.
    sorted_stations = get_binned_stations(network_id)
    onekm_data = oneKm.open_granule_1km(CONFIG.get('DATASETS', 'onekm_path'))
    delta_limit = int(CONFIG.get('RUNTIME', 'elevation_err'))

    print "Elevation error set to " + str(delta_limit) + " ft."
    print ""

    stations_to_investigate = dict()
    resolve_method_used = ""

    # These are for the statistics, not really needed
    total_hits = 0

    onekm_hits = 0
    onekm_fails = 0

    srtm_hits = 0
    srtm_fails = 0

    # Ideally we can loop over the stations that are group together
    # in the histogram bins.
    for granule in sorted_stations:
        srtm_data = open_granule_30m(granule)

        # Check to see if the SRTMv3 granule came back good, if not
        # we need to use our 1km DEM file.
        if srtm_data is None:
            # We have to use the 1km dataset, Poo!
            for node in sorted_stations[granule]:
                resolved_elev = oneKm.get_elev_from_1km(float(node['LATITUDE']), float(node['LONGITUDE']), onekm_data)

                api_elev = float(node['ELEVATION'])
                delta_api = api_elev - resolved_elev
                resolve_method_used = "1km_dem"
                onekm_hits = onekm_hits + 1
                total_hits = total_hits + 1

                delta_api = api_elev - resolved_elev
                if delta_api > delta_limit:
                    onekm_fails = onekm_fails + 1
                    result = resolve_delta({
                        "node": node,
                        "api_elev": api_elev,
                        "resolved_elev": resolved_elev,
                        "delta_api": delta_api,
                        "delta_limit": delta_limit,
                        "resolve_method_used": resolve_method_used,
                        "onekm_hits": onekm_hits,
                        "srtm_hits": srtm_hits
                    })

                    if result is not None:
                        stations_to_investigate[result['stid']] = result


        else:
            # We're going to use the 30m granules, Yay!
            srtm_data = srtm_data.transpose() * 3.28084 # Convert units, m->ft
            for node in sorted_stations[granule]:
                resolved_elev = get_srtm_30m_elev(float(node['LATITUDE']), float(node['LONGITUDE']), srtm_data)

                api_elev = float(node['ELEVATION'])
                resolve_method_used = "30m_dem"
                srtm_hits = srtm_hits + 1
                total_hits = total_hits + 1

                delta_api = api_elev - resolved_elev
                if delta_api > delta_limit:
                    srtm_fails = srtm_fails + 1
                    result = resolve_delta({
                        "node": node,
                        "api_elev": api_elev,
                        "resolved_elev": resolved_elev,
                        "delta_api": delta_api,
                        "delta_limit": delta_limit,
                        "resolve_method_used": resolve_method_used,
                        "onekm_hits": onekm_hits,
                        "srtm_hits": srtm_hits
                    })

                    if result is not None:
                        stations_to_investigate[result['stid']] = result

    # Save to file
    filedir = "./results/"
    filename = filedir + "stations_to_investigate_network_" + str(network_id) + ".json"
    with open(filename, 'w') as file_out:
        json.dump(stations_to_investigate, file_out, sort_keys=True, indent=4)

    onekm_failure = calc_stats(onekm_hits, onekm_fails)
    srtm_failure = calc_stats(srtm_hits, srtm_fails)

    print ""
    print "Stats (hits vs. misses)"
    print "-----------------------"
    print "Total Stations evaluated: " + str(total_hits)
    print "30m DEM: " + str(srtm_hits) + "/" + str(srtm_fails) \
          + " = " + '{:.2f}'.format(srtm_failure) + " % resolve failures"
    print "1km DEM: " + str(onekm_hits) + "/" + str(onekm_fails) \
          + " = " + '{:.2f}'.format(onekm_failure) + " % resolve failures"
    print ""

    return 0

if __name__ == "__main__":
    # Get user arguments
    try:
        network_id = None
        opts, args = getopt.getopt(sys.argv[1:], "n", ["network="])
    except getopt.GetoptError as err:
        # Print help information and exit:
        print str(err)
        sys.exit(2)
    for o, a in opts:
        if o in ("-n", "--network"):
            network_id = a
        else:
            assert False, "unhandled option"
            print args

    if network_id is None:
        # Need to bail out!
        print "Network ID required. -n --network="
        sys.exit(2)
    elif network_id == 'all':
        # get a list of network id's
        base_url = 'https://api.mesowest.net/v2/networks?'
        api_parameters = {'token': 'yo'}

        # Construct and return the Mesonet API query
        request = base_url + urllib.urlencode(api_parameters)
        response = json.loads(urllib.urlopen(request).read())

        list_of_networks = []
        for item in response['MNET']:
            list_of_networks.append(int(item['ID']))

        # Do this so we could dig out stat if we want them.
        for netid in sorted(list_of_networks):
            main(netid)
    else:
        main(network_id)
