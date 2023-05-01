import whisper
import time

def main():
    last_time = time.time()
    print("Initializing")
    model = whisper.load_model("base")
    print("Initialized in %.1f" % (time.time() - last_time))

    last_time = time.time()
    result = model.transcribe("./assets/user.wav")
    print(result["text"])
    print("Transcribed in %.1f" % (time.time() - last_time))
