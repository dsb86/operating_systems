import drive
import directoryEntry
import heapq

class Volume:

    SIZE_BITMAP = 128
    SIZE_ENTRY = 64
    SIZE_FNAME = 8
    SIZE_BLOCK_INDEX = 4
    NUM_ROOTFILES = 6
    NUM_FILES = 8
    NUM_BLOCK_INDEX = 12
    INDEX_FNAME = 2
    INDEX_BLOCKS = 16


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
        self.heap_sort(block)

    def reconnect(self):

        self.mydrive.reconnect()
        block = self.mydrive.read_block(0)
        self.heap_sort(block)


    def heap_sort(self, block):
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
                beggining = Volume.INDEX_FNAME + (Volume.SIZE_ENTRY * d)
                end = beggining + len(label)
                if(block[beggining:end]==label):
                    index = d
                    break

            #TODO: Set Loop to be helper function go through
            # blocks

    def find_entry_index(self, name, block_address):
        block_data = self.mydrive.read_block(block_address)
        for index in range(Volume.NUM_FILES):
            beggining = Volume.INDEX_FNAME + (Volume.SIZE_ENTRY * index)
            end = beggining + len(name)
            if (block_data[beggining:end] == name):
                return index

        return -1




    def find_base_directory_address(self, path, block_address):
        name = ""
        entry_index = None
        end = 0

        for c in range(1, Volume.SIZE_FNAME):
            if path[c] == '/':
                end = c
                break

            if c == Volume.SIZE_NAME-1:
                end=-1

        if end == -1:
            return block_address
        else:
            name = path[1:end]
            entry_index = self.find_entry_index(name, block_address)

        if entry_index == -1:
            return -1
        else:
            used_blocks = self.find_used_blocks(block_address, entry_index)
            for block in used_blocks:
                target = self.find_base_directory(path[end:], block)
                if(target != -1):
                    return target

        return -1

    def find_used_blocks(self, block_address, entry_index):
        block_data = self.mydrive.read_block(block_address)
        block_index_beginning = entry_index * Volume.SIZE_BLOCK + Volume.INDEX_BLOCKS
        block_index_end = block_index_beginning + Volume.SIZE_BLOCK_INDEX
        used_blocks=[]
        for c in range(Volume.NUM_BLOCK_INDEX):
            block_index = block_data[block_index_beginning:block_index_end]
            block_num = int(block_index)
            if(block_num != 0):
                used_blocks.append(block_num)

        return used_blocks
















