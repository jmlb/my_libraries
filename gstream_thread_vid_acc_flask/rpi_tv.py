# coding: utf-8

import os
import subprocess
import socket
import time
from adxl345 import adxl345

"""
accelerometer: outputs 0 when object in freefall and -g when at rest (static)
 Accelerometers are used to sense both static (e.g. gravity) and dynamic (e.g. sudden starts/stops) acceleration. 
 They don’t need to be tracked and can measure the current angle at any given time. 
 Accelerometers however are very noisy and are only useful for tracking angles over a long period of time.
http://www.instructables.com/id/Accelerometer-Gyro-Tutorial/
"""


def run_vstreamer():

  new_env = dict(os.environ)
  new_env['DISPLAY'] = '0.0'
  #kill any pre-existing streamer
  try:
      cmd_kill = "killall -9 mjpg_streamer"
      subprocess.Popen(cmd_kill, shell=True)
      print("Killing Gstreamer ....")
      time.sleep(5)

  except:
      print("Could not kill GStreamer")
  
  path_streamer = "/usr/src/mjpg-streamer/mjpg-streamer-experimental/"
  #cmd = "{}mjpg_streamer -o '{}output_http.so -w {}www' -i '{}input_raspicam.so -x 640 -y 480 -fps 30 -ex night' ".format(path_streamer, path_streamer,path_streamer, path_streamer)
  cmd = "{}mjpg_streamer -o '{}output_http.so -w {}www' -i '{}input_raspicam.so -x 320 -y 240 -timestamp -fps 30 -ex night'".format(path_streamer, path_streamer,path_streamer, path_streamer)
  #Make sure to use shell=True, otherwise might get Erro of directory/file does not exists
  subprocess.Popen(cmd, env=new_env, shell=True)
  print("GStreamer started")


def run_tstreamer():

  '''
  Telemetry streaming: sending data to server
  '''
  # Create TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #Then bind() is used to associate the socket with the server address. 
  #In this case, the address is localhost, referring to the current server, 
  #and the port number is 10000.
  server_address = ("", 10000)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(server_address)
  sock.listen(1)
  accel = adxl345.ADXL345()
  while True:
      # Wait for a connection
      connection, client_address = sock.accept()
      #accept() returns an open connection between the server and client, along with the address of the client. 
      #The connection is actually a different socket on another port (assigned by the kernel). 
      #Data is transmitted from the connection with sendall().
      # Receive the data in small chunks and retransmit it
      while True:
          #to get axes as ms**2 False / True in g unit
          axes = accel.getAxes(False)
          x, y, z = axes["x"], axes["y"], axes["z"]
          timestamp = int( time.time() * 1000) #milliseconds
          message = "Accelerometer(x, y, z): {} {} {}".format(x, y, z)
          msg = "{:d}, {},  {}, {}".format(timestamp, x, y, z)
          # assign start/end signature
          start_marker, end_marker =  "xx0", "xxn"
          msg = start_marker + msg + end_marker
          msg_as_bytes = str.encode(msg)
          print(msg)
          connection.sendall(msg_as_bytes)
          time.sleep(0.15)


def run_tstreamer2():
  
  '''
  Original
  Telemetry streaming: sending data to server
  '''
  # Create TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #Then bind() is used to associate the socket with the server address. 
  #In this case, the address is localhost, referring to the current server, 
  #and the port number is 10000.
  server_address = ("", 10000)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(server_address)
  sock.listen(1)
  while True:
      # Wait for a connection
      connection, client_address = sock.accept()
      #accept() returns an open connection between the server and client, along with the address of the client. 
      #The connection is actually a different socket on another port (assigned by the kernel). 
      #Data is transmitted from the connection with sendall().
      # Receive the data in small chunks and retransmit it
      while True:
          message = "Timestamp: {}".format(time.time())
          print(message)
          connection.sendall(b'message')
          time.sleep(0.5)


if __name__ == "__main__":

    run_vstreamer()
    run_tstreamer()
