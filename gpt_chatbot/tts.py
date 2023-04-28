import time
import subprocess
import os
import re
from threading import Thread
from gpt_chatbot.console_utils import print_center

NEW, GENERATING, GENERATED, PLAYING, PLAYED = range(5)

class TtsMessage:
    id: int
    text: str
    status: int

    def __init__(self, id, text):
        self.id = id
        self.text = text.replace("&", "and")
        self.text = re.sub("[^a-zA-Z ]", "", self.text)
        self.status = NEW

    def __str__(self):
        return "%i (%s): %s" % (self.id, ["NEW", "GENERATING", "GENERATED", "PLAYING", "PLAYED"][self.status], self.text[:20])

class TextToSpeech:
    __message_buffer: list[TtsMessage] = []
    __voice: str = ""
    __debug: bool = False
    __generate_thread: Thread
    __play_thread: Thread
    __next_id: int

    def __init__(self, voice, debug):
        self.__voice = voice
        self.__debug = debug
        self.__next_id = 1

        self.__play_thread = Thread(target=self.__check_for_play, name="Check for Play")
        self.__play_thread.start()
        self.__generate_thread = Thread(target=self.__check_for_generate, name="Check for Generate")
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
                time.sleep(0.05)
                break

    def __check_for_generate(self):
        while True:
            for message in self.__message_buffer:
                if message.status != NEW:
                    continue
                message.status = GENERATING
                self.__generate_text_async(message)
                message.status = GENERATED
            time.sleep(0.05)

    # Adds the text to the queue to be played back
    # The audio file will begin generation right away(ish)
    def say(self, text):
        new_message = TtsMessage(self.__next_id, text)
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
        lastTime = time.time()
        subprocess.run(
            ["mimic3", "--voice", self.__voice, "ai-%i|%s" % (message.id, message.text), "--output-dir", "./audio-gen", "--csv"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        if self.__debug: 
            print_center("Got mimic3 TTS audio in %.1fs" % (time.time() - lastTime))

    def __print_message_buffer(self, prefix):
        print(prefix)
        for message in self.__message_buffer:
            print("  %s" % message)
        print("")

    def cleanup(self):
        files = os.listdir("./audiogen")
        for f in files:
            subprocess.run(["rm", f])