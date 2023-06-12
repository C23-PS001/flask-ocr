import json
import requests
import easyocr
import os
import re

from flask import Flask, request
from google.cloud import storage
from google.cloud import secretmanager
from PIL import Image
from io import BytesIO
from flask_cors import CORS
from urllib.parse import unquote

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
def getOCRData(params):    
    response = requests.get(params)
    image = Image.open(BytesIO(response.content))
    results = reader.readtext(image)
    List= []
    for result in results:
        List.append(result[1])
    return json.dumps({
      'error': 'false',
      'message': 'Data berhasil diterima!',
      'NIK':CariNIK(List),
      'Nama':CariNama(List),
      'Tgl Lahir':CariTTL(List), 
      'Link Photo':params
      })

@app.route('/masuk',methods=['POST'])
def upload():
  
    gcpClient = secretmanager.SecretManagerServiceClient()
    keysName = f"projects/872765504345/secrets/gcs-key/versions/latest"
    response = gcpClient.access_secret_version(request={"name": keysName})
    credentials = json.loads(response.payload.data.decode('UTF-8'))
    client = storage.Client.from_service_account_info(credentials)
    file= request.files['images']
    file.save(file.filename)
    bucket_name = "suara-kita"
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('fotoktp/{}'.format(file.filename))
    blob.upload_from_filename(file.filename)
    linkFoto = blob.public_url
    os.remove(file.filename)
    test = getOCRData(linkFoto)
    return test

@app.route('/keluar',methods=['POST'])
def delete():
    linkFoto = request.form.get('linkFoto')
    gcpClient = secretmanager.SecretManagerServiceClient()
    keysName = f"projects/872765504345/secrets/gcs-key/versions/latest"
    response = gcpClient.access_secret_version(request={"name": keysName})
    credentials = json.loads(response.payload.data.decode('UTF-8'))
    client = storage.Client.from_service_account_info(credentials)
    bucket_name = "suara-kita"
    bucket = client.get_bucket(bucket_name)
    filename = unquote(os.path.basename(linkFoto)) 
    blob = bucket.blob('fotoktp/{}'.format(filename))
    blob.delete()
    return 'Success'    

if __name__ == '__main__':
    app.run(debug=True)