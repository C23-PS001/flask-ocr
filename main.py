from flask import Flask, request, redirect, url_for
import numpy as np
import json
import requests
import easyocr
from google.cloud import storage
from PIL import Image
from io import BytesIO
from flask_cors import CORS
import os
import re

def CariNIK(X):
  for i in X:
    if re.match(r'\d{10,}',i):
      return i
      
  return ""

def CariNama(X):
  c=0
  for i in X:
    if c==1:
      return i
    if re.match(r'nam[a-z]',i.lower()):
      c=1
      
  return ""

def CariTTL(X):
  for i in X:
    match = re.search(r'[a-zA-Z, ]+(\d{2}[- ]{1}\d{2}[- ]{1}\d{4})', i)
    if match:
        extracted_format = match.group(1)
        return extracted_format
  return ""

app = Flask(__name__)
CORS(app)

reader = easyocr.Reader(['id'])
@app.route('/absen',methods=['POST'])
def ilham(params):    
    response = requests.get(params)
    image = Image.open(BytesIO(response.content))
    results = reader.readtext(image)
    List= []
    for result in results:
        List.append(result[1])
    #print(image_list[:20])
    # TTL_SPLIT= CariTTL(List)
    return json.dumps({'NIK':CariNIK(List),'Nama':CariNama(List),'Tgl Lahir':CariTTL(List)})

@app.route('/masuk',methods=['POST'])
def upload():
    credentials_path = r"nyobaaja-973da4b3851c.json"
    client = storage.Client.from_service_account_json(credentials_path)
    file= request.files['images']
    file.save(file.filename)
    bucket_name = "upload_foto"
    # Get the bucket and create a Blob object
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('fotoktp/{}'.format(file.filename))
    # Upload the file to Cloud Storage
    blob.upload_from_filename(file.filename)
    # Get the public URL of the file
    videoUrl = blob.public_url
    os.remove(file.filename)
    test = ilham(videoUrl)
    response = delete(file.filename)
    return test, response

@app.route('/keluar',methods=['POST'])
def delete(filenames):
    credentials_path = r"nyobaaja-973da4b3851c.json"
    client = storage.Client.from_service_account_json(credentials_path)
    bucket_name = "upload_foto"
    # Get the bucket and create a Blob object
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('fotoktp/{}'.format(filenames))
    blob.delete()
    return 'Success'    

if __name__ == '__main__':
    app.run('0.0.0.0', 8080, debug=True)