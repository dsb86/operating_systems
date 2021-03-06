class DirectoryEntry:
    SIZE_ENTRY = 64
    SIZE_FT = 2
    SIZE_NAME = 9
    SIZE_FSIZE = 4
    SIZE_NUMBLOCKS = 12
    NUM_ENTRY = 8
    def __init__(self, type, name):
        self.data = "{:s}:{:s}".format(type,name);
        for c in range (DirectoryEntry.SIZE_NAME-len(name)):
            self.data = "{} ".format(self.data)

        self.data = "{}0000:".format(self.data)

        for c in range (DirectoryEntry.SIZE_NUMBLOCKS):
            self.data = "{}000 ".format(self.data)

    def getEntry(self):
        return self.data

    def getDirectory(self):
        empty_block = ""
        for c in range (DirectoryEntry.NUM_ENTRY):
            empty_block = "{}{}".format(empty_block, self.data)

        return empty_block


