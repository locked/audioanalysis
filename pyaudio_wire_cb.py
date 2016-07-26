import pyaudio
import audioop
import time
import datetime

import scipy
import struct
import scipy.fftpack

from Tkinter import *
import threading
import wckgraph
import math


WIDTH = 2
CHANNELS = 1
RATE = 22050

root = Tk()
root.title("SPECTRUM ANALYZER")
root.geometry('500x200')
w = wckgraph.GraphWidget(root)
w.pack(fill=BOTH, expand=1)

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    #print "frame", in_data
    print audioop.max(in_data, 2)
    #data = scipy.array(struct.unpack("%dB"%(1024), in_data))
    out_data = None
    return (out_data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
