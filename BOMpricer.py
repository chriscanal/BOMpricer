#!/usr/bin/python

#This file was written by Chris Canal for iRobot
#If you have any questions or need help with
#a similair script, please contact me at
#chriscanal@chriscanal.com

#Import dependencies
import requests
import json
from pprint import pprint
from xml.dom import minidom
from urllib2 import urlopen
import pprint

#Establish Global variables needed for making
#POST requests to the ECIA Authorized server
#via the ECIA's API.
Company_ID = 'iRobot'
API_Key = '8e2b4c56-05aa-4ce9-82dc-be9a660bb1ea'
endpoint = 'http://inventory.api.eciaauthorized.com/api/Search/Query'

#Part Queries from any iRobot BOM
query_params =  {
    "CompanyID": "iRobot",
    "APIKey": "8e2b4c56-05aa-4ce9-82dc-be9a660bb1ea",
    "CountryCode": "",
    "CurrencyCode": "",
    "InStockOnly": "false",
    "ExactMatch": "false",
    "Queries": [
        {
            "SearchToken": "rf202"
        }
    ]
}
header =  { 'Content-Type': 'application/json'}

#The request to the ECIA server
response = requests.post(endpoint, data = json.dumps(query_params), headers= header)

#Parsing the response. The data is contained
#in a attribute of the response called 'content'
#response.content is a string
data = response.content

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

#Changes data from string to python dictionary
decodedData = json.loads(data, object_hook=_decode_dict)
