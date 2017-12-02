import os
import subprocess
import socket
import time

def run_gstreamer():

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
  print("GStreamer staterted")


def run_tstreamer():

  '''
  Telemetry streaming: sending data to server
  '''
  # Create TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #Then bind() is used to associate the socket with the server address. 
  #In this case, the address is localhost, referring to the current server, 
  #and the port number is 10000.
  server_address = ("192.168.0.108", 10000)
  sock.connect(server_address)

  #try:
  while True:
      message = "Timestamp: {}".format(time.time())
      sock.sendall(message)
      time.sleep(0.5)

  #finally:
  #  print("Closing socket")
  #  sock.close()


def run_tstreamer2():
  
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
  while True:
      # Wait for a connection
      connection, client_address = sock.accept()
      #accept() returns an open connection between the server and client, along with the address of the client. 
      #The connection is actually a different socket on another port (assigned by the kernel). 
      #Data is transmitted from the connection with sendall().
      # Receive the data in small chunks and retransmit it
      while True:
          message = "Timestamp: {}".format(time.time())
          connection.sendall(message)
          time.sleep(0.5)


if __name__ == "__main__":

    run_gstreamer()
    run_tstreamer2()
