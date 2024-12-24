from .snes_header import SNES_ROM_Header
import logging

class SNES_ROM:
    def __init__(self, data:bytes):
        self.data = bytearray(data)
        self.logger = logging.getLogger("C."+self.__class__.__name__)
        self.has_extra_header = False
        self.base_offset = 0
        self.__check_length()
        self.__find_header()
        assert self.header, "Couldn't find ROM header"
        self.__calculate_checksum()
    
    def __check_length(self):
        self.length = len(self.data)
        if (self.length & 0xfff) == 0x200:
            self.has_extra_header = True
            self.base_offset = 0x200

    def __find_header(self):
        self.header = None
        possible_header_offsets = [0x7fc0, 0xffc0, 0x40ffc0]
        for off in possible_header_offsets:
            try:
                t_off = off+self.base_offset
                self.header = SNES_ROM_Header(self.data[t_off:t_off+0x40])
                self.header_base = t_off
                return
            except Exception as e:
                self.logger.debug(f"Error while trying to parse header at {hex(off)}: {e}")

    def __calculate_checksum(self, do_check=True):
        curr_sum = 0
        for b in self.data[self.base_offset:]:
            curr_sum += b
        self.checksum = curr_sum & 0xffff
        self.checksum_complement = (self.checksum ^ 0xffff) & 0xffff

        if do_check:
            assert self.checksum == self.header.checksum, f"Checksum Mismatch. Calculated: {hex(self.checksum)} Header Checksum: {hex(self.header.checksum)}"
            assert self.checksum_complement == self.header.checksum_complement, f"Checksum Complement Mismatch. Calculated: {hex(self.checksum_complement)} Header Checksum: {hex(self.header.checksum_complement)}"

    def __update_header_bytes(self):
        # We expect checksum to be incorrect if we altered bytes
        self.__calculate_checksum(do_check=False)
        self.header.checksum = self.checksum
        self.header.checksum_complement = self.checksum_complement
        self.data[self.header_base:self.header_base+0x40] = self.header.to_bytes()

    @classmethod
    def from_file(cls, path:str)->"SNES_ROM":
        with open(path, "rb") as f:
            return SNES_ROM(f.read())
        
    
    def write_to(self, path:str)->None:
        self.__update_header_bytes()
        with open(path, "wb") as f:
            f.write(self.data)