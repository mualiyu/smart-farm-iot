#!/usr/bin/env python3

import serial
import json
import queue
from time import sleep
from gpiozero import LED
import requests
import paho.mqtt.client as mqtt

#loraModule = serial.Serial('/dev/ttyUSB0', 9600)
loraModule = serial.Serial('/dev/ttyS0', 9600)
# gpsModule = serial.Serial ("/dev/ttyUSB0", 9600, timeout=0.01)
DeviceId = "123456789";
url = 'http://hydrosensex.mukeey.online/actuator/uppdate/node/details'

# GPIO pin 17
valve = LED(17)
AUTOMATIC_MODE = True
def str2bool(v):
  return v in ("yes", "true", "1")

def on_message(client, userdata, message):
    try:
        topic = str(message.topic).split("/")
        payload = json.loads(str(message.payload.decode("utf-8")).strip())
        #print(str2bool(payload['pump']), str2bool(payload['operationMode']))
        if topic[1] == "command":
            global AUTOMATIC_MODE
            AUTOMATIC_MODE = str2bool(payload['operationMode'])
            if str2bool(payload['pump']):
                valve.on()
                print("pump on")
            else :
                valve.off()
                print("pump off")
        #print(valve.value, AUTOMATIC_MODE)
    except :
      #print ("JSon Error")
      pass
    

mqttBroker ="broker.emqx.io"
#mqttBroker ="35.178.174.64"
client = mqtt.Client("SmartAgriculture")
try:
  client.connect(mqttBroker)
  print('mqtt connected') 
except Exception as ex:
  print(ex)
  pass
def formatDegreesMinutes(coordinates, digits):
    
    parts = coordinates.split(".")

    if (len(parts) != 2):
        return coordinates

    if (digits > 3 or digits < 2):
        return coordinates
    
    left = parts[0]
    right = parts[1]
    degrees = left[:digits]
    minutes = right[:3]

    return degrees + "." + minutes

# This method reads the data from the serial port, the GPS dongle is attached to,
# and then parses the NMEA messages it transmits.
# gps is the serial port, that's used to communicate with the GPS adapter

def getPositionData(gps):
    run = True
    while run:
        #print("acquiring GPS data")
        data = gps.readline().decode('utf-8').strip()
        #print (data)
        message = data[0:6]
        if (message == "$GPRMC"):
            # GPRMC = Recommended minimum specific GPS/Transit data
            # Reading the GPS fix data is an alternative approach that also works
            parts = data.split(",")
            if parts[2] == 'V':
                # V = Warning, most likely, there are no satellites in view...
                #print ("GPS receiver warning") #mm
                return "{}"
            else:
                # Get the position data that was transmitted with the GPRMC message
                # In this example, I'm only interested in the longitude and latitude
                # for other values, that can be read, refer to: http://aprs.gids.nl/nmea/#rmc
                longitude = formatDegreesMinutes(parts[5], 3)
                latitude = formatDegreesMinutes(parts[3], 2)
                #print ("Your position: lon = " + str(longitude) + ", lat = " + str(latitude)) #mm
                return "{\"longitude\":\""+longitude+"\", \"latitude\":\""+latitude+"\"}"
        else:
            # Handle other NMEA messages and unsupported strings
            #pass
            return "{}"
          
def sensorRead():
    # In the NMEA message, the position gets transmitted as:
    # DDMM.MMMMM, where DD denotes the degrees and MM.MMMMM denotes
    # the minutes. However, I want to convert this format to the following:
    # DD.MMMM. This method converts a transmitted string to the desired format
    running = True
    while running:
        #print("starting sensor read")  
        try:
            #print("starting GPS")
            #if gpsModule:
            #  gps = getPositionData(gpsModule)
            #else:
            gps = "{}"
            #gps = getPositionData(gpsModule)
            #print("starting Lora")
            nodeA = loraModule.readline().decode().strip()
            nodeB = loraModule.readline().decode().strip()
            valveController(nodeA, nodeB)
            #payload = """{"node":"""+nodeB+""" ,"gps":"""+gps+""" ,"pump":"""+str(valve.value).lower()+""","operationMode":"""+str(AUTOMATIC_MODE).lower()+""" }"""
            payload = """"nodes": {"1":" """+nodeA+"""","2":" """+nodeB+""""},"gps":"""+gps+""" ,"pump":"""+str(valve.value).lower()+""", "device_id": " """+str(DeviceId)+"""", "operationMode":"""+str(AUTOMATIC_MODE).lower()
            #"{\"nodeA\":"+nodeA+",\"nodeB\":"+nodeB+",\"gps\":"+gps+"}"
            print(payload)
            print("")
            
            myobj = {'nodes': {'1': nodeA, '2': nodeB}, 'pump': str(valve.value), 'operationMode': str(AUTOMATIC_MODE), 'device_id':DeviceId}
            #x = requests.get(url, json = myobj)
            #print(x.text)
            
            client.loop_start()
            client.subscribe("smart_farm/command")
            client.on_message=on_message
            client.publish("smart_farm/dataset", payload)
            sleep(1)
            client.loop_stop()
         
        except Exception as ex:
            #running = False
            #gpsModule.close()
            #loraModule.close()
            print ("Sensor read Fails!", ex) #mm
            pass
def valveController(nodeA, nodeB):
    if AUTOMATIC_MODE:
        print("starting valveController====================")
        try:
             #nodex = nodeA #json.loads(nodeA)
             #nodey = nodeB #json.loads(nodeB)
            nodeX = str(nodeA).split(",")
            nodeY = str(nodeB).split(",")

            if int(nodeX[3]) < 10 :
                print("turning off valve")
                valve.off()
            if int(nodeY[3]) < 10:
                print("turning off valve")
                valve.off()
            else:
                print("turning on valve")
                valve.on()
        except:
            print("Error Json")
            pass
    else:
        #TODO: turn valves on or off based on mqtt message
        pass
sensorRead()
