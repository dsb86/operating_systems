import os
import sys
import pickle


class MessageProc:

    def __init__(self):


        self.pid = os.getpid()
        pid_conv = str(self.pid)
        self.pipe_name = "/tmp/%s.fifo" % (pid_conv)

    def main(self):

        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

    def start(self):
        ANY=any
        pid = os.fork()
        if pid == 0:
            self.main()
            sys.exit()
        else:
            return pid

    def give(self, pid, identifier, *args):
        pid_conv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        if not os.path.exists(pipe_name):
            os.mkfifo(pipe_name)
        fifo = open(pipe_name, "w")
        string = '%s\n' % identifier
        fifo.write(identifier)
        fifo.flush()
        fifo.close()

    def receive(self, *messages):
        pid = os.getpid()
        pid_conv = str(pid)
        dicty={};
        for mess in messages:
            val = mess.getDict()
            ident = mess.getIdent()
            dicty[ident]=val

        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        if not os.path.exists(pipe_name):
            os.mkfifo(pipe_name)
        fifo = open(pipe_name, 'r')
        while True:
            for line in fifo:
                print(line)
                # try:
                print(dicty[line]['action']())
                # except KeyError:
                #     return dicty[any]['action']()

class Message:

    def __init__(self, identifier, **function):
        ANY = any
        self.ident = identifier
        self.dicty = function


    def getDict(self):
        return self.dicty

    def getIdent(self):
        return self.ident
