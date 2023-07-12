import paho.mqtt.client as mqtt
import picamera
import io
import time

# MQTT broker settings
mqtt_broker = "broker.emqx.io"
mqtt_port = 8083
mqtt_topic = "smart_farm/cameraDataset"

# Initialize the MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port)

# Initialize the Pi camera
camera = picamera.PiCamera()

# Set camera resolution
camera.resolution = (640, 480)

# Set camera framerate
camera.framerate = 30

# Create a stream object to hold the image data
stream = io.BytesIO()

# Capture and publish images continuously
while True:
    try:
        # Capture an image
        camera.capture(stream, format='jpeg', use_video_port=True)
        
        # Convert image data to bytes and publish to MQTT
        client.publish(mqtt_topic, stream.getvalue())
        
        # Reset the stream for the next capture
        stream.seek(0)
        stream.truncate()
        
        # Wait for a moment before capturing the next image
        time.sleep(0.1)
        
    except KeyboardInterrupt:
        # Clean up resources on keyboard interrupt
        camera.close()
        client.disconnect()
        break
