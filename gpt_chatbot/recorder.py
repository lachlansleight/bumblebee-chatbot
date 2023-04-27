import time
import os
import struct
import wave
import subprocess

from pvporcupine import Porcupine, create
from pvrecorder import PvRecorder
from webrtcvad import Vad

from gpt_chatbot.console_utils import print_center

class AudioRecorder:

    __recorder: PvRecorder
    __vad: Vad
    __porcupine: Porcupine
    __device_name: str

    __sample_rate: int
    __frame_length: int

    __dead_time_threshold: float
    __debug: bool


    def __init__(self, device_id = 0, vad_sensitivity = 2, dead_time_threshold = 0.5, debug = False):
        #print_center("Audio Input Devices:")
        #for i, device in enumerate(PvRecorder.get_audio_devices()):
        #    print_center("[%d]: %s" % (i, device))
        #print("")

        # Initialize porcupine wakeword detector
        self.__porcupine = create(access_key=os.environ.get("picovoice_key"), keywords=['bumblebee'])

        self.__sample_rate = self.__porcupine.sample_rate
        self.__frame_length = self.__porcupine.frame_length

        # Initialize audio recorder
        self.__recorder = PvRecorder(device_index=device_id, frame_length=self.__frame_length)
        self.__device_name = PvRecorder.get_audio_devices()[device_id]

        # Initialize Voice Activation Detector
        self.__vad = Vad()
        self.__vad.set_mode(vad_sensitivity)

        if not os.path.exists("./audio-gen"):
            os.mkdir("./audio-gen")

        self.__dead_time_threshold = dead_time_threshold

        self.__debug = debug

    def get_device_name(self):
        return self.__device_name

    # Takes in user input and saves it to a wav file once a long enough gap is detected
    async def record_speech(self):
        frames = []
        deadTime = 0
        lastTime = time.time()

        while True:
            newData = self.__recorder.read()
            frames.extend(newData)

            vadBytes = b''.join(struct.pack('<h', sample) for sample in newData[:480])
            isDead = not self.__vad.is_speech(vadBytes, self.__sample_rate)
            if isDead:
                deadTime += self.__frame_length / self.__sample_rate
            else:
                deadTime = 0
            if deadTime > self.__dead_time_threshold: #silence -> records wav file and sends to GPT-4
                self.stop_recording()
                if self.__debug:
                    print_center("Finished recording, duration is %.1fs" % (time.time() - lastTime - 0.5))
                with wave.open("./audio-gen/user.wav", "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.__porcupine.sample_rate)
                    wf.writeframes(b''.join(struct.pack('<h', sample) for sample in frames))
                break

    def check_for_wakeword(self):
        pcm = self.__recorder.read()
        result = self.__porcupine.process(pcm)
        return result

    def start_recording(self):
        self.__recorder.start()

    def stop_recording(self):
        self.__recorder.stop()

    def cleanup(self):
        self.__recorder.delete()
        self.__porcupine.delete()
        if os.path.exists("./audio-gen/user.wav"):
            subprocess.run(["rm", "./audio-gen/user.wav"])
        