from flask import Flask
from flask import request
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from apiclient.discovery import build
from operator import attrgetter
from apiclient.http import MediaInMemoryUpload
import urllib2

PROJECT_ID = 'api-project-971540488736'
BUCKET_NAME = 'd71941_bucket_test'

app = Flask(__name__)

client_email = '971540488736-8m9sbcup6rb4fvlgfj4mdsuqva3i3tm1@developer.gserviceaccount.com'
with open("API_Project-749b28932d1c.p12") as f:
    private_key = f.read()

credentials = SignedJwtAssertionCredentials(client_email, private_key, ['https://www.googleapis.com/auth/prediction', 'https://www.googleapis.com/auth/devstorage.full_control'])

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    name = request.args.get('name')
    if request.method == 'GET':
        dictionary = request.args.get('dictionary')
        data = urllib2.urlopen(dictionary).read()
    elif request.method == 'POST':
        data = request.data
    http_auth = credentials.authorize(Http())
    storage = build('storage', 'v1', http=http_auth)
    response = storage.objects().insert(bucket=BUCKET_NAME, name=name, media_body=MediaInMemoryUpload(data)).execute()

    print response

    return "OK"

@app.route('/train', methods=['POST'])
def train():
    body = request.get_json(force=True)
    data = body['data']
    model = body['model_name']
    http_auth = credentials.authorize(Http())
    prediction = build('prediction', 'v1.6', http=http_auth)
    result = prediction.trainedmodels().insert(project=PROJECT_ID, body = {"id":model, "storageDataLocation":BUCKET_NAME+"/"+data}).execute()

    return "OK"

@app.route('/predict', methods=['POST'])
def predict():
    body = request.get_json(force=True)
    model = body['model']
    sample = body['sample']
    http_auth = credentials.authorize(Http())
    prediction = build('prediction', 'v1.6', http=http_auth)
    result = prediction.trainedmodels().predict(project=PROJECT_ID, id=model, body = {"input":{"csvInstance":sample}}).execute()
    print result
    label = result['outputLabel']

    return label

if __name__ == '__main__':
    app.run(debug=True)