from board import SCL, SDA
import busio
import adafruit_ssd1306

def main():
	# initialize screen
	i2c = busio.I2C(SCL, SDA)
	display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

	display.fill(0)
	display.show()

if __name__ == '__main__':
	main()
