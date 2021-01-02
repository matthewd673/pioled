from board import SCL, SDA
import busio

import adafruit_ssd1306

i2c = busio.I2C(SCL, SDA)

display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

display.pixel(0, 0, 1)
display.pixel(64, 16, 1)
display.pixel(127, 31, 1)
display.show()
