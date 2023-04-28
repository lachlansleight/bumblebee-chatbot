import time
import os
import asyncio
from typing import cast
import whisper

from gpt_chatbot.console_utils import print_right, print_center, print_recording, print_transcribing, clear_last_line
from gpt_chatbot.tts import TextToSpeech
from gpt_chatbot.openai import OpenAi
from gpt_chatbot.recorder import AudioRecorder
from gpt_chatbot.soundplayer import SoundPlayer

async def main_loop():
    # Config vars - should make these command line arguments at some point
    #============================================#
    # The duration of no detected speech to use before transcribing + sending to GPT-4
    dead_time_threshold = 1
    # If no messages are received from the user in this time, the conversation will be wiped
    # This is to save on prompt token spending
    conversation_break_threshold = 120
    # Whether to show debug messages, mostly regarding how long things take
    show_debug = False
    # The audio device ID to use for user speech
    device_id = 0
    # The sensitivity of voice-activation, 0 - 3
    # Higher means it's more aggressive at considering something 'silence'
    vad_sensitivity = 2
    # The voice type to use for text-to-speech
    # https://mycroftai.github.io/mimic3-voices/
    tts_voice = "en_US/hifi-tts_low#92"
    # The Whisper model to use - larger models are more accurate, but much slower
    whisper_model = "base"
    # The system prompt that defines the broad behaviour of the system
    system_prompt = "You are a casual and helpful assistant. Unless more information is requested, you keep your replies as brief as possible. Unless explicitly asked, you do not respond with lists of information."
    #============================================#

    openai = OpenAi(system_prompt)
    tts = TextToSpeech(tts_voice, show_debug)
    soundplayer = SoundPlayer()

    # Show fancy header
    print("")
    total_width = os.get_terminal_size().columns
    os.system("clear")
    print("=" * total_width)
    print_center("GPT-4 Conversation Bot")
    print("=" * total_width)
    
    # Initialize all the audio recording stuff
    print_center("Initializing Audio")
    recorder = AudioRecorder(device_id, vad_sensitivity, dead_time_threshold, show_debug)
    clear_last_line()
    print_center("Initialized Audio with device:")
    print_center(recorder.get_device_name())

    # Initialize Whisper transcription
    print_center("Initializing Whisper")
    model = whisper.load_model(whisper_model)
    clear_last_line()
    print_center("Initialized Whisper with model \"%s\"" % whisper_model)

    # A global variable to keep track of the last user message (for conversation resetting)
    last_message_time = time.time()    

    #Play welcome message
    print("")
    print_center("Initialization Complete.")
    print_center("Say 'Bumblebee' to trigger recording")
    #tts.say("Initialization Complete!")
    #tts.say("Say 'Bumblebee' to trigger recording.")
    soundplayer.play_beep_low()
    soundplayer.play_beep_high()
    print("=" * total_width + "\n")

    # Start recording!
    recorder.start_recording()

    # Will keep running forever until the user performs a keyboard interrupt
    try:
        while True:
            # Clear conversation history if it's been more than the threshold time since the last message
            if time.time() - last_message_time > conversation_break_threshold and openai.completion_tokens > 0:
                print_center("Starting a new conversation.")
                print_center("The last conversation cost %.2f cents" % openai.get_price_cents())
                openai.reset_conversation()

            # Watch for wakeword
            result = recorder.check_for_wakeword()
            if result >= 0:
                # Wakeword detected - begin recording audio from the user
                soundplayer.play_beep_low()
                print_recording()
                await recorder.record_speech()

                # Transcribe speech to text
                lastTime = time.time()
                clear_last_line()
                print_transcribing()
                transcribed = model.transcribe("./audio-gen/user.wav")
                user_message = cast(dict[str, str], transcribed)["text"]
                if show_debug:
                    print_center("Got whisper transcription in %.1f" % (time.time() - lastTime))
                clear_last_line()
                print_right(user_message)

                if len(user_message.strip()) > 0:
                    # User speech detected - get response from OpenAI and play it
                    soundplayer.play_beep_high()
                    await openai.add_message(user_message, tts.say)
                elif show_debug:
                    print("Transcription detected no words, skipping")
                
                last_message_time = time.time()
                recorder.start_recording()


    except KeyboardInterrupt:
        print_center("Keyboard Interrupt Received - Stopping App")
    finally:
        # Cleanup
        recorder.cleanup() # frees resources
        tts.cleanup() # deletes temporary audio files

def main():
    asyncio.run(main_loop())