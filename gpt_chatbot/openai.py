import os
import sys
import openai
import asyncio
import time
import json
from tiktoken import get_encoding, Encoding
from typing import cast
from colorama import Back, Style

from gpt_chatbot.console_utils import clear_last_line, print_thinking

class OpenAi:
    prompt_tokens = 0
    completion_tokens = 0

    __encoding: Encoding # tiktoken tokenizer encoding
    __system_message: str = ""
    __system_tokens: int = 0
    __messages: list[dict[str, str]] = []

    def __init__(self, system_message):
        openai.api_key = os.environ.get("openai_key")
        self.__encoding = get_encoding("cl100k_base") # This was weirdly hard to find out
        self.__system_message = system_message
        self.__system_tokens = len(self.__encoding.encode(self.__system_message))
        self.reset_conversation()

    # Runs an asynchronous streamed completion, keeping track of token counts
    # A callback is raised each time a phrase/sentence is completed (if it's at least 5 words)
    async def __doAsyncCompletion(self, messages, on_sentence_received):
        print_thinking()

        text = ""
        all_text = ""
        written_length = 0
        lines = 0
        console_width = int(os.get_terminal_size().columns/1.25)

        # Actually trigger the streaming response
        self.prompt_tokens = self.prompt_tokens + len(self.__encoding.encode(messages[-1]["content"]))
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages, stream=True)
        
        clear_last_line()
        for chunk in response:
            new_text = cast(dict[str, list[dict[str, dict[str, str]]]], chunk)["choices"][0]["delta"].get("content", "")
            if not new_text == "":
                # Manage printing pretty messages to the console
                if written_length + len(new_text) > console_width:
                    sys.stdout.write(Back.BLUE + (" " * (console_width - written_length)) + Style.RESET_ALL)
                    sys.stdout.write("\n")
                    lines = lines + 1
                    written_length = 0
                if new_text[0] == " " and written_length == 0:
                    sys.stdout.write(Back.BLUE + new_text.strip() + Style.RESET_ALL)
                    written_length = written_length + len(new_text) - 1
                else:
                    sys.stdout.write(Back.BLUE + new_text + Style.RESET_ALL)
                    written_length = written_length + len(new_text)
                sys.stdout.flush()

                # Add the new token to the text buffer and record its token count
                text = text + new_text
                all_text = all_text + new_text
                self.completion_tokens = self.completion_tokens + len(self.__encoding.encode(new_text))

            # When we receive a comma or sentence-ending, if the current phrase is long enough,
            # we emit a sentence_received event to send it to TTS
            # This lets the AI speak while it's still generating tokens for long responses
            if len(text.split(" ")) > 5 and (new_text == "." or new_text == "," or new_text == "\n") or new_text == "!" or new_text == "?":
                on_sentence_received(text)
                text = ""

        if len(text) > 0:
            on_sentence_received(text)

        if lines > 0:
            sys.stdout.write(Back.BLUE + (" " * (console_width - written_length)) + Style.RESET_ALL)
        sys.stdout.write("\n")
        sys.stdout.flush()
        print("")
        self.__messages.append({"role": "assistant", "content": all_text})

    # Adds a new user message to the conversation and requests a response from GPT-4
    def add_message(self, message, on_sentence_received):
        self.__messages.append({"role": "user", "content": message})
        return asyncio.create_task(self.__doAsyncCompletion(self.__messages, on_sentence_received))
    
    # Resets messages and token counts, plus saves a JSON file of the conversation
    def reset_conversation(self):
        # Print conversation to JSON
        if(len(self.__messages) > 1):
            if not os.path.exists("./conversations"):
                os.mkdir("./conversations")
            with open("./conversations/%i.json" % round(time.time()), "w") as f:
                f.write(json.dumps({
                    "messages": self.__messages, 
                    "usage": {
                        "prompt_tokens": self.prompt_tokens,
                        "completion_tokens": self.completion_tokens,
                        "total_tokens": (self.completion_tokens + self.prompt_tokens),
                        "price_cents_usd": self.get_price_cents()
                    }}, indent=2))
                
        # Reset messages to just the system prompt and reset token counts
        self.completion_tokens = 0
        self.prompt_tokens = self.__system_tokens
        self.__messages = [{"role": "system", "content": self.__system_message}]

    # Returns the cumulative price so far in cents (USD), based on GPT-4 8k pricing
    def get_price_cents(self):
        return (self.prompt_tokens * 0.003 + self.completion_tokens * 0.006)