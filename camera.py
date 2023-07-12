import paho.mqtt.client as mqtt
import time
import json
import io
from picamera import PiCamera
import base64

CAPTURE = False

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    #client.subscribe("smart_farm/cameraCommand")

def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload}")
    payload = json.loads(str(msg.payload.decode("utf-8")).strip())
    print(payload['camera'])
    global CAPTURE
    if payload['camera']:
        CAPTURE = True
    else:
        CAPTURE = False

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = on_message

client.will_set('smart_farm/cameraCommand', b'{"camera": 1}')

client.connect("broker.emqx.io", 1883)

i=0

while True:
    i=i+1
    client.loop_start()
    client.subscribe("smart_farm/cameraCommand")
    client.on_message = on_message
    
    while CAPTURE:
        stream = io.BytesIO()
        with PiCamera() as camera:
            camera.start_preview()
            time.sleep(2)
            stream = io.BytesIO()

            for foo in camera.capture_continuous( stream, format='jpeg', bayer=True ):
                num_of_bytes = stream.tell()
                
                client.publish("smart_farm/cameraDataset", stream.getvalue())
                stream.seek(0)
                
                filename = './test.jpg'
                # with open(filename, 'wb') as f:
                    # f.write(stream.read(num_of_bytes))
                    
                # with open("./test.jpg",'rb') as file:
                    # filecontent = file.read()
                    # base64_bytes = base64.b64encode(filecontent)
                    # base64_message = base64_bytes.decode('ascii')
                    # print(base64_message+"\n\n\n")
                    # client.loop_start()
                    # client.subscribe("smart_farm/cameraCommand")
                    # client.on_message = on_message
                    # client.publish('smart_farm/cameraDataset',payload=base64_message)
                    # time.sleep(1)
                    # client.loop_stop()
                # Empty the stream
                #stream.seek(0)
                stream.truncate()
                
        #client.publish('smart_farm/cameraDataset', payload=i)
    
    time.sleep(1)
    client.loop_stop()

#client.loop_forever()
