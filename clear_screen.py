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
