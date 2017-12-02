import cv2
import urllib.request
import numpy as np
 
stream=urllib.request.urlopen('http://192.168.0.111:8080/?action=stream')
bytes_=b''
while True:
    bytes_+=stream.read(1024)
    a = bytes_.find(b'\xff\xd8')
    b = bytes_.find(b'\xff\xd9')
    if a!=-1 and b!=-1:
        print("OK")
        jpg = bytes_[a:b+2]
        bytes_= bytes_[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('i',i)
        if cv2.waitKey(1) == 27:
            exit(0)