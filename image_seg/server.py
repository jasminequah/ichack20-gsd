from __future__ import print_function
import sys
import socket
import numpy
import cv2
import pickle

s = socket.socket()
s.bind((b'',8000))
s.listen(1)
while True:
    c,a = s.accept()
    data = b''
    while True:
        block = c.recv(4096)
        if not block: break
        data += block
    c.close()
    unserialized_input = pickle.loads(data,encoding='bytes')
    cv2.imshow('frame',unserialized_input)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
