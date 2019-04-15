# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:16:09 2019

@author: jpri_
"""

import requests
import json
import os
import obspython as obs

getMetadataUrl = 'http://localhost:3000/video/inactive'
record_folder = os.path.expanduser("~") + os.path.sep + "Videos"
opencastUrl = 'http://192.168.1.230:8080/api/events'
deleteUrl = 'http://localhost:3000/video/delete'


#-------------- Helpers -----------------------
def getMetadata(url):
    response = requests.get(url)
    json_response = json.loads(response.text)
    metadata = json_response['message'][0]['metadata']
    metadata['id'] = json_response['message'][0]['_id']
    print("METADATA",metadata)
    for i in metadata['fields']:
        del i['_id']
    return metadata

def find_latest_obs_capture(capture_dir):
    def new_video_sort_key(f):
        if f.name[-3:] in ['flv', 'mp4', 'mov', 'mkv']:
            return f.stat().st_mtime
        return 0
    newest_video_file = sorted(os.scandir(capture_dir), key = new_video_sort_key, reverse = True)[0]
    if new_video_sort_key(newest_video_file) is 0:
        print("Could not find any video files!")
        return None
    return newest_video_file.name

def delete_video(video_id, url):
    login = requests.post(url = "http://localhost:3000/user/login",data={"email":"test@test.com","password":"tester"})
    token = json.loads(login.text)['token']
    response = requests.post(url = url, data={'streamKeyID':video_id}, headers={"Authorization":"Bearer "+token})
    print("RESPONSE",response.text)

def opencast_ingest( opUrl, metadataUrl, recordFolder, delete_url):
    notParsedMetadata = getMetadata(metadataUrl)
    notParsedMetadata['fields'][4]['value'] = notParsedMetadata['fields'][4]['value'].split(",")
    notParsedMetadata['fields'][5]['value'] = notParsedMetadata['fields'][5]['value'].split(",")
    
    metadata = []
    metadata.append(notParsedMetadata)
    video_id = metadata[0]['id']
    print("ID",video_id)
    
    processing = {
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
        "role": "ROLE_ADMIN",
      },
      {
        "action": "read",
        "role": "ROLE_USER",
      }
    ]
    
    headers = {   
        "authorization": "Basic",
        "content-disposition": "form-data"
    }   
    
    filename = find_latest_obs_capture(record_folder)
    fullPathFile = record_folder + os.path.sep + filename
    

    files = {
        "acl": (None , json.dumps(acl)),
        "metadata": (None, json.dumps(metadata)),
        "processing": (None, json.dumps(processing)),
        "presenter": (filename, open(fullPathFile,'rb'))
    }
    
    requests.post(opUrl, files=files, headers=headers, auth=("admin","opencast"))
    print("ID",video_id)
    delete_video(video_id, delete_url)
    

#----------------- Plugin -------------------------
class OBSPluginOpencast():
  description = "<b>Opencast Ingester</b>" + \
                "<hr>" + \
                "Automatically ingest recordings to Opencast, just after the recording is finished" + \
                "<br/><br/>" + \
                "©2019 Juan Pablo Rothkegel" + \
                "<hr>"

  recording_signal_handler= None

  def __init__(self, op_url, record_folder, metadata_url, delete_url):
    self.op_url = op_url
    self.record_folder = record_folder
    self.metadata_url = metadata_url
    self.delete_url = delete_url

  def recording_finished(self, stop_code):
    if stop_code is 0:
      opencast_ingest(self.op_url, self.metadata_url, self.record_folder, self.delete_url)

#--------------- Plugin Instance --------------------------------------------
opencastplug = OBSPluginOpencast(opencastUrl, record_folder, getMetadataUrl, deleteUrl)


#------------ Callbacks ----------------------------------
def cb_recording_finished(callback_data):
  stop_code = obs.calldata_int(callback_data, "code")
  opencastplug.recording_finished(stop_code)
  return True

def update_recording_callback(reconnect = True):
  if opencastplug.recording_signal_handler is not None:
    obs.signal_handler_disconnect(opencastplug.recording_signal_handler, "stop", cb_recording_finished)
  if reconnect:
    opencastplug.recording_signal_handler = obs.obs_output_get_signal_handler(obs.obs_frontend_get_recording_output())
    obs.signal_handler_connect(opencastplug.recording_signal_handler, "stop", cb_recording_finished)


#------------- OBS Interaction --------------------------
def script_description():
  return opencastplug.description

def script_load(settings):
  update_recording_callback()


