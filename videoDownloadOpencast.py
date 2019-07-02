# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 16:11:51 2019

@author: jpri_
"""

import requests
import json
import os

opUrl = "http://192.168.0.67:8080/api/events/"

events = requests.get(opUrl, auth=("admin", "opencast"))
json_response = json.loads(events.text)

responseArray = []
open("downData.json", "w").write('[')
print("Largo", len(json_response))
count = 0
for i in json_response:
    publications = requests.get(opUrl + i['identifier'] +'/publications',auth=("admin", "opencast"))
    names = []
    responseObject={}
    responseObject['identifier'] = i['identifier']
    responseObject['title'] = i['title']
    responseObject['presenter'] = i['presenter']
    responseObject['creator'] = i['creator']
    responseObject['description'] = i['description']
    responseObject['license'] = i['license']
    responseObject['language'] = i['language']
    responseObject['contributor'] = i['contributor']
    
    
    for data in json.loads(publications.text)[1]['media']:
        videoContent = requests.get(data['url'])
        name = data['url'].split('/')[8]
        names.append(name)
        videoFile = open(name, 'wb')
        print("Descargando...")
        videoFile.write(videoContent.content)
        print("Listo")
        videoFile.close()
    
    if len(names) > 1:
        responseObject['presenter'] = names[0]
        responseObject['presentation'] = names[1]
    else:
        responseObject['presenter'] = names[0]
    
    if count == len(json_response) -1:
        open("downData.json", 'a').write(json.dumps(responseObject) + "]" )
    else:
        open("downData.json", 'a').write(json.dumps(responseObject) + ",\n" )
    count = count + 1
    
