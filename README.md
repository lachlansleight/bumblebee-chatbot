# GPT-4 Chatbot

This is just my spin on the ubiquitous 'gpt 4 voice chatbot' app that everyone's been making. It uses Porcupine for wakeword detection, WebRTC VAD for voice-activation detection, Whisper (locally-run) for transcription, GPT-4 for intelligence and Mimic3 for Text-to-Speech. This means that the only part of the project that isn't run locally is GPT-4 itself. The app could be modified to use something like Alpaca, but it would be much slower and crappier.

I spent most of the time just learning Python since I haven't ever really made anything remotely complicated in Python before, turns out it's great haha.

The main nice feature of this is that lots of things are happening asynchronously - responses from OpenAI are streamed in and sent to the TTS engine one phrase at a time, massively cutting down on the time between the user finishing their query and the first audio coming out of the system (generally only one or two seconds)

It also prints the conversation out as it happens to a sexy console display so that's nice.

The app automatically manages conversation memory, clearing the memory and saving the chat to a JSON file after two minutes (default) of inactivity.

Most of the future work would go into improving the actual chat experience via things like meta-prompts, better system messages, recursive conversation summarization, etc. But for now I'm satisfied enough with how it's turned out!

## Installation

You may need to do more than this, but off the top of my head you will need:

1. To be on ubuntu linux. It may work within other environments, I haven't tried :D
2. Python 3.9 installed and running, I suggest using [pyenv](https://github.com/pyenv/pyenv)
3. [Poetry installed and added to your system's PATH](https://python-poetry.org/docs/)
4. [Mimic3 installed to your environment](https://mycroft-ai.gitbook.io/docs/mycroft-technologies/mimic-tts/mimic-3#installation) - you should be able to run `mimic3 Hello` and hear it speak. Note that if you follow the docs and install it within a venv, you'll need to run this app from within that same environment. I suggest just intalling it globally
5. Your chosen mimic3 voice pre-downloaded. Unless you changed it in config.py, you can install it by running `mimic3 --voice en_US/hifi-tts_low#92 Hello`
5. An API key for both [OpenAI](https://platform.openai.com/signup/) and [Picovoice](https://console.picovoice.ai/signup)
6. An .env file in the root of this repository (next to .gitignore etc) with the lines `openai_key = "your-key-here"` and `picovoice_key = "your-key-here"`
7. To check the `config.py` file, especially the hardware devices section to ensure everything is working
8. Run `poetry install` to automatically download and install all the project dependencies

## Usage

Run `poetry run dev` to start the app! Check out `config.py` for options.

If the wakeword detection isn't working, verify that the audio input device that the console reports its using is the correct one and that it's receiving audio.