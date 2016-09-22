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

    # initialize volume
    def __init__(self, vdrive):

        # variables include drive and heap for bitmapping
        self.drivename = vdrive
        self.mydrive = drive.Drive(vdrive)
        self.heap = []

    # Clear drive and format blocks
    def format(self):

        #call oem format
        self.mydrive.format()

        #set bitmap
        block = "+"
        for c in range (Volume.SIZE_BITMAP-1):
            block = "{:s}{:s}".format(block, '-')

        # create empty block in root alongside bitmap
        entry = directoryEntry.DirectoryEntry('f', '')
        data = entry.getEntry()
        for c in range (Volume.NUM_ROOTFILES):
            block = "{}{}".format(block, data)

        #write back to block
        self.mydrive.write_block(Volume.ROOT, block)

        #instantiate bitmap heap
        self.heap_sort(block)

    # NOTE: Works
    def reconnect(self):

        self.mydrive.reconnect()
        # instantiate bitmap heap
        block = self.mydrive.read_block(Volume.ROOT)
        self.heap_sort(block)

    # add existing bitmap to heap and heapify
    def heap_sort(self, block):
        for c in range (Volume.SIZE_BITMAP):
            if block[c] == '-':
                heapq.heappush(self.heap, c)


    # make a file in a path, expand directory if full
    def mkfile(self, path):
        #find the entry address of the deepest directory
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        #parse the name of the file to be created
        file_name = self.parse_name(path)
        block_to_modify = None
        index_to_modify = None
        #parse the name of the directory that the file is being written to
        directory_name = self.parse_name(path[:-(len(file_name)+1)])
        # if the name is not blank or None we are not making an entry in ROOT
        if (directory_name != None and len(directory_name) != Volume.ROOT):
            # format directory name to include d: header
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)
            # get the block and index of the lowest open entry slot
            full_address = self.find_entry_in_directory(Volume.OPEN_ENTRY, directory_name, directory_address)
            # if an actual address is returned parse block and index
            if(full_address!=-1):

                block_to_modify = full_address[0]
                index_to_modify = full_address[1]
            else:
                # otherwise find the index of the directory itself within its parent
                directory_index = self.find_entry_index(directory_name, directory_address)

                # create an empty directory entry
                empty_entry = directoryEntry.DirectoryEntry('f', '')
                empty_directory = empty_entry.getDirectory()

                # find the lowest free block
                lowest_free_block = self.allocate_block()
                # create empty directory block
                self.mydrive.write_block(lowest_free_block, empty_directory)
                # append block to directory
                self.add_block(directory_address, directory_index, lowest_free_block)
                # modify size of directory to include new block
                size = self.get_size(directory_address, directory_index) + Volume.SIZE_BLOCK
                self.update_size(directory_address, directory_index, size)
                # set new block and index 0 to be written to
                block_to_modify = lowest_free_block
                index_to_modify = 0
        else:
            # otherwise find free space in root
            block_to_modify = Volume.ROOT
            index_to_modify = self.find_entry_index(Volume.OPEN_ENTRY, Volume.ROOT)

        # read data of block being modified
        original_block = self.mydrive.read_block(block_to_modify)
        file_name= "{}{}".format(Volume.HEAD_FILE, file_name)
        insertion_index = index_to_modify * Volume.SIZE_ENTRY
        file_name_length = len(file_name) + insertion_index
        # insert file into block
        new_block = "{}{}{}".format(original_block[:insertion_index], file_name, original_block[file_name_length:])
        # write back to drive
        self.mydrive.write_block(block_to_modify, new_block)

    # make new directory NOTE: See programming notes on mkfile until next comment
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
        # automatically allocate a block for new directory
        empty_entry = directoryEntry.DirectoryEntry('f', '')
        empty_directory = empty_entry.getDirectory()
        lowest_free_block = self.allocate_block()
        self.mydrive.write_block(lowest_free_block, empty_directory)
        self.add_block(block_to_modify, index_to_modify, lowest_free_block)
        self.update_size(block_to_modify, index_to_modify, Volume.SIZE_BLOCK)

    def append(self, path, data):
        # find the entry address of the deepest directory
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        # parse the name of the file to be modified
        file_name = self.parse_name(path)
        file_name = "{}{}".format(Volume.HEAD_FILE, file_name)
        block_to_modify = None
        index_to_modify = None
        # parse the name of the directory that the file is being written to
        directory_name = self.parse_name(path[:-(len(file_name)+1)])
        # if the name is not blank or None we are not making an entry in ROOT
        if (directory_name != None and len(directory_name) != Volume.ROOT):
            # format directory name to include d: header
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)

            # get the block and index of the file header
            full_address = self.find_entry_in_directory(file_name, directory_name, directory_address)
            block = full_address[0]
            index = full_address[1]
        else:
            # otherwise we are in root
            block = Volume.ROOT
            index = self.find_entry_index(file_name, Volume.ROOT)

        #find the current size of the file
        curr_size  = self.get_size(block, index)

        # find the amount of space remaining in already allocated blocks
        remaining_space = Volume.SIZE_BLOCK - (curr_size % Volume.SIZE_BLOCK)
        print("{:s}{:d}".format("remainining space ", remaining_space))
        # find how many blocks are used
        blocks = self.find_used_blocks(block, index)
        used_block_num = len(blocks)
        # if blocks have been allocated and there is open space

        if (curr_size <used_block_num * Volume.SIZE_BLOCK):
            #append to last block
            block_to_modify = blocks[-1]
            #find data currently in block
            block_data = self.mydrive.read_block(block_to_modify)
            # append maximum amount of new data to block
            block_data = "{}{}".format(block_data[:curr_size % Volume.SIZE_BLOCK], data[:remaining_space])
            # update current size
            curr_size += len(data[:remaining_space])
            # fill in rest of block with blank spaces
            additional_spaces = Volume.SIZE_BLOCK - (curr_size % Volume.SIZE_BLOCK)
            if(additional_spaces==Volume.SIZE_BLOCK):
                additional_spaces = 0

            print("{:s}{:d}".format("len block data b4 ", len(block_data)))

            block_data = "{}{}".format(block_data, ' ' * additional_spaces)
            print("{:s}{:d}".format("len block data at ", len(block_data)))
            # write block back and update size
            print("{:s}{:d}".format("writing to block ", block_to_modify))
            self.mydrive.write_block(block_to_modify, block_data)
            self.update_size(block, index, curr_size)
            # if there was more data than current space rerun append on remaining data
            if(len(data)>remaining_space):
                self.append(path, data[remaining_space:])
        else:

            # if we need more room find the lowest free block
            lowest_free_block = self.allocate_block()
            # add it to the file
            self.add_block(block, index, lowest_free_block)
            # rerun append
            self.append(path, data)

    def print(self, path):
        # find the entry address of the deepest directory
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        # parse the name of the file to be modified
        file_name = self.parse_name(path)
        file_name = "{}{}".format(Volume.HEAD_FILE, file_name)
        block_to_modify = None
        index_to_modify = None
        # parse the name of the directory that the file is being written to
        directory_name = self.parse_name(path[:-(len(file_name)+1)])
        # if the name is not blank or None we are not making an entry in ROOT
        if (directory_name != None and len(directory_name) != Volume.ROOT):
            # format directory name to include d: header
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)

            # get the block and index of the file header
            full_address = self.find_entry_in_directory(file_name, directory_name, directory_address)
            block = full_address[0]
            index = full_address[1]
        else:
            # otherwise we are in root
            block = Volume.ROOT
            index = self.find_entry_index(file_name, Volume.ROOT)

        blocks = self.find_used_blocks(block, index)

        data = ""
        for item in blocks:
            bd = self.mydrive.read_block(item)
            data = "{}{}".format(data, bd)

        print(data)

    def delfile(self, path):
        # find the entry address of the deepest directory
        directory_address = self.find_base_directory_address(path, Volume.ROOT)
        # parse the name of the file to be modified
        file_name = self.parse_name(path)
        file_name = "{}{}".format(Volume.HEAD_FILE, file_name)
        block_to_modify = None
        index_to_modify = None
        # parse the name of the directory that the file is being written to
        directory_name = self.parse_name(path[:-(len(file_name)+1)])
        # if the name is not blank or None we are not making an entry in ROOT
        if (directory_name != None and len(directory_name) != Volume.ROOT):
            # format directory name to include d: header
            directory_name = "{}{}".format(Volume.HEAD_DIRECTORY, directory_name)

            # get the block and index of the file header
            full_address = self.find_entry_in_directory(file_name, directory_name, directory_address)
            block = full_address[0]
            index = full_address[1]
        else:
            # otherwise we are in root
            block = Volume.ROOT
            index = self.find_entry_index(file_name, Volume.ROOT)

        blocks = self.find_used_blocks(block, index)


        for item in blocks:
            self.deallocate_block(item)

        blank_entry = directoryEntry.DirectoryEntry('f', ' ').getEntry()
        block_data = self.mydrive.read_block(block)
        start = index * Volume.SIZE_ENTRY
        end = start + Volume.SIZE_ENTRY
        block_data = "{}{}{}".format(block_data[:start], blank_entry, block_data[end:])
        self.mydrive.write_block(block, block_data)

        if(block != Volume.ROOT):
            count = self.get_num_entries(block)
            directory_index = self.find_entry_index(directory_name, directory_address)
            num_blocks = len(self.find_used_blocks(directory_address, directory_index))

            if(count == 0 and num_blocks > 1):
                self.deallocate_block(block)

                self.remove_block(directory_address, directory_index, block)
                curr_size = self.get_size(directory_address, directory_index)
                curr_size = curr_size - Volume.SIZE_BLOCK
                self.update_size(directory_address, directory_index, curr_size)

    def deldir(self, path):
        self.delfile(path)


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

    # parse name from end of path
    def parse_name(self, path):
        for c in range(len(path)-1, -1, -1):
            if(path[c]=='/'):
                name = path[c+1:]
                return name

    # find block and index of entry within directory, return -1 if not found
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

    def deallocate_block(self,block):
        blank = " " * Volume.SIZE_BLOCK
        self.mydrive.write_block(block, blank)
        root_block = self.mydrive.read_block(Volume.ROOT)
        root_block = "{}{}{}".format(root_block[:block], '-', root_block[block + 1:])
        self.mydrive.write_block(Volume.ROOT, root_block)
        heapq.heappush(self.heap, block)

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

    def remove_block(self, address, index, block_to_remove):
        block_data = self.mydrive.read_block(address)
        used_blocks = self.find_used_blocks(address, index)
        start = index * Volume.SIZE_ENTRY + Volume.INDEX_BLOCKS
        end = start + Volume.SIZE_BLOCK_INDEX * Volume.NUM_BLOCK_INDEX
        block_data = "{}{}{}".format(block_data[:start], '000 ' * Volume.NUM_BLOCK_INDEX, block_data[end:])
        self.mydrive.write_block(address, block_data)

        for item in used_blocks:
            if (item != block_to_remove):
                self.add_block(address, index, item)


    def get_size(self, address, index):
        block = self.mydrive.read_block(address)
        start = index*Volume.SIZE_ENTRY + Volume.INDEX_FSIZE
        end = start + Volume.SIZE_BLOCK_SIZE
        size = int(block[start:end])
        return size

    def get_num_entries(self, block):
        blank_entry = directoryEntry.DirectoryEntry('f', ' ').getEntry()
        block_data = self.mydrive.read_block(block)
        count = 0
        for c in range(Volume.NUM_FILES):
            start = c * Volume.SIZE_ENTRY
            end = start + Volume.SIZE_ENTRY
            actual_entry = block_data[start:end]
            if(actual_entry!=blank_entry):
                count+=1

        return count




















