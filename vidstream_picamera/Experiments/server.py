import io
import socket
import struct
from PIL import Image
import time



if __name__ == '__main__':
    # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
    # all interfaces)
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 1308))
    server_socket.listen(0)
    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('rb')

    # Parameters
    n_recs = 0
    cnt_streamed_imgs = 0
    summary = []
    n_measurements = 100
    avg_img_len = 0
    W, H = 320, 240

    try:
        test = True
        init = time.time()
        while test:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]

            if not image_len:
                break
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            try:
                #reading jpeg image
                image_stream.write(connection.read(image_len))
                image = Image.open(image_stream)
            except:
                #if reading raw images: yuv or rgb
                image = Image.frombytes('L', (W, H), image_stream.read())
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            avg_img_len += image_len

            elapsed = (time.time() - init)
            cnt_streamed_imgs += 1
            if elapsed > 10 and elapsed < 11:
                #record number of images streamed in about 10secs
                avg_img_len = avg_img_len / cnt_streamed_imgs
                print("{} | Nbr_frames: {} - Elapased Time: {:.2f} | Average img length: {:.1f}]".format(n_recs, cnt_streamed_imgs, elapsed, avg_img_len) )
                summary.append( [cnt_streamed_imgs, elapsed, avg_img_len] )
                n_recs += 1
                #reset counters
                init = time.time()
                cnt_streamed_imgs = 0
                avg_img_len = 0
            if n_recs == n_measurements:
                #Number of measurements
                test = False

            #Write summary
        with open("stream_perf_07.txt", "w") as file:
            file.write("nbr_images, elapsed(sec), avg_img_size\n")
            for record in summary:
                file.write("{}, {}, {}\n".format( record[0], record[1], record[2]))

    finally:
        connection.close()
        server_socket.close()