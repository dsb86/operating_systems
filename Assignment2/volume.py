import drive
import directoryEntry
import heapq

class Volume:

    SIZE_BITMAP = 128
    SIZE_ENTRY = 64
    NUM_ROOTFILES = 6
    NUM_FILES = 8
    INDEX_FNAME = 2


    def __init__(self, vdrive):

        self.drivename = vdrive
        self.mydrive = drive.Drive(vdrive)
        self.heap = []

    def format(self):

        self.mydrive.format()

        block = "+"

        for c in range (Volume.SIZE_BITMAP-1):
            block = "{:s}{:s}".format(block, '-')

        entry = directoryEntry.DirectoryEntry('f', '')
        data = entry.getEntry()

        for c in range (Volume.NUM_ROOTFILES):
            block = "{}{}".format(block, data)

        self.mydrive.write_block(0, block)
        self.heapsort(block)

    def reconnect(self):

        self.mydrive.reconnect()
        block = self.mydrive.read_block(0)
        self.heapsort(block)


    def heapsort(self, block):
        for c in range (Volume.SIZE_BITMAP):
            if block[c] == '-':
                self.heap.append(c)

        heapq.heapify(self.heap)

    def mkfile(self, path):
        eop = False

        indi = []
        for c in range (len(path)):
            if(path[c] == '/'):
                indi.append(c)

        for c in range (len(indi)-1):
            block = self.mydrive.read_block(c)
            label = path[indi[c]:indi[c+1]]
            index = 0;
            for d in range (Volume.NUM_FILES):
                beggining = INDEX_FNAME + 64 *d
                end = beggining + len(label)
                if(block[beggining:end]==label):
                    index = d
                    break

            #TODO: Set Loop to be helper function go through
            # blocks 












