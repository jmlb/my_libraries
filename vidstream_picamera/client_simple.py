
import io
import socket
import struct
import time
import picamera
import argparse


############
# arguments
############
parser = argparse.ArgumentParser(description="Client side-RPi streams Motion pictures")
parser.add_argument('-ip', '--ip_last_number', type=int, help='Last ip number of 192.168.0.xxx', default='108')
parser.add_argument('-W', '--img_width', type=int, help='width of captured image', default='320')
parser.add_argument('-H', '--img_height', type=int, help='height of captured image', default='240')
parser.add_argument('-format', '--img_format', type=str, help='Format of the image (jpeg/yuv, rgb)', default='jpeg')
parser.add_argument('-vidport', '--videoport', help='Use video Port 1 or 0', type=bool, default=1)
parser.add_argument('-capture', '--capture', help='Capture type: sequence (seq/cont)', default='cont')
args = parser.parse_args()



#######################################################################################
# Generator yields empty io.BytesIO object to store the captured image from picamera
#######################################################################################
def gen():
    stream = io.BytesIO()
    while True:
        yield stream
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        stream.seek(0)  #seek to location 0 of stream_img
        connection.write(stream.read())  #write to file
        stream.seek(0)
        stream.truncate()



###########################################################
# setup connection to server
###########################################################
# Connect a client socket to server_ip:8000
client_socket = socket.socket()
ip_address = "192.168.0.{}".format(args.ip_last_number)
client_socket.connect( ( ip_address, 1308 ) )
# Make a file-like object out of the connection
connection = client_socket.makefile('wb')


if __name__ == '__main__':
    try:
        camera.raw_format = args.img_format
        with picamera.PiCamera() as camera:
            camera.resolution = ( args.img_width, args.img_height )
            # Start a preview and let the camera warm up for 2 seconds
            camera.start_preview()
            time.sleep(2)
            camera.stop_preview()
            
            if args.capture == "seq":
                camera.capture_sequence(gen(), args.img_format, use_video_port=args.videoport)
            elif args.capture == "cont":
                camera.capture_continuous(gen(), args.img_format, use_video_port=args.videoport)
            else:
                camera.capture_continuous(gen(), "jpeg", use_video_port=True)
        connection.write(struct.pack('<L', 0))
    finally:
        connection.close()
        client_socket.close()