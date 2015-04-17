#!/usr/bin/python
import requests
import json
from pprint import pprint
from xml.dom import minidom
from urllib2 import urlopen
import pprint

Company_ID = 'iRobot'
API_Key = '8e2b4c56-05aa-4ce9-82dc-be9a660bb1ea'
endpoint = 'http://inventory.api.eciaauthorized.com/api/Search/Query'

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
oral =  { 'Content-Type': 'application/json'}
#print query_params
#print json.dumps(query_params)
response = requests.post(endpoint, data = json.dumps(query_params), headers= oral)
#print vars(response)
#print "The request.get just ran"
data = response.json
#print "The response.json just ran"
pprint.pprint(data)
#print "The pprint just ran"
