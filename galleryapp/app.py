from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image
from io import BytesIO
import base64
from flask import Flask, request, render_template

#---PIOLED---
#setup
i2c = busio.I2C(SCL, SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

#clear tool
def clear_display():
	display.fill(0)
	display.show()

#initial clear
clear_display()

#dithering helper
def push_error(c_val, error, factor):
	return int(c_val + error * (factor/16.0))

#draw image
def draw_image(b64_data):

	print ("loading image")
	
	#load image, get properties
	image = Image.open(BytesIO(base64.b64decode(b64_data)))

	#resize by width
	max_width = 128;
	w_ratio = (max_width/float(image.size[0]))
	r_height = int((float(image.size[1]) * float(w_ratio)))
	image = image.resize((max_width, r_height), Image.ANTIALIAS)

	#convert to rgb, get properties
	rgb_image = image.convert('RGB')
	width, height = image.size

	print ("width: " + str(width) + " height: " + str(height))

	#limit width and height when drawing
	if width > 128:
		width = 128
	if height > 32:
		height = 32

	print ("dithering")
	#convert to black and white
	for j in range(height - 1):
		for i in range(width - 1):
			r, g, b = rgb_image.getpixel((i, j))

			#calculate grayscale and bw value
			gray = (r + b + g) / 3
			bw = 0
			if gray > 255 / 2:
				bw = 255

			#calculate error
			error = gray - bw;

			#(x + 1, y)
			n_r, n_g, n_b = rgb_image.getpixel((i + 1, j))
			n_r = push_error(n_r, error, 7)
			n_g = push_error(n_g, error, 7)
			n_b = push_error(n_b, error, 7)
			rgb_image.putpixel((i + 1, j), (n_r, n_g, n_b))

			#(x - 1, y + 1)
			n_r, n_g, n_b = rgb_image.getpixel((i - 1, j + 1))
			n_r = push_error(n_r, error, 3)
			n_g = push_error(n_g, error, 3)
			n_b = push_error(n_b, error, 3)
			rgb_image.putpixel((i - 1, j + 1), (n_r, n_g, n_b))

			#(x, y + 1)
			n_r, n_g, n_b = rgb_image.getpixel((i, j + 1))
			n_r = push_error(n_r, error, 5)
			n_g = push_error(n_g, error, 5)
			n_b = push_error(n_b, error, 5)
			rgb_image.putpixel((i, j + 1), (n_r, n_g, n_b))

			#(x + 1, y + 1)
			n_r, n_g, n_b = rgb_image.getpixel((i + 1, j + 1))
			n_r = push_error(n_r, error, 1)
			n_g = push_error(n_g, error, 1)
			n_b = push_error(n_b, error, 1)
			rgb_image.putpixel((i + 1, j + 1), (n_r, n_g, n_b))

	print ("displaying")
	for j in range(height):
		for i in range(width):
			r, g, b = rgb_image.getpixel((i, j))
			if r > (255 / 2):
				display.pixel(i, j, 1)
	display.show()
	print ("image displayed")


#---FLASK---
app = Flask(__name__, static_url_path='/static/')

@app.route('/')
def index():
	return render_template("index.html", message="Welcome!")

@app.route('/upload')
def route_upload():
	return app.send_static_file('upload.html')

@app.route('/uploadb64/', methods=['GET', 'POST'])
def route_acceptb64():
	if request.method == 'GET':
		image_b64 = request.args.get('image_b64', '', type=string)
		print ("b64 recieved")
		draw_image(image_b64)
	if request.method == 'POST':
		print ("post recieved")
		post_data = request.form
		image_b64 = post_data.get('image_b64')
		print (image_b64)
		draw_image(image_b64)
		return render_template("index.html", message="Completed draw!")

@app.route('/clear')
def route_clear():
	clear_display()
	return "Completed clear"

#run flask server
if __name__ == '__main__':
	app.run(host='0.0.0.0')
