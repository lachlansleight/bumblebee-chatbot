import subprocess

class SoundPlayer:
    __beep_low: str
    __beep_high: str

    def __init__(self):
        # do nothing
        self.__beep_low = "./assets/beep_low.wav"
        self.__beep_high = "./assets/beep_high.wav"
    
    def __play_sound(self, path):
        subprocess.Popen(
            ["aplay", path], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )

    def play_beep_low(self):
        self.__play_sound(self.__beep_low)

    def play_beep_high(self):
        self.__play_sound(self.__beep_high)
