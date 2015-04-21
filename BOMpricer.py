#!/usr/bin/python

#This file was written by Chris Canal for iRobot
#If you have any questions or need help with
#a similair script, please contact me at
#chriscanal@chriscanal.com

#Got some help with parsing Json from:
#http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

#Import dependencies
import requests
import json
import pprint
import sys
import urllib2
import csv
import time
from random import randint
from pprint import pprint
from xml.dom import minidom


#--------Methods Section------------#

#This method gets the data from the CSV file and returns it
def getPartData(fileLocation):
    out = open(fileLocation,"rb")
    CSVdata = csv.reader(out, skipinitialspace=False)
    CSVdata = [row for row in CSVdata]
    out.close()
    return CSVdata

#This method compares 1 part from the BOM to 1 Part from
#the ECIA authorized search, and returns the best price
def

#This method creates an empty part and returns it
def createNewPart():
    newPart = {
        'Compliance': {
            'RoHS': [
                {
                    'Description': 'None',
                    'IsCompliant': 'None',
                    'Region': 'None'
                }
            ]
        },
        'Description': 'None',
        'DistributorPartNumber': 'None',
        'Links': [
            {
                'Type': 'None',
                'Url': 'None'
            },
            {
                'Type': 'None',
                'Url': 'None'
            }
        ],
        'Manufacturer': 'None',
        'PartNumber': 'None',
        'Pricing': {
            'CurrencyCode': 'None',
            'MinimumQuantity': 'None',
            'Prices': [
                {
                    'Amount': 'None',
                    'FormattedAmount': 'None',
                    'Quantity': 'None',
                    'Text': 'None'
                }
            ],
            'QuantityMultiple': 'None'
        },
        'Stock': {
            'Availability': 'None',
            'QuantityOnHand': 'None'
        }
    }
    return newPart



#Json Parsing methods: These next two methods pars the
#json and make sure that it is no longer in unicode format
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


#--------API Server Request Section------------#

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

#Changes data from string to python dictionary
decodedData = json.loads(data, object_hook=_decode_dict)
partData = (((((decodedData['PartResults'])[0])['Distributors'])[0])['DistributorResults'])

#--------Compare Excel-BOM Requirements to Search Results------------#
