from board import SCL, SDA
import busio
import adafruit_ssd1306
import asyncio
import websockets

#setup
i2c = busio.I2C(SCL, SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

#clear display
display.fill(0)
display.show()

async def draw(websocket, path):
    coords = await websockets.recv()
    c_array = coords.split(',')

    x = c_array[0]
    y = c_array[1]
    fill = c_array[2]

    display.pixel(x, y, fill)
    display.show()


server = websockets.serve(draw, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()