from flask import session
import requests
import config
import os
import time 
from bus import Bus

key = config.key
api_id = config.api_id

def get_stops():
    """
    Given a postcode this fetches live bus times for the two closest bus stops using Transport API.

    Returns:
        
    """
    location = get_location("NW51TL")
    longitude, latitude = location[0], location[1]
    stop_atcocodes = get_closest_stop_atcocodes(latitude, longitude)
    first_stop_atcocode = stop_atcocodes[0]
    second_stop_atcocode = stop_atcocodes[1]
    bus_stop1 = get_stop_from_atcocode(first_stop_atcocode)
    stop_name1 = bus_stop1[0]
    stop_departures1 = bus_stop1[1]
    bus_stop2 = get_stop_from_atcocode(second_stop_atcocode)
    stop_name2 = bus_stop2[0]
    stop_departures2 = bus_stop1[1]
    bus_list1 = get_bus_list(stop_departures1)
    bus_list2 = get_bus_list(stop_departures2)
    map1 = {'name': stop_name1, 'bus_list': bus_list1}
    map2 = {'name': stop_name2, 'bus_list': bus_list2}
    return [map1, map2]


def get_location(postcode):
    url = "http://api.postcodes.io/postcodes/{}".format(postcode)
    location_details = requests.request("GET", url).json()
    longitude = location_details['result']['longitude']
    latitude = location_details['result']['latitude']
    return [longitude, latitude]


def get_closest_stop_atcocodes(latitude, longitude):
    url = "http://transportapi.com/v3/uk/places.json?lat={}&lon={}&type=bus_stop&api_key={}&app_id={}".format(latitude, longitude, key, api_id)
    members = requests.request("GET", url).json()['member']
    first_member_atcocode = members[0]['atcocode']
    second_member_atcocode = members[1]['atcocode']
    return [first_member_atcocode, second_member_atcocode]


def get_stop_from_atcocode(atcocode):
    url = "http://transportapi.com/v3/uk/bus/stop/{}/live.json?api_key={}&app_id={}".format(atcocode, key, api_id)
    bus_stop = requests.request("GET", url).json()
    return[bus_stop['name'], bus_stop['departures']]


def get_bus_list(stop_departures):
    bus_list = []
    for departure in stop_departures.values():
        for bus in departure:
            bus_list.append(Bus(bus['line'], bus['expected_departure_time'], bus['direction']))
    return sorted(bus_list, key=lambda bus: bus.estimated_dep_time)