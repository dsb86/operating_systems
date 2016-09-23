import volume
import sys

class TinyDOS:

    def __init__(self):
        self.myvolume = None

    def main(self):
        # connection = input('')
        #
        # divider = 0
        # while (connection[divider] != ' '):
        #     divider += 1
        #
        # function = connection[:divider]
        # arg = connection[divider+1:]



        switch = {'format': self.format,
                  'reconnect': self.reconnect,
                  'ls': self.ls,
                  'mkfile': self.mkfile,
                  'mkdir': self.mkdir,
                  'append': self.append,
                  'print': self.print,
                  'delfile': self.delfile,
                  'deldir': self.deldir,
                  'quit': self.quit,
                  any: self.fatal_error}

        while(1):
            go = True;
            while(go):
                try:
                    line = input('')
                    if(line != ""):
                        go =False
                except EOFError:
                    quit()

            arg = []

            indexes = []

            for c in range(len(line)):

                if line[c]==' ':
                    indexes.append(c)

                if(len(indexes)==2):
                    break
            if(len(indexes) != 0):
                function = line[:indexes[0]]
            else:
                function = line

            for c in range(len(indexes)):
                if(c==len(indexes)-1):

                    arg.append(line[indexes[c] + 1:])

                else:

                    arg.append(line[indexes[c] + 1:indexes[c+1]])


            switch[function](arg)



    def format(self, arg = []):
        # 
        # string = arg[0]
        string = arg[0]
        self.myvolume = volume.Volume(string)
        self.myvolume.format()

    def reconnect(self, arg = []):
        # 
        # string = arg[0]
        string = arg[0]
        self.myvolume = volume.Volume(string)
        self.myvolume.reconnect()

    def ls(self, arg = []):
        
        string = arg[0]
        self.myvolume.ls(string)

    def mkfile(self, arg = []):
        
        string = arg[0]
        self.myvolume.mkfile(string)

    def mkdir(self, arg = []):
        
        string = arg[0]
        self.myvolume.mkdir(string)

    def append(self, arg = []):
        
        string = arg[0]

        string2 = arg[1]
        string2 = string2[1:-1]
        self.myvolume.append(string, string2)

    def print(self, arg = []):
        
        string = arg[0]
        self.myvolume.print(string)

    def delfile(self, arg = []):
        
        string = arg[0]
        self.myvolume.delfile(string)

    def deldir(self, arg = []):
        
        string = arg[0]
        self.myvolume.deldir(string)

    def quit(self, arg = []):
        sys.exit()

    def fatal_error(self):
        raise IOError('failed to connect to drive')






if __name__== '__main__':


    me = TinyDOS()
    me.main()
