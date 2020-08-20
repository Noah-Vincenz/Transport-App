from flask import session
import requests
import config
import os
import time 
from item import Item

key = config.key
api_id = config.api_id

def get_items():
    """
    Fetches all cards from Trello.

    Returns:
        list: The list of cards constructed using the Card class.
    """
    url1 = "http://api.postcodes.io/postcodes/NW51TL"
    location_details = requests.request("GET", url1).json()
    longitude = location_details['result']['longitude']
    latitude = location_details['result']['latitude']

    url2 = "http://transportapi.com/v3/uk/places.json?lat={}&lon={}&type=bus_stop&api_key={}&app_id={}".format(latitude, longitude, key, api_id)

    members = requests.request("GET", url2).json()['member']
    first_member_atcocode = members[0]['atcocode']
    second_member_atcocode = members[1]['atcocode']

    url3 = "http://transportapi.com/v3/uk/bus/stop/{}/live.json?api_key={}&app_id={}".format(first_member_atcocode, key, api_id)
    url4 = "http://transportapi.com/v3/uk/bus/stop/{}/live.json?api_key={}&app_id={}".format(second_member_atcocode, key, api_id)

    bus_stop1 = requests.request("GET", url3).json()
    stop_departures1 = bus_stop1['departures']
    stop_name1 = bus_stop1['name']
    
    bus_list1 = []
    for departure in stop_departures1.values():
        for bus in departure:
            bus_list1.append(Item(bus['line'], bus['expected_departure_time'], bus['direction']))


    bus_stop2 = requests.request("GET", url4).json()
    stop_departures2 = bus_stop2['departures']
    stop_name2 = bus_stop2['name']

    bus_list2 = []
    for departure in stop_departures2.values():
        for bus in departure:
            bus_list2.append(Item(bus['line'], bus['expected_departure_time'], bus['direction']))

    sorted_list1 = sorted(bus_list1, key=lambda bus: bus.estimated_dep_time)

    # sorted_list1 = sorted((time.strptime(d, "%H:%M:%S") for d in time_list), reverse=True)

    sorted_list2 = sorted(bus_list2, key=lambda bus: bus.estimated_dep_time)

    map1 = {'name': stop_name1, 'bus_list': sorted_list1}
    map2 = {'name': stop_name2, 'bus_list': sorted_list2}
    return [map1, map2]


def get_list_name(card_id):
    """
    Gets the list name a specific card is in, based on the card's id.

    Returns:
        string: The list's name.
    """
    url = "https://api.trello.com/1/cards/{}/list".format(card_id)
    query = {
        'key': key,
        'token': token
    }
    list = requests.request("GET", url, params=query)
    return list.json()['name']


def create_item(title, description):
    """
    Creates a card in the TO DO list of the board.

    Returns:
        Card: The newly created Card object.
    """
    url = "https://api.trello.com/1/cards"
    query = {
        'key': key,
        'token': token,
        'name': title, 
        'desc': description,
        'pos': len(get_items()) + 1, 
        'idList': '5f2977346edfad5675e78f48' # this is the id for the 'To Do' list
    }
    card = requests.request("POST", url, params=query)
    return card


def complete_item(item_id):
    """
    Moves a card to the 'DONE' list of the board.
    """
    id_list = "5f297734a916318df131886e" # this is the id for the 'Done' list
    url = "https://api.trello.com/1/cards/{}".format(item_id)
    query = {
        'key': key,
        'token': token,
        'idList': id_list
    }
    requests.request("PUT", url, params=query)


def undo_item(item_id):
    """
    Moves a card to the 'TODO' list of the board.
    """
    id_list = '5f2977346edfad5675e78f48' # this is the id for the 'To Do' list
    url = "https://api.trello.com/1/cards/{}".format(item_id)
    query = {
        'key': key,
        'token': token,
        'idList': id_list
    }
    requests.request("PUT", url, params=query)