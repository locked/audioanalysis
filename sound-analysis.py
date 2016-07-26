#!/usr/bin/env python
# Written by Yu-Jie Lin
# Public Domain
#
# Deps: PyAudio, NumPy, and Matplotlib
# Blog: http://blog.yjl.im/2012/11/frequency-spectrum-of-sound-using.html

import struct
import wave
import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pyaudio

TITLE = ''
WIDTH = 1024
HEIGHT = 720
FPS = 25.0

nFFT = 512
BUF_SIZE = 4 * nFFT
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050

def callback(data, frame_count, time_info, status):
    N = max(frame_count / nFFT, 1) * nFFT

    # Unpack data, LRLRLR...
    y = np.array(struct.unpack("%dh" % (N * CHANNELS), data)) / MAX_y
    y_L = y[::2]
    y_R = y[1::2]

    Y_L = np.fft.fft(y_L, nFFT)
    Y_R = np.fft.fft(y_R, nFFT)

    # Sewing FFT of two channels together, DC part uses right channel's
    Y = abs(np.hstack((Y_L[-nFFT / 2:-1], Y_R[:nFFT / 2])))

    y_sum = 0
    y2_sum = 0
    for k, y in enumerate(Y):
        if k >= 315 and k <= 325:
            print str(k) + ":" + str(round(y)),
            y_sum += y
        else:
            y2_sum += y
    print
    print y_sum/10.0, y2_sum/490.0

    out_data = None
    return (out_data, pyaudio.paContinue)

p = pyaudio.PyAudio()
MAX_y = 2.0 ** (p.get_sample_size(FORMAT) * 8 - 1)
MAX_y /= 30.0

def main():

  stream = p.open(format=FORMAT,
                  channels=CHANNELS,
                  rate=RATE,
                  input=True,
                  frames_per_buffer=BUF_SIZE,
                  stream_callback=callback)

  stream.start_stream()

  while stream.is_active():
    time.sleep(0.1)

  stream.stop_stream()
  stream.close()
  p.terminate()

if __name__ == '__main__':
  main()
