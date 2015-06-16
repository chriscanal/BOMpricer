#!/usr/bin/python

#This file was written by Chris Canal for iRobot
#If you have any questions or need help with
#a similair script, please contact me at
#chriscanal@chriscanal.com

#Got some help with parsing Json from:
#http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

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
from Tkinter import *
import tkMessageBox
import tkFileDialog
import glob
from threading import Thread


global fileLocation
global outputFileLocation
global CSVMatrix
global searchResults
global outputFileLocation

fileLocation = "Unknown"
outputFileLocation = "Unknown"
CSVMatrix = []
searchResults = []

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
        lowestPrice = checkForPrice(searchData[x]['lowestPrice'])
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
            if 'Type' in (partData['links'][x]):
                if (partData['links'][x])['Type'] == 'Buy':
                    if 'Url' in partData['links'][x]:
                        buyLink = partData['links'][x]['Url']
    return buyLink


def checkForPrice(price):
    if price == 1000000:
        price = 0.0
    return str(price)

def findStockAmount(stockData):
    quantityOnHand = "unknown"
    if 'QuantityOnHand' in stockData:
        quantityOnHand = stockData['QuantityOnHand']
    return quantityOnHand



def findDatasheetLink(partData):
    datasheetLink = "Not Found"
    if 'links' in partData:
        for x in range(0, len(partData['links'])):
            if 'Type' in (partData['links'][x]):
                if partData['links'][x]['Type'] == 'Datasheet':
                    if 'Url' in partData['links'][x]:
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
        'lowestPrice': 1000000,
        'cutOffQuantity': 1000000,
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
                        if 'Quantity' in currentPart['Pricing']['Prices'][y]:
                            if ((currentPart['Pricing']['Prices'])[y])['Quantity'] <= quantityNeeded and ((currentPart['Pricing']['Prices'])[y])['Quantity'] != 0:
                                print "-----------Test 1----------"
                                if 'Amount' in currentPart['Pricing']['Prices'][y]:
                                    if bestPart['lowestPrice'] > ((currentPart['Pricing']['Prices'])[y])['Amount']:
                                        print "-----------Test 2----------"
                                        if ((currentPart['Pricing']['Prices'])[y])['Amount'] != 0.0:
                                            print "-----------Test 3----------"
                                            if (type(((currentPart['Pricing']['Prices'])[y])['Amount']) == type(0.0) or type(((currentPart['Pricing']['Prices'])[y])['Amount']) == type(0)):
                                                print "-----------Test 4----------"
                                                if (((currentPart['Pricing']['Prices'])[y])['Amount']) != None:
                                                    print "-----------Test 5----------"
                                                    bestPart = newBestPart(currentPart, y, vendor)
    return bestPart

#Iterates through all the data gathered from the
#API query and finds the cheapest part.
def findCheapestPart(decodedData, BOMpartNumber, quantityNeeded):
    bestPart = createNewPart()
    pprint.pprint(bestPart)
    if 'PartResults' in decodedData:
        for i in range(0, lengthOfPartResults(decodedData)):
            PartResults = (decodedData['PartResults'])[i]
            if 'Distributors' in PartResults:
                for j in range(0, lengthOfDistributors(PartResults)):
                    Distributors = (PartResults['Distributors'])[j]
                    if 'DistributorResults' in Distributors:
                        for k in range(0, lengthOfDistributorResults(Distributors)):
                            DistributorResults = (Distributors['DistributorResults'])[k]
                            if 'Name' in Distributors:
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

def mainProgram():
    startPricing()
    fileLocation = "Unknown"
    while fileLocation == "Unknown":
        fileLocation = openCSVfile()
    print "OpenCSV just completed"
    CSVdata = getPartData(fileLocation)
    print "CSVMatrix"
    currentPart, partIndex = findPartNumbersIndex(CSVdata)
    print "current Part"
    quantityIndex = findQuantityIndex(CSVdata)
    print "quantityIndex"
    while (currentPart < len(CSVdata)):
        print "while Loop Number "+`currentPart`
        partNumberArray = seperatePartNumbers(CSVdata[currentPart][partIndex])
        formattedPartNumberArray = formatPartNumberArray(partNumberArray)
        ECIAdata = executeSearch(formattedPartNumberArray)
        bestPart = findCheapestPart(ECIAdata, partNumberArray, int(CSVdata[currentPart][quantityIndex]))
        searchResults.append(bestPart)
        print "-------------Search Results Thus Far--------------"
        pprint.pprint(searchResults)
        displayPartData(searchResults)
        currentPart = currentPart+1
    finalPartData = formatSearchResults(searchResults)
    writeObjectToFile(finalPartData)
    quitProgram()

#-------------------GUI Functions---------------------------#
def displayPartData1():
    time.sleep(5)
    displayPartData(searchResults)

def displayPartData(searchResults):
    dataMatrix = formatSearchResults(searchResults)
    for i in range(0, len(dataMatrix)):
        for j in range(0, len(dataMatrix[i])):
            theMessage = dataMatrix[i][j]
            updateBOMgui(theMessage, i, j)
            print theMessage

def updateBOMgui(newLabel, x, y):
    Label(BOMgui, text=newLabel).grid(row=x+2,column=y)


def startPricing():
    popUpLabel = Label(BOMgui,text="The program has started looking for the lowest prices").pack()

def printHello():
    print "Hello Chris"

def openCSVfile():
    return tkFileDialog.askopenfilename()

def getOUtoutFileLocation():
    outputFileLocation = tkFileDialog.askdirectory()
    if "/" in outputFileLocation:
        outputFileLocation += "/PricesAndBuyLinks.csv"
    else:
        outputFileLocation += "\PricesAndBuyLinks.csv"
    print outputFileLocation

def quitProgram():
    mExit = messagebox.askokcancel(title="Quit",message="Are You Sure")
    if mExit > 0:
        BOMgui.destory()
        return

def raise_above_all(window):
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)

def TestUpdate(counter):
    counter+=1
    TextMessage="The new Data is: "+str(counter)
    Label(BOMgui, text=TextMessage).grid(row=counter,column=1)

def TestUpdate1():
    TestUpdate(counter)

def startMain():
    theMain = Thread(target=mainProgram, args=())
    theMain.start()
    GUIupdater = Thread(target=displayPartData1)
    GUIupdater.start()

def threadThreeButtons():
    buttonOne = Thread(target=chooseLocation, args=())
    buttonOne.start()
    buttonTwo = Thread(target=openCSVfileLocation, args=())
    buttonTwo.start()
    buttonThree = Thread(target=startSearch, args=())
    buttonThree.start()

def chooseLocation():
    Spacing0 = Label(BOMgui, text="                  ").grid(row=0,column=0)
    stepOneLabel = Label(BOMgui, text="STEP ONE:\nChoose the output\nfile location\n ").grid(row=0,column=1)
    stepOneButton = Button(BOMgui, text = "Choose Folder", command = getOUtoutFileLocation).grid(row=1,column=1)

def openCSVfileLocation():
    Spacing1 = Label(BOMgui, text="                  ").grid(row=0,column=2)
    stepTwoLabel = Label(BOMgui, text="STEP TWO:\nOpen the BOM file.\nnote:This file must be\nin csv format").grid(row=0,column=3)
    stepTwoButton = Button(BOMgui, text = "Open BOM csv file", command = startMain).grid(row=1,column=3)

def startSearch():
    Spacing2 = Label(BOMgui, text="                  ").grid(row=0,column=4)
    stepThreeLabel = Label(BOMgui, text="STEP THREE:\nBegin looking for\npart Links and Prices!\n  ").grid(row=0,column=5)
    stepThreeButton = Button(BOMgui, text = "START", command = startMain).grid(row=1,column=5)

def guiFunctions():
    BOMgui.title("ECIA Electronic Parts Price Finder")
    userMessage = "Welcome to the iRobot's BOM pricer! \nThis program used the ECIA Authorized search engine to find \nthe lowest priced parts in stock and ready to buy.\nIf you have questions or need help of any kind\n please contact Chris Canal, a former intern at iRobot.\nChris Canal can be reached at chriscanal@chriscanal.com"
    buttonThread = Thread(target=threadThreeButtons, args=())
    buttonThread.start()
    raise_above_all(BOMgui)

if __name__ == "__main__":
    BOMgui = Tk()
    BOMgui.geometry('1200x1200')
    mainThread = Thread(target=guiFunctions, args=())
    mainThread.start()
    BOMgui.mainloop()
