#!/usr/bin/env python
# Written by Yu-Jie Lin
# Public Domain
#
# Deps: PyAudio, NumPy
# Blog: http://blog.yjl.im/2012/11/frequency-spectrum-of-sound-using.html

import os
import sys
import struct
import wave
import time

import numpy as np
import pyaudio

nFFT = 512
BUF_SIZE = 4 * nFFT
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100 #22050

p = pyaudio.PyAudio()

MAX_y = 2.0 ** (p.get_sample_size(FORMAT) * 8 - 1)
MAX_y /= 30.0

last_beep = time.time()


def callback(data, frame_count, time_info, status):
    global last_beep

    N = max(frame_count / nFFT, 1) * nFFT

    # Unpack data, LRLRLR...
    y = np.array(struct.unpack("%dh" % (N * CHANNELS), data)) / MAX_y
    y_L = y[::2]
    y_R = y[1::2]

    Y_L = np.fft.fft(y_L, nFFT)
    Y_R = np.fft.fft(y_R, nFFT)

    # Sewing FFT of two channels together, DC part uses right channel's
    Y = abs(np.hstack((Y_L[-nFFT / 2:-1], Y_R[:nFFT / 2])))

    # 190 191 [192] 193  +  318 [319] 320 321
    freqs = [189, 190, 191, 192, 193, 194, 195, 316, 317, 318, 319, 320, 321, 322]
    ignore = [254, 255, 256, 257]
    y_sum = 0
    y2_sum = 0
    for k, y in enumerate(Y):
        if y > 20 and k not in freqs: print str(k) + ":" + str(round(y)),
        if k in ignore:
            continue
        if k in freqs:
            y_sum += y
        else:
            y2_sum += y
    y_avg, y2_avg = y_sum/len(freqs), y2_sum/(500-len(freqs))
    """
    print y_sum/len(freqs), y2_sum/(500-len(freqs))
    y_sum = 0
    y2_sum = 0
    for k, y in enumerate(Y):
        if y > 30: print str(k),
        #if k >= 310 and k <= 330:
        #    #print str(k) + ":" + str(round(y)),
            y_sum += y
        else:
            y2_sum += y
    print
    #print y_sum/10.0, y2_sum/490.0
    """
    if y_avg > 20 and y2_avg < 2:
        print "Beep detected", y_avg, y2_avg
        last_beep = time.time()

    out_data = None
    return (out_data, pyaudio.paContinue)

def main():
  info = p.get_host_api_info_by_index(0)
  numdevices = info.get('deviceCount')
  input_device_index = None
  for i in range (0, numdevices):
    device_info = p.get_device_info_by_host_api_device_index(0, i)
    if device_info.get('maxInputChannels')>0:
      print "Input Device id ", i, " - ", device_info.get('name')
      input_device_index = i
  if input_device_index is None:
    print "Could not find suitable input device"
    sys.exit(1)
  devinfo = p.get_device_info_by_index(input_device_index)
  print "Selected device is ",devinfo.get('name')
  #if p.is_format_supported(44100.0,  # Sample rate
  #                       input_device=devinfo["index"],
  #                       input_channels=devinfo['maxInputChannels'],
  #                       input_format=pyaudio.paInt16):
  #  print 'Yay!'
  #p.terminate()
  #sys.exit()

  stream = p.open(format=FORMAT,
                  channels=CHANNELS,
                  rate=RATE,
                  input=True,
                  frames_per_buffer=BUF_SIZE,
                  stream_callback=callback,
                  input_device_index=input_device_index)

  stream.start_stream()

  while stream.is_active():
    time.sleep(0.1)
    time_since_last_beep = time.time() - last_beep
    if time_since_last_beep > 5:
       print "Timeout. Time since last beep:" + str(time_since_last_beep)
       cmd = "ssh -XC eadam 'touch /tmp/lock' 2>/dev/null"
    else:
       cmd = "ssh -XC eadam 'rm /tmp/lock' 2>/dev/null"
    os.system(cmd)


  stream.stop_stream()
  stream.close()
  p.terminate()

if __name__ == '__main__':
  main()
