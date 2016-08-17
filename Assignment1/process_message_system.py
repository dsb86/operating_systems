import os
import sys


class MessageProc:

    def __init__(self):
        print("initialized")
        self.pid = os.getpid()
        pid_conv = str(self.pid)
        self.pipe_name = "/tmp/%s.fifo" % (pid_conv)

    def main(self):

        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

    def start(self):
        print(os.getpid())
        pid = os.fork()
        if pid == 0:
            return os.getpid()

    def give(self, pid, message):
        pid_conv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        if not os.path.exists(pipe_name):
            os.mkfifo(pipe_name)
        fifo = open(pipe_name, "w")
        fifo.write(message)
        fifo.close()

    def recieve(self, *messages):
        pid = os.getpid()
        pid_conv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        fifo = open(pipe_name, 'r')
        for line in fifo:
            text = line.getName()
            for mess in messages:
                if mess.getName()==text:
                    line.getAction()()

        fifo.close()

class Message:

    def __init__(self, id_in, action_in):
        self.name = id_in
        self.action = action_in
        print(id_in)

    def getName(self):
        return self.name

    def getAction(self):
        return self.action
