# debug websockets
from asyncio.exceptions import CancelledError
from asyncio.tasks import ALL_COMPLETED
import logging
import asyncio
import os
from typing import List

import picamera     #camera library
import pygame as pg #audio library
import os           #communicate with os/command line
import numpy as np

from google.cloud import vision  #gcp vision library
from time import sleep
from adafruit_crickit import crickit
import time
import signal
import sys
import subprocess

# debug websockets
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
from gtts import gTTS
import re   #regex lib for string searches


#set up your GCP credentials - replace the " " in the following line with your .json file and path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="vision-voice-key.json"

# ELLIE DEBUG TEST
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

async def broadcast(*args, **kwargs):
    value = args[0]
    if len(websockets) > 0:
        logger.info("Sending: " + value)
        await asyncio.wait(
            [asyncio.create_task(ws.send_text(value)) for ws in websockets],
            timeout=3,
            return_when=ALL_COMPLETED,
        )
# END ELLIE DEBUG TEST

# this line connects to Google Cloud Vision! 
client = vision.ImageAnnotatorClient()

# global variable for our image file - to be captured soon!
image = 'image.jpg'

def takephoto(camera):
    
    # this triggers an on-screen preview, so you know what you're photographing!
    camera.start_preview() 
    sleep(.5)                   #give it a pause so you can adjust if needed
    camera.capture('image.jpg') #save the image
    camera.stop_preview()       #stop the preview

def ocr_handwriting(image):
    #this function sends your image to google cloud using the
    #text_detection method, collects a response, and parses that
    #response for all of the associated words detected.
    #these are captured as a single joined string in word_text.
    #if there is handwriting detected, strings are sent to motor_turn()
    #to determine if and how the motor should actuate!
    
    #these two lines connect to google cloud vision in the text_detection mode
    response = client.text_detection(image=image)
    text = response.full_text_annotation
    
    word_text = ""
    
    #this next block of code parses google cloud's response
    #down to words detected, which are combined into word_text
    for page in text.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text += " "
                    word_text += ''.join([
                        symbol.text for symbol in word.symbols
                        ])                    

    #this next block checks if any word text was detected - and
    #if it was, the text and search strings are sent to motor_turn()

    if word_text:
        return word_text
    else:
        return 0

# ELLIE DEBUG TEST
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

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        logger.info("Socket: %s, Message: %s", websocket, data)
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
# END ELLIE DEBUG TEST


def main():
    prev_outputs = []
    counter = 0
    #generate a camera object for the takephoto function to
    #work with
    camera = picamera.PiCamera()
    sleep_time = 0.1
    #setup our pygame mixer to play audio in subsequent stages
  #  pg.init()
  #  pg.mixer.init()
    
    #this while loop lets the script run until you ctrl+c (command line)
    #or press 'stop' (Thonny IDE)
    while True:
 
        takephoto(camera) # First take a picture
        """Run a label request on a single image"""

        with open('image.jpg', 'rb') as image_file:
            #read the image file
            content = image_file.read()
            #convert the image file to a GCP Vision-friendly type
            image = vision.Image(content=content)
            output = ocr_handwriting(image)
            
            if output != 0:
                prev_outputs.append(output)
                counter += 1
                print(output)
                sleep_time = 0.01
            
            elif output == 0: # No text detected anymore
                counter = 0
                prev_outputs = []
            
                
            if counter == 10: #text is detected
                values, counts = np.unique(prev_outputs, return_counts=True)
                ind = np.argmax(counts)
                most_likely_candidate = values[ind]
                print('Most likely handwriting(): {}'.format(most_likely_candidate))
                
            time.sleep(sleep_time)        
        
if __name__ == '__main__':
        main()