import os
import sys


class MessageProc:

    def _init_(self):
        self.pid = os.getpid()
        pid_conv = str(self.pid)
        self.pipe_name = "/tmp/%s.fifo" % (pid_conv)

    def main(self):

        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

    def start(self):
        os.fork()

    def give(self, pid, message):
        pid_conv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)
        fifo = open(pipe_name, "w")
        fifo.write(message)
        fifo.close()

    def recieve(self, *messages):
        pid = os.getpid()
        pid_conv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        fifo = open(pipe_name, 'r')
        for line in fifo:
            print(line)
        fifo.close()


class Message:

    def _init_(self, id_in, action_in):
        self.name = id_in
        self.action = action_in
