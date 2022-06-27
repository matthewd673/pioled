from flask import Flask, render_template, redirect, make_response, request
from urllib.parse import urlencode
import requests
import random
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/auth')
def auth():
	scope = 'user-read-playback-state'
	redirect_uri = 'http://192.168.1.13/callback'
	state = generateRandomString(16)
	client_id = os.getenv('SPOTIFY_CLIENT_ID')

	auth_url = 'https://accounts.spotify.com/authorize?'
	auth_params = {
		'response_type': 'code',
		'client_id': client_id,
		'scope': scope,
		'redirect_uri': redirect_uri,
		'state': state
	}

	response = make_response(redirect(auth_url + urlencode(auth_params)))
	response.set_cookie('state', state)

	return response

@app.route('/callback')
def callback():
	code = request.args.get('code')
	state = request.args.get('state')
	storedState = request.cookies.get('state')
	redirect_uri = 'http://192.168.1.13/callback'

	message = 'Nothing happened'

	if code == None:
		print('None code')
		responseText = 'None code'
		return render_template('callback.html', api_message=message, success=False)

	if state != storedState:
		print('State mismatch')
		print('state: ' + state)
		print('storedState: ' + storedState)
		message = 'State mismatch'
		return render_template('callback.html', api_message=message, success=False)

	auth_url = 'https://accounts.spotify.com/api/token'
	form = {
		'code': code,
		'redirect_uri': redirect_uri,
		'grant_type': 'authorization_code'
	}

	client_id = os.getenv('SPOTIFY_CLIENT_ID')
	client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

	print('Sending auth post request...')

	auth_request = requests.post(auth_url, data=form, auth=(client_id, client_secret))
	if auth_request.status_code == 200:
		print('Got 200!')
		data = auth_request.json()

		access_token = data['access_token']
		refresh_token = data['refresh_token']

		message = 'Got 200!'

		subprocess.Popen(['python3', 'screen.py', access_token, refresh_token])

	response = make_response(render_template('callback.html', api_message=message, success=True))
	response.set_cookie('state', '', expires=0)

	return response

def generateRandomString(length):
	text = ''
	chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

	for i in range(length):
		text += chars[random.randrange(len(chars))]
	return text

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)
