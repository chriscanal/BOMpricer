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
import pprint

fileLocation = '//Users/christophercanal4/GithubProjects/iRobot/BOMpricer/shortTest.csv'
outputFileLocation = "/Users/christophercanal4/Desktop/PriceAndQuantity.csv"

#--------Methods Section------------#
#This method gets the data from the CSV file and returns it
def getPartData(fileLocation):
    out = open(fileLocation,"rb")
    CSVdata = csv.reader(out, skipinitialspace=False)
    CSVdata = [row for row in CSVdata]
    out.close()
    return CSVdata

def writeObjectToFile(bestPrices):
    with open(outputFileLocation, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(bestPrices)

def formatSearchResults(searchData):
    formattedData = []
    formattedData.append(['Part Number','Lowest Price Found','Vendor','Buy Link','DataSheet Link','Amount in Stock','Manufacturer'])
    for x in range(0, len(searchData)):
        partNumber = searchData[x]['partNumber']
        lowestPrice = str(searchData[x]['lowestPrice'])
        vendor = searchData[x]['Vendor']
        buyLink = findBuyLink(searchData[x])
        datasheet = findDatasheetLink(searchData[x])
        stock = str(findStockAmount(searchData[x]['Stock']))
        manufacturer = searchData[x]['Manufacturer']
        formattedData.append([partNumber, lowestPrice, vendor, buyLink, datasheet, stock, manufacturer])
    print "-----------------Formatted Data-----------------"
    pprint.pprint(formattedData)
    return formattedData

def findBuyLink(partData):
    buyLink = "Not Found"
    if 'links' in partData:
        for x in range(0, len(partData['links'])):
            if partData['links'][x]['Type'] == 'Buy':
                buyLink = partData['links'][x]['Url']
    return buyLink



def findStockAmount(stockData):
    quantityOnHand = "unknown"
    if 'QuantityOnHand' in stockData:
        quantityOnHand = stockData['QuantityOnHand']
    return quantityOnHand



def findDatasheetLink(partData):
    datasheetLink = "Not Found"
    if 'links' in partData:
        for x in range(0, len(partData['links'])):
            if partData['links'][x]['Type'] == 'Datasheet':
                datasheetLink = partData['links'][x]['Url']
    return datasheetLink



##This Block finds strings in the CSV file that have the new line character and seperates them
def seperatePartNumbers(partNumberField):
    partNumbers = []
    index = 0
    newLine = partNumberField.find('\n', index)
    while newLine != -1:
            partNumbers.extend({partNumberField[index:newLine]})
            index = newLine+1
            newLine = partNumberField.find('\n', index)
    partNumbers.extend({partNumberField[index:]})
    return partNumbers


#Looks for where the partNumbers are in the CSV file
def findPartNumbersIndex(CSVdata):
    for x in range(0,len(CSVdata)):
        for y in range(0, len(CSVdata[x])):
            if CSVdata[x][y] == "Part Number":
                return x+1, y
    return 0,0

#Looks for where the quantityNeeded numbers are in the CSV file
def findQuantityIndex(CSVdata):
    for x in range(0,len(CSVdata)):
        for y in range(0, len(CSVdata[x])):
            if CSVdata[x][y] == "Quantity":
                return y
    return 0,0

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



#This method creates an empty part and returns it
def createNewPart():
    newPart = {
        'partNumber':"Not Found",
        'lowestPrice':"Not Found",
        'cutOffQuantity':"Not Found",
        'links':"Not Found",
        'Stock':"Not Found",
        'Manufacturer':"Not Found",
        'Vendor':"Not Found"
    }
    return newPart

#Creates a new Part from searched data and
#prepares relevant data for writing to file
def newBestPart(currentPart, pricesIndex, vendor):
    newPart = {
        'partNumber': currentPart['PartNumber'],
        'lowestPrice': (((currentPart['Pricing']['Prices'])[pricesIndex])['Amount']),
        'cutOffQuantity': (((currentPart['Pricing']['Prices'])[pricesIndex])['Quantity']),
        'links': currentPart['Links'],
        'Stock': currentPart['Stock'],
        'Manufacturer': testForManufacturer(currentPart),
        'Vendor': vendor
    }
    return newPart
def testForManufacturer(part):
    if 'Manufacturer' in part:
        if part['Manufacturer'] != None:
            return part['Manufacturer']
    return "Not Found"

#Check if BOM Part Number Matches Distributor Part number
#Only matches half of the part number for less strict search
def BOMPartNumberMatches(DistributorResults, BOMpartNumber):
    if 'PartNumber' in DistributorResults:
        if len(DistributorResults['PartNumber']) > 2:
            halfLength = (len(DistributorResults['PartNumber']))/2
            for x in range(0, len(BOMpartNumber)):
                if halfLength > len(BOMpartNumber[x]):
                    print "halfLength is equal to: "+halfLength
                    halfLength = len(BOMpartNumber[x])
                if DistributorResults['PartNumber'][0:halfLength] == BOMpartNumber[x][0:halfLength]:
                    return True
    return False

def testForBuyLinkAvailability(currentPart):
    if 'Links' in currentPart:
        for x in range(0, len(currentPart['Links'])):
            if 'Type' in currentPart['Links'][x]:
                if currentPart['Links'][x]['Type'] == 'Buy':
                    return True
    return False


#Checks part prices from a given distributor
#and finds the best cutoff quantity price
#for the based on the quantity needed
def checkPricesAndQuantities(currentPart, bestPart, quantityNeeded, vendor):
    if testForBuyLinkAvailability(currentPart):
        if (currentPart['Stock'])['QuantityOnHand'] > quantityNeeded:
            if 'Pricing' in currentPart:
                if 'Prices' in currentPart['Pricing']:
                    for y in range(0, len(currentPart['Pricing']['Prices'])):
                        if ((currentPart['Pricing']['Prices'])[y])['Quantity'] <= quantityNeeded and ((currentPart['Pricing']['Prices'])[y])['Quantity'] != 0:
                            if ((bestPart['lowestPrice'] == "Not Found") or (bestPart['lowestPrice'] > ((currentPart['Pricing']['Prices'])[y])['Amount']) and (((currentPart['Pricing']['Prices'])[y])['Amount'] != 0) and (((currentPart['Pricing']['Prices'])[y])['Amount'] != None)):
                                bestPart = newBestPart(currentPart, y, vendor)
    return bestPart

#Iterates through all the data gathered from the
#API query and finds the cheapest part.
def findCheapestPart(decodedData, BOMpartNumber, quantityNeeded):
    bestPart = createNewPart()
    pprint.pprint(bestPart)
    for i in range(0, lengthOfPartResults(decodedData)):
        PartResults = (decodedData['PartResults'])[i]
        for j in range(0, lengthOfDistributors(PartResults)):
            Distributors = (PartResults['Distributors'])[j]
            for k in range(0, lengthOfDistributorResults(Distributors)):
                DistributorResults = (Distributors['DistributorResults'])[k]
                if BOMPartNumberMatches(DistributorResults, BOMpartNumber):
                    bestPart = checkPricesAndQuantities(DistributorResults, bestPart, quantityNeeded, Distributors['Name'] )
    return bestPart




#--------API Server Request Section------------#

def formatPartNumberArray(excelField):
    partNumbersArray = []
    for x in range(0,len(excelField)):
        searchToken = {"SearchToken":excelField[x]}
        partNumbersArray.append(searchToken)
    return partNumbersArray



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
    return decodedData


#--------API Server Request Section------------#

def main():
    searchResults = []
    CSVdata = getPartData(fileLocation)
    currentPart, partIndex = findPartNumbersIndex(CSVdata)
    quantityIndex = findQuantityIndex(CSVdata)
    while (currentPart < len(CSVdata)):
        partNumberArray = seperatePartNumbers(CSVdata[currentPart][partIndex])
        formattedPartNumberArray = formatPartNumberArray(partNumberArray)
        ECIAdata = executeSearch(formattedPartNumberArray)
        bestPart = findCheapestPart(ECIAdata, partNumberArray, int(CSVdata[currentPart][quantityIndex]))
        searchResults.append(bestPart)
        print "-------------Search Results Thus Far--------------"
        pprint.pprint(searchResults)
        currentPart = currentPart+1
    finalPartData = formatSearchResults(searchResults)
    writeObjectToFile(finalPartData)
main()
