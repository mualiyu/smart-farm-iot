import RPi.GPIO as p
import time

p.setmode(p.BCM)

p.setwarnings(False)

p.cleanup()

p.setup(18, p.OUT)



while True:
	try:
		p.output(18, p.HIGH)
		time.sleep(1)
		p.output(18, p.LOW)
		time.sleep(1)
	except KeyboardInterrupt:
		p.cleanup()
		exit()
		
	
	
	
