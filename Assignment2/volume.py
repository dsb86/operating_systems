import drive
import directoryEntry

class Volume:

    SIZE_BITMAP = 128
    NUM_ROOTFILES = 6


    def __init__(self, vdrive):

        self.drivename = vdrive;
        self.mydrive = drive.Drive(vdrive)

    def format(self):

        self.mydrive.format()

        block = "+";

        for c in range (Volume.SIZE_BITMAP-1):
            block = "{:s}{:s}".format(block, '-')

        entry = directoryEntry.DirectoryEntry('f', '')
        data = entry.getEntry()

        for c in range (Volume.NUM_ROOTFILES):
            block = "{}{}".format(block, data)

        self.mydrive.write_block(0, block)










