import os
import sys

class MessageProc:

    def _init_(self):
        self.pid=""
        self.pipe_name = ""

    def main(self):
        self.pid=os.getpid()
        self.pipe_name = "/tmp/%s.fifo" (str(self.pid))
        if not os.path.exists(self.pipe_name):
        	os.mkfifo(self.pipe_name)

    def give(self, pid, message):
        pipe_name = "/tmp/%d.fifo" (str(pid))
        fifo = open(pipe_name, "w")
        fifo.write(message)
        fifo.close()

    def recieve(self):
        pid = os.getPID
        pipe_name = "/tmp/my_program.fifo"
        fifo = open(pipe_name, 'r')
        for line in fifo:
            print(line)
        fifo.close()

class Message:

    def _init_(self, idIn, actionIn):
        self.name = idIn
        self.action = actionin
