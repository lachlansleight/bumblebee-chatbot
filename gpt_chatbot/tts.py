import time
import subprocess
from subprocess import Popen
import os
import re
import requests
import urllib.parse
from threading import Thread
from gpt_chatbot.console_utils import print_center

NEW, GENERATING, GENERATED, PLAYING, PLAYED = range(5)

class TtsMessage:
    id: int
    text: str
    terminator: str
    status: int

    def __init__(self, id, text):
        self.id = id
        self.terminator = text[-1]
        self.text = text.replace("&", "and")
        self.text = re.sub("[^a-zA-Z0-9 ]", "", self.text)
        self.status = NEW

    def __str__(self):
        return "%i (%s) %s" % (self.id, ["NEW", "GENERATING", "GENERATED", "PLAYING", "PLAYED"][self.status], self.text[:20])

class TextToSpeech:
    __message_buffer: list[TtsMessage] = []
    __voice: str = ""
    __debug: bool = False
    __generate_thread: Thread
    __play_thread: Thread
    __next_id: int
    __server_process: Popen

    def __init__(self, voice, debug):
        self.__voice = voice
        self.__debug = debug
        self.__next_id = 1

        self.__server_process = subprocess.Popen(
            ["mimic3-server"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
        )

        self.__play_thread = Thread(target=self.__check_for_play, name="Check for Play", daemon=True)
        self.__play_thread.start()
        self.__generate_thread = Thread(target=self.__check_for_generate, name="Check for Generate", daemon=True)
        self.__generate_thread.start()

        

    def __check_for_play(self):
        while True:
            for message in self.__message_buffer:
                if message.status == PLAYING or message.status == PLAYED:
                    continue
                if message.status == NEW or message.status == GENERATING:
                    continue
                message.status = PLAYING
                self.__say_text_async(message)
                message.status = PLAYED
                if message.terminator == "," or message.terminator == ";": 
                    # minimum pause between phrases (if we have the next audio segment already)
                    time.sleep(0.05)
                elif message.terminator == "!" or message.terminator == "." or message.terminator == "?" or message.terminator == "\n" or message.terminator == ":": 
                    # pause between sentences (if we have the next audio segment already)
                    time.sleep(0.25)
                break
            time.sleep(0)

    def __check_for_generate(self):
        while True:
            for message in self.__message_buffer:
                if message.status != NEW:
                    continue
                message.status = GENERATING
                self.__generate_text_async(message)
                message.status = GENERATED
            time.sleep(0)

    # Adds the text to the queue to be played back
    # The audio file will begin generation right away(ish)
    def say(self, text):
        new_message = TtsMessage(self.__next_id * 1000 + len(text), text)
        self.__message_buffer.append(new_message)
        self.__next_id = self.__next_id + 1

    # Generates and plays an audio file speaking the provided text
    def __say_text_async(self, message: TtsMessage):
        fn = "./audio-gen/ai-%i.wav" % message.id

        # Wait for file generation to complete
        while not os.path.exists(fn):
            time.sleep(0.01)

        subprocess.run(
            ["aplay", fn], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        subprocess.run(["rm", fn])

    def __generate_text_async(self, message: TtsMessage):
        if os.path.exists("./audio-gen/ai-%i.wav" % message.id):
            os.remove("./audio-gen/ai-%i.wav" % message.id)

        lastTime = time.time()
        url = "http://localhost:59125/api/tts?text=%s&voice=%s" % (urllib.parse.quote(message.text), urllib.parse.quote(self.__voice))
        response = requests.get(url)
        with open("./audio-gen/ai-%i.wav" % message.id, mode="bx") as f:
            f.write(response.content)

        if self.__debug: 
            print_center("Got mimic3 TTS audio in %.1fs" % (time.time() - lastTime))

    def __print_message_buffer(self, prefix):
        print(prefix)
        for message in self.__message_buffer:
            print("  %s" % message)
        print("")

    def cleanup(self):
        self.__server_process.kill()
        files = os.listdir("./audio-gen")
        for f in files:
            subprocess.run(["rm", "./audio-gen/" + f])