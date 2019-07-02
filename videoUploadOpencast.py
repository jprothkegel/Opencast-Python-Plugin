# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 20:28:03 2019

@author: jpri_
"""

import requests
import json
import os.path
import time

opUrl = "http://192.168.0.67:8080/api/events"

if (os.path.exists('downData.json')):
    metadataJSON = open('downData.json', 'r')
    metadata = {
        "flavor": "dublincore/episode",
        "fields": [
            {
                "id": "title",
                "value": ""
            },
            {
                "id": "description",
                "value": ""
            },
            {
                "id": "language",
                "value": ""
            },
            {
                "id": "license",
                "value": ""
            },
            {
                "id": "creator",
                "value": ""
            },
        ]
    }
        
    processing= {
        "workflow": "schedule-and-upload",
        "configuration": {
            "flagForCutting": "false",
            "flagForReview": "false",
            "publishToEngage": "true",
            "publishToHarvesting": "true",
            "straightToPublishing": "true"
        }
    }

    acl = [
        {
            "action": "write",
            "role" : "ROLE_ADMIN"
        },
        {
            "action": "read",
            "role": "ROLE_USER"
        }
    ]

    headers = {
        "authorization": "Basic",
        "content-disposition": "form-data"
    }

    for x in json.loads(metadataJSON.read()):
        parsedMetadata = []
        metadata['fields'][0]['value'] = x['title']
        metadata['fields'][1]['value'] = x['description']
        metadata['fields'][2]['value'] = x['language']
        metadata['fields'][3]['value'] = x['license']
        metadata['fields'][4]['value'] = x['contributor']
        parsedMetadata.append(metadata)
        print("METADATA: ",parsedMetadata)
        try:
            if x['presentation']:
                files = {
                    "acl": (None, json.dumps(acl)),
                    "metadata": (None, json.dumps(parsedMetadata)),
                    "processing": (None, json.dumps(processing)),
                    "presenter": (x['presenter'], open(x['presenter'], 'rb')),
                    "presentation": (x['presentation'], open(x['presentation'], 'rb'))
                }    
                r = requests.post(opUrl, files = files, headers = headers, auth=("admin", "opencast"))
                print("CONTENT: ",r.text)
                
        except:
            files = {
                "acl": (None, json.dumps(acl)),
                "metadata": (None, json.dumps(parsedMetadata)),
                "processing": (None, json.dumps(processing)),
                "presenter": (x['presenter'], open(x['presenter'], 'rb'))
            } 
            r = requests.post(opUrl, files = files, headers = headers, auth=("admin", "opencast"))
            print("CONTENT: ",r.text)

else:
    print("El archivo no existe")
