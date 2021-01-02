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

def draw_image():
	image = Image.open(r"matthew.png")
	rgb_image = image.convert('RGB')
	width, height = image.size

	for i in range(width):
		for j in range(height):
			r, g, b = rgb_image.getpixel((i, j))
			if r > 0:
				display.pixel(i, j, 255)

	display.show()

draw_image()
