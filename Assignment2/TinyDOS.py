import volume

class TinyDOS:

    def __init__(self, vdrive):
        self.myvolume= volume.Volume(vdrive)

    def main(self):


    def format(self):
        self.myvolume.format()

    def reconnect(self):
        self.myvolume.format()





if __name__== 'main':
    connection = input()
    divider = 0
    while(connection[divider] != ' '):
        divider += 1

    function = connection[:divider]
    arg = connection[:divider+1:]

    switch
