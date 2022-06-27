import requests
import sys
import os
import time
import io

from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

def main():
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

	print('Access Token: ' + access_token)
	print('Refresh Token: ' + refresh_token)

	while True:
		loop(display, access_token)

def loop(display, access_token):
	print('Making request...')
	data = get_currently_playing(access_token)

	image = Image.new("1", (display.width, display.height))
	draw = ImageDraw.Draw(image)
	font = ImageFont.load_default()

	if len(data) == 0:
		print('No data to display')
		display.fill(0)
		display.show()
		time.sleep(3*60)
		return

	# grab stats
	progress = data['progress_ms']
	duration = data['item']['duration_ms']
	name = data['item']['name']
	artist_1 = data['item']['artists'][0]['name']
	art_url = data['item']['album']['images'][2]['url']

	draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # clear

	# draw text
	draw_text(draw, 36, 2, name, font)
	draw_text(draw, 36, 10, artist_1, font)

	display.image(image)

	# draw album art (manually)
	if art_url != None:
		draw_image(display, 2, 2, download_image(art_url), 32, 32)

	# draw progress until song is over
	while progress < duration + 500:
		print('Drawing...')
		draw_line(display, 36, 24, 90, 3, progress, duration)
		# draw_line(display, 36, 25, 90, 1, 1, 1)

		# print('Drawing...')
		# display.image(image)
		display.show()

		progress += 1000;
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

def get_currently_playing(access_token):
	headers = {}
	headers['Accept'] = 'application/json'
	headers['Authorization'] = 'Bearer ' + access_token
	r = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)

	print('Completed request, got ' + str(r.status_code))

	if r.status_code == 204: # no content
		return {}

	data = r.json()
	return data

if __name__ == '__main__':
	main()
