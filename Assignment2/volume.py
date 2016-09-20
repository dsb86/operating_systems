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
    OPEN_ENTRY = "f:        "
    HEAD_DIRECTORY = "d:"
    HEAD_FILE = "f:"
    ROOT = 0


    def __init__(self, vdrive):

        self.drivename = vdrive
        self.mydrive = drive.Drive(vdrive)
        self.heap = []

    # NOTE: Works
    def format(self):

        self.mydrive.format()

        block = "+"

        for c in range (Volume.SIZE_BITMAP-1):
            block = "{:s}{:s}".format(block, '-')

        entry = directoryEntry.DirectoryEntry('f', '')
        data = entry.getEntry()

        for c in range (Volume.NUM_ROOTFILES):
            block = "{}{}".format(block, data)

        self.mydrive.write_block(Volume.ROOT, block)
        self.heap_sort(block)

    # NOTE: Works
    def reconnect(self):

        self.mydrive.reconnect()
        block = self.mydrive.read_block(Volume.ROOT)
        self.heap_sort(block)


    def heap_sort(self, block):
        for c in range (Volume.SIZE_BITMAP):
            if block[c] == '-':
                self.heap.append(c)

        heapq.heapify(self.heap)

    def mkfile(self, path):
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        file_name = self.parse_name(path)
        block_to_modify = None
        index_to_modify = None

        if(directory_address != Volume.ROOT):
            directory_name = self.parse_name(path[:-len(file_name)])
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)

            full_address = self.find_entry_in_directory(Volume.OPEN_ENTRY, directory_name, directory_address)
            #TODO: Expand directory if no space found
            block_to_modify = full_address[0]
            index_to_modify = full_address[1]
        else:
            block_to_modify = Volume.ROOT
            index_to_modify = self.find_entry_index(Volume.OPEN_ENTRY, Volume.ROOT)

        # NOTE: Works
        original_block = self.mydrive.read_block(block_to_modify)
        file_name= "{}{}".format(Volume.HEAD_FILE, file_name)
        insertion_index = index_to_modify * Volume.SIZE_ENTRY
        file_name_length = len(file_name) + insertion_index
        new_block = "{}{}{}".format(original_block[:insertion_index], file_name, original_block[file_name_length:])
        self.mydrive.write_block(block_to_modify, new_block)

    # NOTE: Works
    def find_entry_index(self, name, block_address):
        block_data = self.mydrive.read_block(block_address)
        for index in range(Volume.NUM_FILES):
            beggining = Volume.SIZE_ENTRY * index
            end = beggining + len(name)
            if (block_data[beggining:end] == name):
                return index

        return -1




    def find_base_directory_address(self, path, block_address):
        name = ""
        entry_index = None
        end = 0
        boundary = Volume.SIZE_FNAME
        if boundary > len(path):
            boundary = len(path)
        for c in range(1, boundary):
            if path[c] == '/':
                end = c
                break

            if c == boundary-1:
                end=-1

        if end == -1:
            return block_address
            # NOTE: Works Up To Here For Sure
        else:
            name = path[1:end]
            name = "{}{}".format(Volume.HEAD_DIRECTORY, name)
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

    # NOTE: Works
    def parse_name(self, path):
        for c in range(len(path)-1, -1, -1):
            if(path[c]=='/'):
                name = path[c+1:]
                return name

    def find_entry_in_directory(self, entry, directory_name, directory_address):
        directory_index = self.find_entry_index(directory_name, directory_address)
        used_blocks = self.find_used_blocks(directory_address, directory_index)
        for block in used_blocks:
            entry_index = self.find_entry_index(entry, block)
            if(entry_index != -1):
                full_address =[block, entry_index]
                return full_address

        return -1

    #TODO: Write mkdir to test full functionality of mkfile

















