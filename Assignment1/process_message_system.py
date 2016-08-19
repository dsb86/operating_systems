# Daniel Brotman
# dbro761
# Augist 2016

import os
import pickle
import time
import threading
import queue

ANY = any


class MessageProc:

    def __init__(self):
        # initialize variables
        self.pid = None
        self.pipe_name = None
        self.arrived_condition = None
        self.communication_queue = None

    def main(self):
        # set pip and pipe name
        self.pid = os.getpid()
        self.pipe_name = "/tmp/{}.pkl".format(self.pid)

        # create queue for message queueing
        self.communication_queue = queue.Queue()

        # from Robert's lecture
        self.arrived_condition = threading.Condition()
        transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True)
        transfer_thread.start()

    def start(self):
        # fork
        pid = os.fork()

        if pid == 0:
            # run main in child process
            self.main()
        else:
            # register child with parent
            return pid

    def give(self, pid, *args):
        # open desired pipe file for writing
        pipe_out = "/tmp/{}.pkl".format(pid)
        pickle_file = open(pipe_out, 'wb', buffer=0)
        # pickle data
        pickle.dump(args, pickle_file)
        # close pickle file
        pickle_file.close()

    def receive(self, *messages):
        # create a dictionary for stored messages
        dicty={}

        for mess in messages:
            # action
            val = mess.getDict()
            # key
            ident = mess.getIdent()

            dicty[ident] = val

        # blocking read
        while True:
            # wait until queue has data
            with self.arrived_condition:
                self.arrived_condition.wait()
                # read what is in the queue
                while not self.communication_queue.empty():
                    data = self.communication_queue.get()
                    try:
                        # see if there are extra arguments
                        if len(data)>1:
                            return dicty[data[0]]['action'](data[1])
                        else:
                            return dicty[data[0]]['action']()
                    except KeyError:
                        # handle unregistered key
                        if len(data)>1:
                            return dicty[ANY]['action'](data[1])
                        else:
                            return dicty[ANY]['action']()


    # from Robert's Lecture
    def extract_from_pipe(self):

        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

        with open(self.pipe_name, 'rb') as unpickle_file:
            while True:
                try:
                    line = pickle.load(unpickle_file)

                    with self.arrived_condition:
                        self.communication_queue.put(line)
                        self.arrived_condition.notify()
                except EOFError:
                    time.sleep(0.01)



class Message:

    def __init__(self, identifier, **function):
        self.ident = identifier
        self.dicty = function

    def getDict(self):
        return self.dicty

    def getIdent(self):
        return self.ident
