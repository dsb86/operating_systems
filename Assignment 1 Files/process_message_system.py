import os
import sys

class MessageProc:

    #def _init_(self):


    def main(self):
        self.pid=os.getpid()
        pidConv=str(self.pid)
        self.pipe_name = "/tmp/%s.fifo" % (pidConv)
        if not os.path.exists(self.pipe_name):
        	os.mkfifo(self.pipe_name)

    def start(self):
        os.fork()
        return os.getpid()


    def give(self, pid, message):
        pidConv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pidConv)
        if not os.path.exists(self.pipe_name):
        	os.mkfifo(self.pipe_name)
        fifo = open(pipe_name, "w")
        fifo.write(message)
        fifo.close()

    def recieve(self):
        pid = os.getpid()
        pidConv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pidConv)
        fifo = open(pipe_name, 'r')
        for line in fifo:
            print(line)
        fifo.close()

class Message:

    def _init_(self, idIn, actionIn):
        self.name = idIn
        self.action = actionIn
