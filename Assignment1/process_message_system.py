import os
import sys
import pickle
import time

ANY = any


class MessageProc:

    def __init__(self):
        self.pid = ''
        self.pipe_name = ''

    def main(self):
        self.pid = os.getpid()
        pid_conv = str(self.pid)
        self.pipe_name = "/tmp/%s.fifo" % (pid_conv)

    def start(self):

        pid = os.fork()
        if pid == 0:
            self.main()
            sys.exit()
        else:
            return pid

    def give(self, pid, identifier, *args):
        pid_conv = str(pid)
        pipe_name = "/tmp/%s.fifo" % (pid_conv)
        pickle_file = open(pipe_name, 'wb')
        print(identifier)
        pickle.dump(identifier,pickle_file)
        pickle_file.close()


    def receive(self, *messages):
        pid = os.getpid()
        pid_conv = str(pid)
        dicty={}
        for mess in messages:
            val = mess.getDict()
            ident = mess.getIdent()
            dicty[ident]=val

        pipe_name = "/tmp/%s.fifo" % (pid_conv)


        unpickle_file = open(pipe_name, 'rb')
        while True:
            try:
                line = pickle.loads(unpickle_file)
                print(line)
                try:
                    print('yup')
                    return dicty[line]['action']()
                except KeyError:
                    print('errpe')
                    return dicty[any]['action']()
            except EOFError:
                print('sleep')
                time.sleep(1)


class Message:

    def __init__(self, identifier, **function):
        self.ident = identifier
        self.dicty = function

    def getDict(self):
        return self.dicty

    def getIdent(self):
        return self.ident
