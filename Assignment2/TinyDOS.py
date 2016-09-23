import volume

class TinyDOS:

    def __init__(self):
        self.myvolume = None

    def main(self):
        connection = input('')

        divider = 0
        while (connection[divider] != ' '):
            divider += 1

        function = connection[:divider]
        arg = connection[divider+1:]



        switch = {'format': self.format, 'reconnect': self.reconnect, any: self.fatal_error}

        while(1):
            data = input('')

            divider = 0
            while (data[divider] != ' '):
                divider += 1

            function = data[:divider]
            arg = [data[:divider + 1:]]

            switch[function](arg)



    def format(self, *arg):
        self.myvolume = volume.Volume(arg[0])
        self.myvolume.format()

    def reconnect(self, *arg):
        self.myvolume = volume.Volume(arg[0])
        self.myvolume.reconnect()

    def fatal_error(self):
        raise IOError('failed to connect to drive')






if __name__== '__main__':


    me = TinyDOS()
    me.main()
