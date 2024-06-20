import numpy as np
import matplotlib.pyplot as plt

import PySpice
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import PySpice.Logging.Logging as Logging
from PySpice.Probe.WaveForm import WaveForm

import pyaudio
import wave
import time

class voice:
    def __init__(self,Format=pyaudio.paInt16,channels=1,
                 frame_rate=44100,chunk=1024,
                 recording_time=3,audio_file_name="test.wav"):
        self.format=Format
        self.channels=channels
        self.frame_rate=44100
        self.chunk=1024
        self.time=recording_time
        self.voice=[]
        self.rate=frame_rate

        self.audio=pyaudio.PyAudio()
        
        self.stream=stream=self.audio.open(format=self.format,channels=self.channels,
                  rate=self.rate,input=True,frames_per_buffer=self.chunk)

        self.file=wave.open(audio_file_name,"wb")

    def record(self):
        ready=False
        
        while not ready:
            ready=input("Ready to capture your voice? (True\False)")
        
        for i in range(5):
            print("Starting recording in "+str(i+1))
            time.sleep(1)
        print("Now speak....")

        for i in range(int(self.rate/self.chunk*self.time)):
            self.voice.append(self.stream.read(self.chunk))

        print("Recording has been finished")

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        
    def save(self):
        self.file.setnchannels(self.channels)
        self.file.setsampwidth(self.audio.get_sample_size(self.format))
        self.file.setframerate(self.rate)
        self.file.writeframes(b''.join(self.voice))
        self.file.close()

    def output_signal(self):
        return np.array(self.voice)

audio=voice(chunk=512,recording_time=1.5)
audio.record()
audio.save()
audio=audio.output_signal()
audio=np.frombuffer(audio,dtype=np.int16)
time=np.arange(len(audio))/44100
audio_norm=audio/np.max(np.abs(audio))

logger=Logging.setup_logging()

cir=Circuit(" ")

cir.PieceWiseLinearVoltageSource(1,"input",cir.gnd,values=[(i @u_s,j @u_V) for i,j in zip(time,audio_norm)])
cir.R(1,"input","output",10@u_kOhm)

sim=cir.simulator(temperature=25,nominal_temperature=25)
analysis=sim.transient(step_time=time[1]-time[0],end_time=time[-1])

new_voice=analysis["output"]*np.max(audio)
new_voice=[int(i) for i in new_voice]

new_voice_bin=np.array(new_voice,dtype=np.int16).tobytes()

file=wave.open("new_test.wav","wb")

file.setnchannels(1)
file.setsampwidth(2)
file.setframerate(44100)

file.writeframes(new_voice_bin)

file.close()
