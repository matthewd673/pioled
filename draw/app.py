from board import SCL, SDA
import busio
import adafruit_ssd1306
import asyncio
import websockets
import logging

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

print("Draw server running");

#setup
i2c = busio.I2C(SCL, SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

#clear display
display.fill(0)
display.show()

async def draw(websocket, path):
    message = await websockets.recv()
    data = message.split(',')

    x = int(data[0])
    y = int(data[1])
    fill = int(data[2])

    print ("Filling " + str(fill) + " at (" + str(x) + ", " + str(y) + ").")

    display.pixel(x, y, fill)
    display.show()


server = websockets.serve(draw, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()