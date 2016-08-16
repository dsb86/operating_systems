import os
import sys

class MessageProc()

    def give(name, text, *extras)
        pipe_name = "/tmp/my_program.fifo"
        if not os.path.exists(pipe_name):
        	os.mkfifo(pipe_name)
        fifo = open(pipe_name, "w")
        fifo.write('How are you doing?\n')
        fifo.close()
