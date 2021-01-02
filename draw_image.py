from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image

#setup
i2c = busio.I2C(SCL, SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

#clear display
display.fill(0)
display.show()

def push_error(c_val, error, factor):
	return int(c_val + error * (factor/16.0))

def draw_image():
	#load image, get properties
	image = Image.open(r"bliss.png")
	rgb_image = image.convert('RGB')
	width, height = image.size

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


draw_image()
