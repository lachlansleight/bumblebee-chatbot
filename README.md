# GPT-4 Chatbot

This is just my spin on the ubiquitous 'gpt 4 voice chatbot' app that everyone's been making. It uses Porcupine for wakeword detection, WebRTC VAD for voice-activation detection, Whisper (locally-run) for transcription, GPT-4 for intelligence and Mimic3 for Text-to-Speech.

This means that the only part of the project that isn't run locally is GPT-4 itself. The app could be modified to use something like Alpaca, but it would be much slower and crappier.

I spent most of the time just learning Python since I haven't ever really made anything remotely complicated in Python before, turns out it's great haha.

The main nice feature of this is that lots of things are happening asynchronously - responses from OpenAI are streamed in and sent to the TTS engine one phrase at a time, massively cutting down on the time between the user finishing their query and the first audio coming out of the system (generally only one or two seconds)

It also prints the conversation out as it happens to a sexy console display so that's nice.

The app automatically manages conversation memory, clearing the memory and saving the chat to a JSON file after two minutes (default) of inactivity.

Most of the future work would go into improving the actual chat experience via things like meta-prompts, better system messages, recursive conversation summarization, etc. But for now I'm satisfied enough with how it's turned out!