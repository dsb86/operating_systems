import drive
import directoryEntry
import heapq

class Volume:

    SIZE_BITMAP = 128
    SIZE_ENTRY = 64
    SIZE_FNAME = 8
    SIZE_BLOCK_INDEX = 4
    SIZE_BLOCK_SIZE = 4
    SIZE_BLOCK = 512
    NUM_ROOTFILES = 6
    NUM_FILES = 8
    NUM_BLOCK_INDEX = 12
    INDEX_FNAME = 2
    INDEX_BLOCKS = 16
    INDEX_FSIZE = 11
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
                heapq.heappush(self.heap, c)



    def mkfile(self, path):
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        file_name = self.parse_name(path)
        block_to_modify = None
        index_to_modify = None

        directory_name = self.parse_name(path[:-(len(file_name)+1)])

        if (directory_name != None and len(directory_name) != Volume.ROOT):
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)

            full_address = self.find_entry_in_directory(Volume.OPEN_ENTRY, directory_name, directory_address)
            if(full_address!=-1):
                block_to_modify = full_address[0]
                index_to_modify = full_address[1]
            else:
                directory_index = self.find_entry_index(directory_name, directory_address)
                empty_entry = directoryEntry.DirectoryEntry('f', '')
                empty_directory = empty_entry.getDirectory()

                lowest_free_block = self.allocate_block()
                self.mydrive.write_block(lowest_free_block, empty_directory)
                self.add_block(directory_address, directory_index, lowest_free_block)
                size = self.get_size(directory_address, directory_index) + Volume.SIZE_BLOCK
                self.update_size(directory_address, directory_index, size)
                block_to_modify = lowest_free_block
                index_to_modify = 0
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

    def mkdir(self, path):
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        file_name = self.parse_name(path)
        block_to_modify = None
        index_to_modify = None

        directory_name = self.parse_name(path[:-(len(file_name) + 1)])
        if (directory_name != None and len(directory_name) != Volume.ROOT):
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)

            full_address = self.find_entry_in_directory(Volume.OPEN_ENTRY, directory_name, directory_address)
            #TODO: Expand directory if no space found
            if(full_address!=-1):
                block_to_modify = full_address[0]
                index_to_modify = full_address[1]
            else:
                directory_index = self.find_entry_index(directory_name, directory_address)
                empty_entry = directoryEntry.DirectoryEntry('f', '')
                empty_directory = empty_entry.getDirectory()

                lowest_free_block = self.allocate_block()
                self.mydrive.write_block(lowest_free_block, empty_directory)
                self.add_block(directory_address, directory_index, lowest_free_block)
                size = self.get_size(directory_address, directory_index) + Volume.SIZE_BLOCK
                self.update_size(directory_address, directory_index, size)

                block_to_modify = lowest_free_block
                index_to_modify = 0
        else:
            block_to_modify = Volume.ROOT
            index_to_modify = self.find_entry_index(Volume.OPEN_ENTRY, Volume.ROOT)

        # NOTE: Works
        original_block = self.mydrive.read_block(block_to_modify)
        file_name= "{}{}".format(Volume.HEAD_DIRECTORY, file_name)
        insertion_index = index_to_modify * Volume.SIZE_ENTRY
        file_name_length = len(file_name) + insertion_index
        new_block = "{}{}{}".format(original_block[:insertion_index], file_name, original_block[file_name_length:])
        self.mydrive.write_block(block_to_modify, new_block)
        empty_entry = directoryEntry.DirectoryEntry('f', '')
        empty_directory = empty_entry.getDirectory()
        lowest_free_block = self.allocate_block()
        self.mydrive.write_block(lowest_free_block, empty_directory)
        self.add_block(block_to_modify, index_to_modify, lowest_free_block)
        self.update_size(block_to_modify, index_to_modify, Volume.SIZE_BLOCK)



    # NOTE: Works
    def find_entry_index(self, name, block_address):
        block_data = self.mydrive.read_block(block_address)
        for index in range(Volume.NUM_FILES):
            beggining = Volume.SIZE_ENTRY * index
            end = beggining + len(name)
            if (block_data[beggining:end] == name):
                return index

        return -1



    # find the block that contains the directory entry to be modified
    def find_base_directory_address(self, path, block_address):
        name = ""
        entry_index = None
        end = 0

        #boundary is the maximum file name size or path length whichever greater
        boundary = Volume.SIZE_FNAME
        if boundary > len(path):
            boundary = len(path)

        #start from the "root" until boundary look for subdirectory
        for c in range(1, boundary):
            #if there is a subdirectory return the index for the name
            if path[c] == '/':
                end = c
                break

            #otherwise indicate that we are at the lowest level
            if c == boundary-1:
                end=-1

        #if we are at lowest level return arg block_address
        if end == -1:
            return block_address
            # NOTE: Works Up To Here For Sure
        else:
            # otherwise indicate the name of the subdirectory
            name = path[1:end]
            name = "{}{}".format(Volume.HEAD_DIRECTORY, name)
            # find its index within the current block
            entry_index = self.find_entry_index(name, block_address)

        # if it is not in current block return file not found
        if entry_index == -1:
            return -1
        else:
            # otherwise see if there is a deeper directory
            end2 = 0
            # new boundary is maximum file name + end or path
            boundary = Volume.SIZE_FNAME + end
            if boundary > len(path):
                boundary = len(path)
            #start past / go to boundary
            for c in range(end+1, boundary):
                if path[c] == '/':
                    end2 = c
                    break

                if c == boundary - 1:
                    end2 = -1

            #if there is no deeper directory return arg
            if(end2==-1):
                return block_address
            else:

                # if there is deeper directory find out what block it is in and recurs
                used_blocks = self.find_used_blocks(block_address, entry_index)
                for block in used_blocks:
                    target = self.find_base_directory_address(path[end2:], block)
                    if(target != -1):
                        return target
        # target not found
        return -1

    def find_used_blocks(self, block_address, entry_index):

        block_data = self.mydrive.read_block(block_address)
        block_index_beginning = entry_index * Volume.SIZE_ENTRY + Volume.INDEX_BLOCKS

        block_index_end = block_index_beginning + Volume.SIZE_BLOCK_INDEX-1

        used_blocks=[]
        for c in range(Volume.NUM_BLOCK_INDEX):
            block_index = block_data[block_index_beginning:block_index_end]
            block_num = int(block_index)

            if(block_num != 0):
                used_blocks.append(block_num)
                block_index_beginning += Volume.SIZE_BLOCK_INDEX
                block_index_end += Volume.SIZE_BLOCK_INDEX
            else:
                return used_blocks

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

    #TODO: Break on drive full
    def allocate_block(self):
        lowest_free_block = heapq.heappop(self.heap)
        root_block = self.mydrive.read_block(Volume.ROOT)
        root_block = "{}{}{}".format(root_block[:lowest_free_block], '+', root_block[lowest_free_block+1:])
        self.mydrive.write_block(Volume.ROOT, root_block)
        return lowest_free_block

    def update_size(self, block_address, index, size):
        block_data = self.mydrive.read_block(block_address)
        size_entry = "{}".format(size)
        diff = Volume.SIZE_BLOCK_SIZE-len(size_entry)
        for c in range (diff):
            size_entry = "{}{}".format('0', size_entry)

        start_index = index*Volume.SIZE_ENTRY+Volume.INDEX_FSIZE
        end_index = start_index + Volume.SIZE_BLOCK_SIZE
        block_data = "{}{}{}".format(block_data[:start_index], size_entry, block_data[end_index:])
        self.mydrive.write_block(block_address, block_data)

    def add_block(self,address, index, block_to_add):
        block_data = self.mydrive.read_block(address)
        block_entry = "{}".format(block_to_add)
        diff = Volume.SIZE_BLOCK_INDEX - len(block_entry) -1
        for c in range(diff):
            block_entry = "{}{}".format('0', block_entry)

        block_entry = "{}{}".format(block_entry, ' ')

        used_blocks = self.find_used_blocks(address, index)
        block_num =len(used_blocks)
        start_index = index * Volume.SIZE_ENTRY + Volume.INDEX_BLOCKS + block_num * Volume.SIZE_BLOCK_INDEX
        end_index = start_index + Volume.SIZE_BLOCK_INDEX
        block_data = "{}{}{}".format(block_data[:start_index], block_entry, block_data[end_index:])

        self.mydrive.write_block(address, block_data)
    #TODO: Write mkdir to test full functionality of mkfile

    def get_size(self, address, index):
        block = self.mydrive.read_block(address)
        start = index*Volume.SIZE_ENTRY + Volume.INDEX_FSIZE
        end = start + Volume.SIZE_BLOCK_SIZE
        size = int(block[start:end])
        return size

















