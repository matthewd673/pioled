import requests
import sys
import os
import time
import io

from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

API_GOT204_RETRY_SECS = 10
API_MIDSONG_DOUBLECHECK_SECS = 10
API_REFRESH_BUFFER_SECS = 15
PLAYER_SONGENDED_BUFFER_MS = -6000

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
access_token = ''
refresh_token = ''

refresh_time = 0

def main():
	global access_token
	global refresh_token

	print('Starting screen.py...')

	if len(sys.argv) < 3:
		print('You must pass an authorization and refresh token')
		print('Everything will break soon')

	# initialize screen
	i2c = busio.I2C(SCL, SDA)
	display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

	# initialize spotify
	access_token = sys.argv[1]
	refresh_token = sys.argv[2]

	refresh_access_token()

	while True:
		loop(display)

def loop(display):
	print('Making request...')
	data = get_currently_playing()

	image = Image.new("1", (display.width, display.height))
	draw = ImageDraw.Draw(image)
	font = ImageFont.load_default()

	if len(data) == 0:
		print('No data to display')
		display.fill(0)
		display.show()
		time.sleep(API_GOT204_RETRY_SECS)
		return

	# grab stats
	progress = data['progress_ms']
	duration = data['item']['duration_ms']
	name = data['item']['name']
	artist_1 = data['item']['artists'][0]['name']
	art_url = data['item']['album']['images'][2]['url']
	is_playing = data['is_playing']

	draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # clear

	# draw text
	draw_text(draw, 34, 2, name, font)
	draw_text(draw, 34, 10, artist_1, font)

	display.image(image)
	display.show()

	# draw album art (manually)
	if art_url != None:
		draw_image(display, 0, 0, download_image(art_url), 32, 32)

	# draw progress until song is over
	secs_since_api_check = 0
	while progress < duration + PLAYER_SONGENDED_BUFFER_MS:
		if secs_since_api_check > API_MIDSONG_DOUBLECHECK_SECS: # double check with api
			new_data = get_currently_playing()
			if new_data['item']['name'] != name: # new song started
				break
			# same song, just double check position
			progress = new_data['progress_ms']
			is_playing = data['is_playing']
			secs_since_api_check = 0

		draw_line(display, 34, 24, 90, 3, progress, duration)
		display.show()

		if is_playing:
			progress += 1000

		secs_since_api_check += 1
		time.sleep(1)

def draw_clear(draw):
	draw.rectangle((0, 0, 128, 32), outline=0, fill=0)

def draw_text(draw, x, y, text, font):
	draw.text((x, y), text, font=font, fill=255)

def draw_line(display, x, y, width, height, val, max_val):
	d_width = (val / max_val) * width
	for i in range(x, x + round(d_width)):
		for j in range(y, y + height):
			display.pixel(i, j, 255)

def draw_image(display, x, y, draw_img, width, height):
	draw_img = draw_img.resize((width, height), Image.ANTIALIAS) # resize to match width and height
	rgb_image = draw_img.convert('RGB') # necessary??
	# apply dithering
	for j in range(height - 1):
		for i in range(width - 1):
			r, g, b = rgb_image.getpixel((i, j))

			gray = (r + b + g) / 3
			bw = 0
			if gray > 255 / 2:
				bw = 255

			error = gray - bw

			# (x + 1, y)
			n_r, n_g, n_b = rgb_image.getpixel((i + 1, j))
			n_r = push_error(n_r, error, 7)
			n_g = push_error(n_g, error, 7)
			n_b = push_error(n_b, error, 7)
			rgb_image.putpixel((i + 1, j), (n_r, n_g, n_b))

			# (x - 1, y + 1)
			n_r, n_g, n_b = rgb_image.getpixel((i - 1, j + 1))
			n_r = push_error(n_r, error, 3)
			n_g = push_error(n_g, error, 3)
			n_b = push_error(n_b, error, 3)
			rgb_image.putpixel((i - 1, j + 1), (n_r, n_g, n_b))

			# (x, y + 1)
			n_r, n_g, n_b = rgb_image.getpixel((i, j + 1))
			n_r = push_error(n_r, error, 5)
			n_g = push_error(n_g, error, 5)
			n_b = push_error(n_b, error, 5)
			rgb_image.putpixel((i, j + 1), (n_r, n_g, n_b))

			# (x + 1, y + 1)
			n_r, n_g, n_b = rgb_image.getpixel((i + 1, j + 1))
			n_r = push_error(n_r, error, 1)
			n_g = push_error(n_g, error, 1)
			n_b = push_error(n_b, error, 1)
			rgb_image.putpixel((i + 1, j + 1), (n_r, n_g, n_b))

	for j in range(height):
		for i in range(width):
			r, g, b = rgb_image.getpixel((i, j))
			if r > (255/2):
				display.pixel(i, j, 1)

def push_error(c_val, error, factor):
	return int(c_val + error * (factor/16.0))

def download_image(url):
	r = requests.get(url, stream=True)
	if r.status_code == 200:
		print('Got image')
		i = Image.open(io.BytesIO(r.content))
		return i
	else:
		print('Image get error')

def get_currently_playing():
	global access_token

	refresh_access_token()

	status_url = 'https://api.spotify.com/v1/me/player/currently-playing'
	headers = {}
	headers['Accept'] = 'application/json'
	headers['Authorization'] = 'Bearer ' + access_token
	status_request = requests.get(status_url, headers=headers)

	print('Completed request, got ' + str(status_request.status_code))

	if status_request.status_code == 204: # no content
		return {}

	data = status_request.json()
	return data

def refresh_access_token():
	global refresh_time
	global access_token
	global refresh_token

	if refresh_time - get_time_secs() > API_REFRESH_BUFFER_SECS: # nothing to worry about
		return;

	print('Refreshing access_token...')
	auth_url = 'https://accounts.spotify.com/api/token'
	form = {
		'grant_type': 'refresh_token',
		'refresh_token': refresh_token
	}
	auth_request = requests.post(auth_url, data=form, auth=(client_id, client_secret))

	if auth_request.status_code == 200:
		print('Auth refresh success')
		data = auth_request.json()
		access_token = data['access_token']
		refresh_time = get_time_secs() + (data['expires_in'])
	else:
		print('Auth refresh failed')

def get_time_secs():
	return int(round(time.time()))

if __name__ == '__main__':
	main()
