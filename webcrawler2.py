"""
CP 423
Assignment 1 - Q 2

 Authors:
 Josh Degazio - 190560510
 Adrian Alting-Mees - 190743560
 Robert Mazza - 190778040

 Date: 12-02-2023

 FILE INFO
 Crawls through a Google Scholar page, then proceeds to download, hash, 
 and extract information from specific pages, then saving it in a JSON format.
"""

import hashlib
import sys
from bs4 import BeautifulSoup
import json
import urllib.request

#Globals
occupation = ""
author = ""
keywords = ""
image = ""
soup = None
html = ""
response = ""

#Dictionary Helpers
c_all = ""
c_since = ""
h_all = ""
h_since = ""
i_all = ""
i_since = ""

#Dictionaries
researcher_dict = {
}
r_d_c = {
"all" : "",
"since_2018" : ""
}
r_d_h = {
"all" : "",
"since_2018" : ""
}
r_d_i = {
"all" : "",
"since_2018" : ""
}
r_d_r = {
    "coauthor_name" : "",
    "coauthor_title" : "",
    "coauthor_link" : ""
}


def extract_info(url):
    #Open URL using urllib
    response = urllib.request.urlopen(url)
    print("Response Status: "+ str(response.getcode()) )

    #Get the webpage html
    html = response.read()
    #Set soup as webpage
    soup = BeautifulSoup(html, 'html.parser')

    #Find everything
    occupation = soup.find("div", class_="gsc_prf_il").get_text()
    author = soup.find("div", id="gsc_prf_inw").get_text()
    keywords = soup.find("div", id="gsc_prf_int").get_text(separator=", ")
    image = soup.find("img", id="gsc_prf_pup-img")['src']

    #Use stats to pull all relevant attributes
    stats = soup.find_all("td", class_="gsc_rsb_std")

    #Go through each stat element to pull citations, hindex, and i10index
    c_all = stats[0].get_text()
    c_since = stats[1].get_text()

    h_all = stats[2].get_text()
    h_since = stats[3].get_text()

    i_all = stats[4].get_text()
    i_since = stats[5].get_text()

    #Return all variables so the globals actually work properly
    return(occupation, author, keywords, image, c_all, c_since, h_all, h_since, i_all, i_since, html, soup)

def write_to_files():
    #Write downloaded content to h.txt
    h = hashlib.md5(soup.encode()).hexdigest()
    lines = html.split(b"\n")
    with open(h + ".txt", 'wb') as f:
        for line in lines:
            f.write(line)
        f.close()

    #Save extracted info to h.json
    with open(h + ".json", "w") as f:
        json.dump(researcher_dict, f, indent=4)
        f.close()
    return()

def jsonify():
    #Gets scholars bio
    bio = occupation.split(", ")
    #Set variables in json format
    researcher_dict["researcher_name"] = author
    researcher_dict["researcher_caption"] = bio[0]

    #Goes through bio to ensure that no institutions are missed
    bio = bio[1:]
    i = 0
    while i != len(bio):
        researcher_dict["researcher_institution_" + str(i)] = bio[i]
        i+=1

    researcher_dict["researcher_keywords"] = keywords
    researcher_dict["researcher_imgURL"] = image

    #Do the nested dicts
    r_d_c["all"] = c_all
    r_d_c["since_2018"] = c_since
    researcher_dict["researcher_citations"] = r_d_c

    #Do the nested dicts
    r_d_h["all"] = h_all
    r_d_h["since_2018"] = h_since
    researcher_dict["researcher_hindex"] = r_d_h

    #Do the nested dicts
    r_d_i["all"] = i_all
    r_d_i["since_2018"] = i_since
    researcher_dict["researcher_i10index"] = r_d_i
    
    #Create temp list for us to append to 
    list_dicts = []

    #Finds authors and links
    authors = soup.find_all("span", class_="gsc_rsb_a_desc")
    links = soup.find_all("a", tabindex="-1")

    i=0
    #Loop through authors
    for a in authors:
        #Split text
        text = a.get_text(separator="$|")
        #Get two of the three attributes
        attributes = text.split('$|')
        #Create a temp dict
        temp_dict = {
        "coauthor_name" : attributes[0],
        "coauthor_title" : attributes[1],
        "coauthor_link" : "scholar.google.ca" + links[i]['href']
        }
        i+=1
        #append temp dict to list
        list_dicts.append(temp_dict)
    #add list to real dict
    if(len(list_dicts) == 0):
        list_dicts.append("none")
    researcher_dict["researcher_coauthors"] = list_dicts

    #Create temp dict for us to append to 
    list_dicts = []

    temp_page = 0
    newresponse = urllib.request.urlopen(url+'&cstart='+ str(temp_page) +'&pagesize=100')
    newhtml = newresponse.read()
    newsoup = BeautifulSoup(newhtml, 'html.parser')
    while newsoup.find("td", class_="gsc_a_e") == None:
        newresponse = urllib.request.urlopen(url+'&cstart='+ str(temp_page) +'&pagesize=100')
        print("Response Status: "+ str(newresponse.getcode()))

        #Get the webpage html
        newhtml = newresponse.read()
        #Set soup as webpage
        newsoup = BeautifulSoup(newhtml, 'html.parser')
        
        #Find papers
        papers = newsoup.find_all("tr", class_="gsc_a_tr")
        for paper in papers:
            #get the text
            text = paper.get_text(separator="$|")
            #get the attributes
            attributes = text.split('$|')

            #Create a temp dict with attributes
            if(len(attributes) >= 5):
                temp_dict = {
                "paper_title" : attributes[0],
                "paper_authors" : attributes[1],
                "paper_journal" : attributes[2],
                "paper_citedby" : attributes[4],
                "paper_year" : attributes[-1] 
                }
            elif(len(attributes) == 4):
                temp_dict = {
                "paper_title" : attributes[0],
                "paper_authors" : attributes[1],
                "paper_journal" : attributes[2],
                "paper_year" : attributes[-1] 
                }
            elif(len(attributes) == 3):
                temp_dict = {
                "paper_title" : attributes[0],
                "paper_authors" : attributes[1],
                "paper_year" : attributes[-1] 
                }
            elif(len(attributes) == 2):
                temp_dict = {
                "paper_title" : attributes[0],
                "paper_authors" : attributes[1],
                }
            elif((len(attributes) == 1) & (attributes[0] != 'There are no articles in this profile.')):
                temp_dict = {
                "paper_title" : attributes[0],
                }

            #Append dict to list
            list_dicts.append(temp_dict)
        temp_page+=100
    #When all dicts are appended, append list to real dict
    researcher_dict["researcher_papers"] = list_dicts
    return()

#Helper method to close the program
def closeProgam():
    print("\nA URL must be entered as a command line argument.")
    print("Closing Program.\n")
    exit(0)

###############################################################
# Program Start

try:
    url = sys.argv[1] # store the URL argument passed from terminal
except:
    closeProgam() 

if(url[0:8] != 'https://'):
    closeProgam()

#Run Functions
#Set global values
occupation, author, keywords, image, c_all, c_since, h_all, h_since, i_all, i_since, html, soup = extract_info(url)
jsonify()
write_to_files()
