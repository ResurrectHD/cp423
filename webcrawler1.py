"""
CP 423
Assignment 1 - Q 1

Authors:
Josh Degazio - 190560510
Adrian Alting-Mees - 190743560
Robert Mazza - 190778040

Date: 12-02-2023

FILE INFO
Web crawler
python webcrawler1.py 0 https://www.wlu.ca
"""

import requests 
import hashlib
import datetime
import re
import sys

print('cmd entry:', sys.argv)
initialURL = sys.argv[2] # store the URL argument passed from CLI
maxDepth =5
URLs = [initialURL]
visitedURLs = []
extractedURLs = []
responseCodes = []
dateAndTime = []
hashValues = []


for x in range(maxDepth):
    for y in URLs:
        response = requests.get(y)
        content = response.text
        hashValueCurrent = hashlib.md5(y.encode()).hexdigest()

        fileName = "hashValueCurrent.txt"
        file = open(fileName, "w")
        file.write(content)
        file.close()

        extractedURLs == re.findall('<a href+"(.?)"', content)

        for extracted in extractedURLs:
            if extracted not in visitedURLs:
                y.append(extracted)
                visitedURLs.append(extracted)

        responseCodes.append(response.status_code)
        dateAndTime.append(datetime.datetime.now())
        hashValues.append(hashValueCurrent)

        logDateTime = str(datetime)
        logResponseCodes = str(responseCodes)

        logFile = open("crawler.log","w")

        logFile.write(hashValueCurrent + "," + y + "," + logDateTime + "," + logResponseCodes + "\n")
        
        logFile.close()