import cv2
import urllib.request
import numpy as np
import threading
import socket
from PIL import Image
import os
import datetime
import argparse


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




def video_thread(datafolder, IP_ADDR):
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
    stream = urllib.request.urlopen("http://"+ IP_ADDR +":8080/?action=stream")
    frame_id =  0
    f = open(datafolder +"/images.txt","w+")
    buffer =b""
    try:
        while True:
            #try statement needed t ostop while loop with keystr
            buffer += stream.read(122024)
            start_jpg = buffer.find(b"\xff\xd8")
            end_jpg = buffer.find(b"\xff\xd9")
            #Timestamp
            start_timestamp = buffer.find(b"Timestamp") + len("Timestamp: ")
            end_timestamp = start_jpg - len( "\r\n\r\n" )
            timestamp = buffer[start_timestamp:end_timestamp].decode('ascii')
            print(timestamp)
            #Timestamp: 1512200452.557939\r\n\r\n\xff\xd8\
            if (start_jpg!=-1) and (end_jpg!=-1) and (start_jpg < end_jpg):
                jpg = buffer[start_jpg:end_jpg+len(b"\xff\xd9")]
                #bytes_= bytes_[end_jpg+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                #Convert from opencv BGR to RGB 
                rgb = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
                #img[:,:,0], img[:,:,1], img[:,:,2] = i[:,:,2], i[:,:,1], i[:,:,0]
                img = Image.fromarray(rgb)
                img.save("{}/img_{:d}.png".format(datafolder, frame_id))
                frame_id += 1
                #f.write("{}, img_{}.png\n".format(timestamp, frame_id ) )
                #cv2.imshow('i',i)
                if cv2.waitKey(1) == 27:
                    exit(0)
                buffer = buffer[end_jpg+len(b"\xff\xd9")::]
                #write to file
                print("write to file file")
                timestamp = int( float(timestamp) * 1000 ) #millisecs
                f.write( "{:d}, img_{:d}.png\n".format(timestamp, frame_id ))
                f.flush()
    except KeyboardInterrupt:
        f.close()
        print("close data socket")
        sock.close()
     


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
    try:
        while True:

            # Wait for a connection
            connection, client_address = sock.accept()
            #accept() returns an open connection between the server and client, along with the address of the client. 
            #The connection is actually a different socket on another port (assigned by the kernel). 
            #Data is transmitted from the connection with sendall().
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(42)
                start_str = data.find("s")
                end_str = data.find("e")
                #Timestamp
                if start_str != -1 and end_str != -1:
                    print("Received data")
                    print(data)
                else:
                    print("No data  arrived")
                    break
    finally:
        f.close()
        print("close data socket")
        sock.close()



def data_thread2(datafolder, IP_ADDR):
    '''
    Telemetry streaming: receiving data from raspberry pi
    '''
    # Create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Then bind() is used to associate the socket with the server address. 
    #In this case, the address is localhost, referring to the current server, 
    #and the port number is 10000.
    server_address = (IP_ADDR, 10000)
    sock.connect(server_address)
    f = open(datafolder+"/telemetry.txt","w+")
    buffer = b''
    start_marker, end_marker = b"xx0", b"xxn"
    try:
        while True:
            buffer_sz = 26
            buffer += sock.recv( buffer_sz)
            if len(buffer) != 0:
                id_start_marker = buffer.find(start_marker) 
                if id_start_marker != -1:
                    data = buffer[id_start_marker + len(start_marker) ::]
                    id_end_marker = data.find(end_marker)
                    if id_end_marker != -1:
                        data = data[0:id_end_marker]
                        data_str = data.decode("utf-8")
                        print(data_str)
                        f.write( "{}".format(data_str+"\n") )
                        f.flush()
                        buffer = buffer[id_start_marker + len(start_marker) + (id_end_marker + len(end_marker)) :]
                else:
                    print("No data  arrived")
    finally:
        f.close()
        print("close data socket")
        sock.close()



def write_html(ip_addr):
    with open("index.html") as file:  
        html = file.read()
        file.close()
    start = html.index('192.168.')
    end = html.index(':8080/')
    new_html = html[0:start] + ip_addr + html[end::]
    f = open("index.html",'w')
    f.write(new_html)
    f.close()




if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="this program stream videos from Raspberry Pi")
    parser.add_argument("-iprpi", "--iprpi", help="ip_address of RPi", type=str)
    args = parser.parse_args()

    #update ip in html file
    write_html(args.iprpi)
    #make data folder
    datafolder = make_folder(root="images/")
    #make html file
    t1 = threading.Thread(target=video_thread, args=[datafolder, args.iprpi])
    t2 = threading.Thread(target=data_thread2, args=[datafolder, args.iprpi])
    t1.start()
    t2.start()