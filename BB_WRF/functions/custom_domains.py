# Dictionary with information for various subdomains
# Created by Brian Blaylock
# November 19, 2015


def get_domain(this_one):
    """
    A dictionary of various subdomains which includes information
    like the subdomin's name, bottom left lat/lon, top right lat/lon
    for plotting purposes. Also includes other info that may
    be useful when working with WRF or HRRR data such as 
    a thin amount for thining out wind barbs and the desired units
    or map projection.
    
    It is easy to add a new subdomain. Simply copy and paste one
    of the subdomains as a template and change the name and
    lat/lon coordinates as desired.
    
    Input
        this_one: the map_domain you wish to get. If this_one='all' then the
        entire dictionary is returned.
    Return
        The dictionary for the specified subdomain.
        Example demonstrated below, or run this script in the terminal.
    """


    domains = {
    'uintah_basin': {
                    'map_domain'    :'Uintah_Basin',                
                    'name'          :'Uintah Basin',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :3,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :39.73,                
                    'bot_left_lon'  :-111.,
                    'top_right_lat' :41.,                
                    'top_right_lon' :-109.
                    },
    'salt_lake_valley': {
                    'map_domain'    :'Salt_Lake_Valley',
                    'name'          :'Salt Lake Valley',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.4,
                    'bot_left_lon'  :-112.19785,
                    'top_right_lat' :40.9,
                    'top_right_lon' :-111.60
                    },
    'great_salt_lake': {
                    'map_domain'    :'Great_Salt_Lake',
                    'name'          :'Great Salt Lake',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.492346,
                    'bot_left_lon'  :-113.25,
                    'top_right_lat' :41.858304,
                    'top_right_lon' :-111.753761
                    },
    'great_salt_lake_cut': { # cut area for Summer 2015 lake size
                    'map_domain'    :'Great_Salt_Lake',
                    'name'          :'Great Salt Lake',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.492346,
                    'bot_left_lon'  :-113.75,
                    'top_right_lat' :41.858304,
                    'top_right_lon' :-111.853761
                    },                    
    'utah_valley': {
                    'map_domain'    :'Utah_Valley',
                    'name'          :'Utah Valley',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.001550,
                    'bot_left_lon'  :-111.901389,
                    'top_right_lat' :40.451040,
                    'top_right_lon' :-111.501889
                    },
    'utah_lake': {
                    'map_domain'    :'Utah_Lake',
                    'name'          :'Utah Lake',
                    'map_projection':'cyl',
                    'units'         :'mph',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.,
                    'bot_left_lon'  :-111.951,
                    'top_right_lat' :40.375,
                    'top_right_lon' :-111.65
                    },
    'bear_lake': {
                    'map_domain'    :'Bear_Lake',
                    'name'          :'Bear Lake',
                    'map_projection':'cyl',
                    'units'         :'mph',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'bot_left_lat'  :41.826247,
                    'bot_left_lon'  :-111.455473,
                    'top_right_lat' :42.153301,
                    'top_right_lon' :-111.189903
                    },
    'full_utah': {
                    'map_domain'    :'Full_Utah',
                    'name'          :'Utah',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :7,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :36.5,
                    'bot_left_lon'  :-114.5,
                    'top_right_lat' :42.5,
                    'top_right_lon' :-108.5
                    },
    'cache_valley': {
                    'map_domain'    :'Cache_Valley',
                    'name'          :'Cache Valley',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :41.228045,
                    'bot_left_lon'  :-112.278722,
                    'top_right_lat' :41.99730,
                    'top_right_lon' :-111.535024
                    },
    'moses_lake': {
                    'map_domain'    :'Moses_Lake',
                    'name'          :'Moses Lake (WA)',
                    'map_projection':'cyl',
                    'units'         :'mph',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :7,
                    'bot_left_lat'  :47.050935,
                    'bot_left_lon'  :-119.403803,
                    'top_right_lat' :47.193245,
                    'top_right_lon' :-119.252493
                    },
    'full_HRRR': {
                    'map_domain'    :'Full_HRRR',
                    'name'          :'HRRR',
                    'map_projection':'lcc',
                    'units'         :'m/s',
                    'thin'          :30,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'ref_lat'       :38.5,  # Requires plotting on lcc projection
                    'ref_lon'       :-97.5,
                    'truelat1'      :38.5,
                    'truelat2'      :38.5,
                    'stand_lon'     :-97.5
                    }
    }
    
    if this_one == 'all':
        return domains
    else:
        return domains[this_one]


#---------------------------------------------------------
#---------------------------------------------------------

    
if __name__ == "__main__":
    
    print ""
    print "Available Subdomains"
    all_doms = get_domain('all')
    for i in all_doms:
        print "  ", i

    print ""
    domain = get_domain('salt_lake_valley')
    print 'Domain Name: ', domain['name']    
    print "Available keys:"
    for i in domain:
        print "  ", i    

    print ""
    print get_domain('all')
    print ""

    print domain
    print domain.keys()
    print ""
    
    ## Draw some subdomains on a map...
    from mpl_toolkits.basemap import Basemap    
    bot_left_lon = get_domain('full_utah')['bot_left_lon']
    bot_left_lat = get_domain('full_utah')['bot_left_lat']    
    top_right_lon = get_domain('full_utah')['top_right_lon']    
    top_right_lat = get_domain('full_utah')['top_right_lat']    
    m = Basemap(resolution='i',area_thresh=10.,projection='cyl',\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    
    m.drawstates(color='k', linewidth=.8)
    m.drawcoastlines()
    m.drawcounties()
    m.fillcontinents()
    #Plot Subdomains (Salt Lake Valley, Utah Lake, etc...)
    for area in ['salt_lake_valley','utah_valley','cache_valley','uintah_basin','bear_lake']:    
        domain = get_domain(area)
        toprightlat = domain['top_right_lat']
        topleftlat = domain['top_right_lat']
        toprightlon = domain['top_right_lon']
        topleftlon = domain['bot_left_lon']
        botrightlat = domain['bot_left_lat']
        botrightlon = domain['top_right_lon']
        botleftlat = domain['bot_left_lat']
        botleftlon = domain['bot_left_lon']
        
        m.drawgreatcircle(toprightlon,toprightlat,topleftlon,topleftlat, color='#FFFF4C', linewidth='3')
        m.drawgreatcircle(topleftlon,topleftlat,botleftlon,botleftlat, color='#FFFF4c', linewidth='3')
        m.drawgreatcircle(botleftlon,botleftlat,botrightlon,botrightlat, color='#FFFF4c', linewidth='3')
        m.drawgreatcircle(botrightlon,botrightlat,toprightlon,toprightlat, color='#FFFF4c', linewidth='3')

    
    
    
