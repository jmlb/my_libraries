import cv2
import urllib.request
import numpy as np
import threading
import socket
from PIL import Image
import os
import datetime


def make_folder(root="images/"):
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d") 
    folder_idx = 0
    directory_name = "{}_{:03d}".format(today, folder_idx)
    dir_exists = False
    while dir_exists== False:
        address = root + directory_name
        if not os.path.exists(address):
            os.makedirs(address)
            dir_exists = True
        else:
            folder_idx += 1
            directory_name = "{}_{:03d}".format(today, folder_idx)
    return address




def video_thread(datafolder):
    '''
    https://stackoverflow.com/questions/3312607/php-binary-image-data-checking-the-image-type
        Check the header to check the format (jpg, png, etc)
        $JPEG = "\xFF\xD8\xFF"
        $GIF  = "GIF"
        $PNG  = "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
        $BMP  = "BM"
        $PSD  = "8BPS"
        $SWF  = "FWS"
        The other ones I wouldn't know right now, but the big 3 (jpeg,gif,png) usually cover 99%. So, compare the first bytes to those string, and you have your answer.

    '''
    stream=urllib.request.urlopen('http://192.168.0.111:8080/?action=stream')
    frame_id = 0
    bytes_= b''
    while True:
        #print("ok")
        bytes_+=stream.read(122024)
        #print(bytes_)
        #print()
        #print()
        start_jpg = bytes_.find(b'\xff\xd8')
        end_jpg = bytes_.find(b'\xff\xd9')
        #Timestamp
        start_timestamp = bytes_.find(b'Timestamp') + len("Timestamp: ")
        end_timestamp = start_jpg - len( "\r\n\r\n" )
        #timestamp = bytes_[start_timestamp:end_timestamp].decode('ascii')
        #Timestamp: 1512200452.557939\r\n\r\n\xff\xd8\
        if start_jpg!=-1 and end_jpg!=-1:
            jpg = bytes_[start_jpg:end_jpg+2]
            bytes_= bytes_[end_jpg+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            #Convert from opencv BGR to RGB
            rgb = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
            #img = np.zeros_like(i)
            #img[:,:,0], img[:,:,1], img[:,:,2] = i[:,:,2], i[:,:,1], i[:,:,0]
            img = Image.fromarray(rgb)
            img.save("{}/img_{}.png".format(datafolder, frame_id))
            
            frame_id += 1
            #cv2.imshow('i',i)
            if cv2.waitKey(1) == 27:
                exit(0)




def data_thread():
    '''
    The server listens to the client(rpi)
`   Listen to server and receive telemetry data
    This is the server
    '''
    #Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Then bind() is used to associate the socket with the server address. 
    #In this case, the address is localhost, referring to the current server, and the port number is 10000.
    # Bind the socket to the port
    server_address = ("", 10000)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)
    #Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.
    sock.listen(1)
    
    while True:

        # Wait for a connection
        connection, client_address = sock.accept()
        #accept() returns an open connection between the server and client, along with the address of the client. 
        #The connection is actually a different socket on another port (assigned by the kernel). 
        #Data is transmitted from the connection with sendall().
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(26)
            if data:
                print("Received data")
                print(data)
            else:
                print("No data  arrived")
                break


def data_thread2():
    '''
    Telemetry streaming: receiving data from raspberry pi
    '''
    # Create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Then bind() is used to associate the socket with the server address. 
    #In this case, the address is localhost, referring to the current server, 
    #and the port number is 10000.
    server_address = ("192.168.0.111", 10000)
    no_data_flag = 0
    sock.connect(server_address)
    while True:
        data = sock.recv(26)
        if data:
            #print("Received data")
            #print(data)
            pass
        else:
            print("No data  arrived")
            no_data_flag += 1
            break
    if no_data_flag == 5:
        sock.close()




if __name__ == "__main__":
    
    #make data folder
    datafolder = make_folder(root="images/")

    t1 = threading.Thread(target=video_thread, args=[datafolder])
    #t2 = threading.Thread(target=data_thread2, args=[])
    t1.start()
    #t2.start()
