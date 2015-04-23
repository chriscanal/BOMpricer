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
import yaml

fileLocation = '/Users/christophercanal4/Desktop/SecondBomJohnfortier (1).csv'
outputFileLocation = "/Users/christophercanal4/Desktop/PriceAndQuantity.csv"

#--------Methods Section------------#
#This method gets the data from the CSV file and returns it
def getPartData(fileLocation):
    out = open(fileLocation,"rb")
    CSVdata = csv.reader(out, skipinitialspace=False)
    CSVdata = [row for row in CSVdata]
    out.close()
    return CSVdata

def findPartNumbersIndex(CSVdata):
    for x in range(0,CSVdata):
        for y in range(0, CSVdata[x]):
            if CSVdata[x][y] = "Part Number":
                return x, y

def findQuantityIndex(CSVdata):
    for x in range(0,CSVdata):
        for y in range(0, CSVdata[x]):
            if CSVdata[x][y] = "Quantity":
                return x, y

#--------Compare Excel-BOM Requirements to Search Results------------#

#Returns the length of the Parts
def lengthOfPartResults(decodedData):
    return len(decodedData['PartResults'])

#Returns the length of the Parts
def lengthOfDistributors(PartResults):
    return len(PartResults['Distributors'])

#Returns the length of the Parts
def lengthOfDistributorResults(Distributors):
    return len(Distributors['DistributorResults'])


#Check if BOM Part Number Matches Distributor Part number
def BOMPartNumberMatches(DistributorResults, BOMpartNumber):
    if DistributorResults['PartNumber'] = BOMpartNumber:
        return True

#This method creates an empty part and returns it
def createNewPart():
    newPart = {
        'lowestPrice':"N/A",
        'cutOffQuantity':"N/A",
        'links':"N/A",
        'Stock':"N/A",
        'Manufacturer':"N/A",
        'Vendor':"N/A"
    }
    return newPart

#Creates a new Part from searched data and
#prepares relevant data for writing to file
def newBestPart(currentPart, pricesIndex, vendor):
    newPart = {
        'lowestPrice': ((currentPart['Prices'])[pricesIndex])['Amount']),
        'cutOffQuantity': ((currentPart['Prices'])[pricesIndex])['Quantity']),
        'links': currentPart['Links'],
        'Stock': currentPart['Stock'],
        'Manufacturer':currentPart['Manufacturer'],
        'Vendor': vendor
    }
    return newPart


#Checks part prices from a given distributor
#and finds the best cutoff quantity price
#for the based on the quantity needed
def checkPricesAndQuantities(currentPart, bestPart, quantityNeeded, vendor):
    if ((currentPart['Stock'])[0])['QuantityOnHand'] > quantityNeeded:
        for y in range(0, len(currentPart['Prices']):
            if ((currentPart['Prices'])[y])['Quantity'] <= quantityNeeded:
                if (bestPart['lowestPrice'] = "N/A") or (bestPart['lowestPrice'] > ((currentPart['Prices'])[y])['Amount']):
                    bestPart = newBestPart(currentPart, y, vendor)
    return bestPart

#Iterates through all the data gathered from the
#API query and finds the cheapest part.
def findCheapestPart(decodedData, BOMpartNumber, quantityNeeded):
    bestPart = createNewPart()
    for i in range(0, lengthOfPartResults(decodedData)):
        PartResults = (decodedData['PartResults'])[i]
        for j in range(0, lengthOfDistributors(PartResults)):
            Distributors = (PartResults['Distributors'])[j]
            for k in range(0, lengthOfDistributorResults(Distributors)):
                DistributorResults = (Distributors['DistributorResults'])[k]
                if BOMPartNumberMatches(DistributorResults, BOMpartNumber):
                    bestPart = checkPricesAndQuantities(DistributorResults[k], bestPart, quantityNeeded, Distributors['Name'] )




#--------API Server Request Section------------#

def constructPartNumberArray(excelField):
    partNumberArray = []
    for x in range(0,len(excelField)):
        searchToken = {"SearchToken": excelField[x]}
        partNumberArray.extend(searchToken)
    return partNumberArray



def executeSearch(partNumber):
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
        "Queries": partNumber
    }

    header =  { 'Content-Type': 'application/json'}

    #The request to the ECIA server
    response = requests.post(endpoint, data = json.dumps(query_params), headers= header)

    #Parsing the response. The data is contained
    #in a attribute of the response called 'content'
    #response.content is a string
    data = response.content

    #Changes data from string to python dictionary
    decodedData = yaml.safe_load(data)
    reutrn decodedData


#--------API Server Request Section------------#

def main():
    CSVdata = getPartData(fileLocation)
    currentPart, partIndex = findPartNumbersIndex(CSVdata)
    
