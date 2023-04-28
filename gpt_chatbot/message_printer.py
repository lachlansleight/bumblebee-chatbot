import sys
from colorama import Back, Style
from gpt_chatbot.console_utils import clear_last_line

class MessagePrinter:
    __max_width: int
    __in_line: bool
    __cur_line_length: int
    __line_count: int
    __lines: list[str]
    __max_line_length: int
    __full_text: str
    __color: str

    def __init__(self, max_width, color = Back.BLUE):
        self.__max_width = max_width
        self.__cur_line_length = 0
        self.__max_line_length = 0
        self.__line_count = 0
        self.__lines = []
        self.__color = color
        self.__in_line = False
        self.__full_text = ""

    def add_token(self, token: str):
        if len(token) == 0:
            return
        
        self.__full_text = self.__full_text + token
        # print({"t": token})

        # print newlines before the token
        while len(token) > 0 and token[0] == "\n":
            if self.__in_line:
                self.__end_line()
            else:
                self.__start_line()
                self.__end_line()
            token = token[1:]

        if len(token) == 0:
            return

        trailing_newlines = 0
        while(len(token) > 0 and token[-1] == "\n"):
            trailing_newlines = trailing_newlines + 1
            token = token[:-1]

        if not self.__in_line:
            # if we're not in a line 
            # (either because the last token ended with \n or this is the first token)
            # we can just print
            self.__start_line()
            if token[0] == " ":
                self.__write(token.strip())
            else:
                self.__write(token)
        elif self.__cur_line_length + len(token) > self.__max_width:
            # we're gonna wrap, so we need to end the line and start a new one
            self.__end_line()
            self.__start_line()
            if token[0] == " ":
                self.__write(token.strip())
            else:
                self.__write(token)
        else:
            # no wrapping, so we just press onwards
            self.__write(token)

        if self.__cur_line_length > self.__max_line_length:
            self.__set_max_line_length(self.__cur_line_length)

        if trailing_newlines > 0:
            for i in range(trailing_newlines):
                if self.__in_line:
                    self.__end_line()
                else:
                    self.__start_line()
                    self.__end_line()

        sys.stdout.flush()

    def finalize(self):
        if self.__in_line:
            self.__end_line()
            sys.stdout.flush()
        

    def __write(self, text: str):
        sys.stdout.write(text)
        self.__lines[-1] += text
        self.__cur_line_length += len(text)
    
    def __start_line(self):
        sys.stdout.write(self.__color)
        self.__line_count = self.__line_count + 1
        self.__in_line = True
        self.__lines.append("")
        sys.stdout.flush()

    def __end_line(self):
        sys.stdout.write(" " * (self.__max_line_length - self.__cur_line_length))
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.write("\n")
        self.__cur_line_length = 0
        self.__in_line = False
        sys.stdout.flush()

    # This lets the background whitespace expand to fit the new maximum line length
    # pretty sweet
    def __set_max_line_length(self, new_length):
        self.__max_line_length = new_length
        if len(self.__lines) < 2: return

        # Go back to the start
        for i in range(len(self.__lines) - 1):
            sys.stdout.write("\033[F")

        for i in range(len(self.__lines)):
            if i != len(self.__lines) - 1:
                self.__lines[i] += (" " * (self.__max_line_length - len(self.__lines[i])))

            sys.stdout.write(self.__lines[i])

            if i != len(self.__lines) - 1:
                sys.stdout.write("\n")