import socket
import numpy
import numpy as np
import cv2
import pickle
import time

cap = cv2.VideoCapture(0)

delta = 0.2
next_time = time.time() + delta
while(True):
    if time.time() >= next_time:
        # Capture frame-by-frame
        ret, frame = cap.read()


        sock = socket.socket()
        sock.connect(('localhost',8000))
        serialized_data = pickle.dumps(frame)
        sock.sendall(serialized_data)
        sock.close()

        next_time = time.time() + delta

# When everything done, release the capture
cap.release()
