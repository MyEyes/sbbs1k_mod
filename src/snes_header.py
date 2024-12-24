from enum import Enum
import struct
import string
import logging

class ROM_MM_MODE(Enum):
    LoROM = 0
    HiROM = 1
    ExHiROM = 5

class SNES_ROM_Header:
    #https://snes.nesdev.org/wiki/ROM_header
    def __init__(self, data:bytes):
        self.data = data
        self.base_off = -0xffc0
        self.__try_parse()

    def __try_parse(self):
        base_off = self.base_off

        assert len(self.data) == 0x40, "Invalid length of header data"
        title_bytes = self.data[0xffc0+base_off:0xffd5+base_off]
        self.title = title_bytes.decode("ascii")
        assert all([c in string.printable for c in self.title])

        self.speed_byte = self.data[0xffd5+base_off]
        self.mm_mode = ROM_MM_MODE(0x0f & self.speed_byte)
        self.speed_fast = (self.speed_byte & 0x10) >> 4
        rom_size_byte = self.data[0xffd7+base_off]
        self.rom_size = 1024<<rom_size_byte
        ram_size_byte = self.data[0xffd8+base_off]
        self.ram_size = 1024<<ram_size_byte
        self.ntsc_byte = self.data[0xffd9+base_off]
        self.checksum_complement = struct.unpack("<H", self.data[0xffdc+base_off:0xffde+base_off])[0]
        self.checksum = struct.unpack("<H", self.data[0xffde+base_off:0xffe0+base_off])[0]

        assert (self.checksum ^ 0xffff) & 0xffff == self.checksum_complement, "Checksum and checksum complement don't match"

    # Only really updates the checksum right now
    def to_bytes(self)->bytes:
        base_off = self.base_off
        
        data = bytearray(self.data)
        data[0xffdc+base_off:0xffde+base_off] = struct.pack("<H", self.checksum_complement)
        data[0xffde+base_off:0xffe0+base_off] = struct.pack("<H", self.checksum)
        return bytes(data)