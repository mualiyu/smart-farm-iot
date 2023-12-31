import io
import socket
import struct
import time
from picamera import PiCamera

while True:
    try:
        client_socket = socket.socket()

       # client_socket.connect(('192.168.43.134', 8000))  # ADD IP HERE
        client_socket.connect(('35.178.174.64', 8000))  # ADD IP HERE

        # Make a file-like object out of the connection
        connection = client_socket.makefile('wb')
        camera = PiCamera()
        print('image snaped')
        camera.vflip = True
        camera.resolution = (480, 360)
        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(2)

        # Note the start time and construct a stream to hold image data
        # temporarily (we could write it directly to connection but in this
        # case we want to find out the size of each capture first to keep
        # our protocol simple)
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send the image data over the wire
            stream.seek(0)
            connection.write(stream.read())
            # If we've been capturing for more than 30 seconds, quit
            #if time.time() - start > 60:
            #    break
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
        # Write a length of zero to the stream to signal we're done
        
    except ConnectionRefusedError:
        pass
    except BrokenPipeError:
        pass
    except:
        connection.write(struct.pack('<L', 0))
        connection.close()
#        client_socket.close()
        pass

connection.close()
client_socket.close()