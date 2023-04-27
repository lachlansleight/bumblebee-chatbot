import os
import sys
import textwrap
from colorama import Back, Style

console_width = os.get_terminal_size().columns
chat_width = int(console_width * 0.8)

# For printing messages from the AI - left aligned, blue background
def print_left(text):
    wrapper = textwrap.TextWrapper(width=chat_width)
    lines = wrapper.wrap(text=text)
    for el in lines:
        print(Back.BLUE + el + Style.RESET_ALL)

# For printing messages from the user - right aligned, magenta background
def print_right(text):
    wrapper = textwrap.TextWrapper(width=chat_width)
    lines = wrapper.wrap(text=text)
    
    max_len = 0
    for el in lines:
        max_len = max(max_len, len(el))
    indent_amount = " " * (console_width - max_len)
    for el in lines:
        rpadding = " " * (console_width - len(indent_amount + el))
        print(indent_amount + Back.MAGENTA + el + rpadding + Style.RESET_ALL)
    print("")

# For printing system messages - system aligned, no background
def print_center(text):
    wrapper = textwrap.TextWrapper(width=chat_width)
    lines = wrapper.wrap(text=text)
    for el in lines:
        print(el.center(console_width))

def clear_last_line():
    sys.stdout.write("\033[F" + (" " * (console_width - 1)) + "\r")

def print_recording():
    print((Back.RED + "Recording..." + Style.RESET_ALL).center(console_width))

def print_transcribing():
    print((Back.GREEN + "Transcribing..." + Style.RESET_ALL).center(console_width))

def print_thinking():
    print((Back.GREEN + "Thinking..." + Style.RESET_ALL).center(console_width))