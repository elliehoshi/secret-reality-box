from asyncio.exceptions import CancelledError
from asyncio.tasks import ALL_COMPLETED
import logging
import asyncio
import os
from typing import List

# Crickit - Servo and NeoPixel
from adafruit_crickit import crickit
# Drive NeoPixels on the NeoPixels Block on Crickit FeatherWing
from adafruit_seesaw.neopixel import NeoPixel

import picamera
from starlette.websockets import WebSocket
from uvicorn import Config, Server
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.routing import Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from uvicorn.config import LOGGING_CONFIG
from google.cloud import vision
import pygame 
from gtts import gTTS

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="vision-voice-key.json"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
LOGGING_CONFIG["formatters"]["default"]["fmt"] = LOG_FORMAT
LOGGING_CONFIG["formatters"]["access"][
    "fmt"
] = "%(asctime)s | %(levelname)s | %(name)s | %(client_addr)s | %(request_line)s | %(status_code)s"
LOGGING_CONFIG["loggers"]["uvicorn.error"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["uvicorn.error"]["propagate"] = False
logger = logging.getLogger("main")

websockets: List[WebSocket] = []
camera = picamera.PiCamera()
vision_client = vision.ImageAnnotatorClient()

async def broadcast(*args, **kwargs):
    value = args[0]
    if len(websockets) > 0:
        logger.info("Sending: " + value)
        await asyncio.wait(
            [asyncio.create_task(ws.send_text(value)) for ws in websockets],
            timeout=3,
            return_when=ALL_COMPLETED,
        )

async def poll_camera():
    while True:
#         camera.start_preview()
        await asyncio.sleep(.5)
        camera.capture('image.jpg')
#         camera.stop_preview()

        with open('image.jpg', 'rb') as image_file:
            content = image_file.read()
            response = vision_client.label_detection(image=vision.Image(content=content))
            labels = response.label_annotations
            for label in labels:
                await broadcast("Tags: {}".format(label.description))

        await asyncio.sleep(1)

# servo code
async def motor_wait():
    while True:
        print("Moving servo #1: motor_wait()")
        crickit.servo_1.angle = 0      # right
        await asyncio.sleep(1)
        crickit.servo_1.angle = 90     # middle
        await asyncio.sleep(1)
        crickit.servo_1.angle = 180    # left
        await asyncio.sleep(1)
        crickit.servo_1.angle = 90     # middle
        await asyncio.sleep(1)
        crickit.servo_1.angle = 0     # right
# end servo code


# nanoring NeoPixel code
num_pixels = 30  # Number of pixels driven from Crickit NeoPixel terminal

# The following line sets up a NeoPixel strip on Seesaw pin 20 for Feather
pixels = NeoPixel(crickit.seesaw, 20, num_pixels)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

async def neopixel_rainbow():
    while True:
        print("neopixel rainbow")
        for j in range(255):
                for i in range(num_pixels):
                    rc_index = (i * 256 // num_pixels) + j
                    pixels[i] = wheel(rc_index & 255)
                pixels.show()
                await asyncio.sleep(1)
# end nanoring NeoPixel code

class DataEndpoint(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        websockets.append(websocket)
        logger.info("Connected to %s", websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        websockets.remove(websocket)
        logger.warning(
            "Disconnected from websocket %s with code %s", websocket, close_code
        )
        await websocket.close()

    async def on_receive(self, websocket: WebSocket, data: str, sound_alarm: False) -> None:
        logger.info("Socket: %s, Message: %s", websocket, data, sound_alarm)
        if data is not None:
            t2s = gTTS(data, lang ='en')
            t2s.save('speech.mp3')
            pygame.mixer.init()
            pygame.mixer.music.load('speech.mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                pygame.time.Clock().tick(10)

app = Starlette(
    routes=[
        WebSocketRoute("/ws", endpoint=DataEndpoint),
        Mount("/", app=StaticFiles(directory="static", html=True), name="static"),
    ],
    middleware=[Middleware(GZipMiddleware, minimum_size=1000)],
)

server = Server(
    config=Config(
        host="localhost",
        port=21489,
        app=app,
    )
)

async def event_loop():
    await asyncio.gather(
        asyncio.create_task(server.serve()),
        asyncio.create_task(poll_camera()),
        asyncio.create_task(motor_wait()),
        asyncio.create_task(neopixel_rainbow())
    )

def main():
    try:
        asyncio.run(event_loop())
    except CancelledError as er:
        pass

# the below 'if' statement helps python distinguish the main function.
if __name__ == "__main__":
    main()
