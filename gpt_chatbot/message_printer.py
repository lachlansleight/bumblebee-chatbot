import sys
from colorama import Back, Style

class MessagePrinter:
    __max_width: int
    __in_line: bool
    __cur_line_length: int
    __line_count: int
    __full_text: str
    __color: str

    def __init__(self, max_width, color: str):
        self.__max_width = max_width
        self.__cur_line_length = 0
        self.__line_count = 0
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

        final_length = len(token)

        if not self.__in_line:
            # if we're not in a line 
            # (either because the last token ended with \n or this is the first token)
            # we can just print
            self.__start_line()
            if token[0] == " ":
                sys.stdout.write(token.strip())
                self.__cur_line_length += len(token.strip())
            else:
                sys.stdout.write(token)
                self.__cur_line_length += final_length
        elif self.__cur_line_length + final_length > self.__max_width:
            # we're gonna wrap, so we need to end the line and start a new one
            self.__end_line()
            self.__start_line()
            if token[0] == " ":
                sys.stdout.write(token.strip())
                self.__cur_line_length += len(token.strip())
            else:
                sys.stdout.write(token)
                self.__cur_line_length += final_length
        else:
            # no wrapping, so we just press onwards
            sys.stdout.write(token)
            self.__cur_line_length += final_length

        for i in range(trailing_newlines):
            if i == 0: continue
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
        
    
    def __start_line(self):
        sys.stdout.write(self.__color)
        self.__line_count = self.__line_count + 1
        self.__in_line = True
        sys.stdout.flush()

    def __end_line(self):
        sys.stdout.write(" " * (self.__max_width - self.__cur_line_length))
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.write("\n")
        self.__cur_line_length = 0
        self.__in_line = False
        sys.stdout.flush()
    