# Config vars - should make these command line arguments at some point

# --------------------------------------------------------------------------------
# Behaviour ----------------------------------------------------------------------
# --------------------------------------------------------------------------------
# The duration of no detected speech to use before transcribing + sending to GPT-4
dead_time_threshold = 1

# If no messages are received from the user in this time, the conversation will be wiped
# This is to save on prompt token spending
conversation_break_threshold = 120

# Once the chatbot has finished speaking, it will listen for this long for user input
# without requiring an additional wakeword
# Note - this isn't currently implemented :D
post_response_listen_time = 5

# The system prompt that defines the broad behaviour of the system
system_prompt = "You are a casual and helpful assistant. Unless more information is requested, you keep your replies as brief as possible. Unless explicitly asked, you do not respond with lists of information."

# --------------------------------------------------------------------------------
# Hardware  Devices --------------------------------------------------------------
# --------------------------------------------------------------------------------
# The audio input device ID to use for user speech
device_id = 0

# Whether to run whisper on the GPU or CPU - must be either 'cuda' or 'cpu'
whisper_device = "cuda"

# --------------------------------------------------------------------------------
# Text to Speech -----------------------------------------------------------------
# --------------------------------------------------------------------------------
# The voice type to use for text-to-speech
# https://mycroftai.github.io/mimic3-voices/
tts_voice = "en_US/hifi-tts_low#92"

# Whether to use a local webserver to generate TTS audio files
# (the server is much faster
use_tts_server = True

# --------------------------------------------------------------------------------
# Speech to Text -----------------------------------------------------------------
# --------------------------------------------------------------------------------
# The wakeword to use that will trigger recording
# Options are: americano, blueberry, bumblebee, grapefruit, grasshopper, picovoice, porcupine and terminator
wakeword = 'bumblebee'

# The wakeword sensitivity to use. Higher = more likely to pickup, but more false positivites
wakeword_sensitivity = 0.35

# The sensitivity of voice-detection, 0 - 3
# Higher means it's more aggressive at considering something 'silence'
vad_sensitivity = 2

# The Whisper model to use - larger models are more accurate, but much slower
# Options are tiny, base, small, medium and large
# Apart from 'large', you can add .en to the model name for english only to improve performance
# This performance gain is more significant for the smaller models
whisper_model = "tiny.en"

# --------------------------------------------------------------------------------
# Debugging ----------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Whether to show debug messages, mostly regarding how long things take
show_debug = False