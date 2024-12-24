from .snes_rom import SNES_ROM
from .sbbs_team import SBBS_Team
import json
import os

class SBBS_ROM(SNES_ROM):
    def __init__(self, data):
        super().__init__(data)
        self.__check_rom_values()
        self.load_teams()

    def __check_rom_values(self):
        title = "baseball simulator    "
        assert self.header.title == "baseball simulator   ", f"Wrong title in header. Expected: \"{title}\" Found: \"{self.header.title}\""
        rom_size = 0x80000
        assert self.header.rom_size == rom_size, f"Wrong rom size. Expected: {hex(rom_size)} Found:{hex(self.header.rom_size)}"
        ram_size = 0x2000
        assert self.header.ram_size == ram_size, f"Wrong ram size. Expected: {hex(ram_size)} Found:{hex(self.header.ram_size)}"
        ntsc = 1
        assert ntsc == self.header.ntsc_byte, f"Wrong country/ntsc value. Expected: {ntsc} Found:{self.header.ntsc_byte}"

    def load_teams(self):
        self.teams = []
        for i in range(18):
            team = SBBS_Team(self, i)
            self.teams.append(team)

    @classmethod
    def from_file(cls, path:str)->"SBBS_ROM":
        with open(path, "rb") as f:
            return SBBS_ROM(f.read())
        
    def export(self, path:str):
        if not os.path.exists(path):
            os.mkdir(path)
        for i,team in enumerate(self.teams):
            team_path = os.path.join(path,f"team_{i}.json")
            with open(team_path, "w") as f:
                json.dump(team.to_dict(), f)

    def import_from(self, path:str):
        assert os.path.exists(path), f"Import path ({path}) doesn't exist."
        count = 0
        for i,team in enumerate(self.teams):
            team_path = os.path.join(path,f"team_{i}.json")
            if os.path.exists(team_path):
                count += 1
                with open(team_path, "r") as f:
                    team_dict = json.load(f)
                    team.from_dict(team_dict)
                    team.update_in_rom()
        return count
        
    def read_bytes(self, offset:int, size:int):
        t_off = offset + self.base_offset
        return self.data[t_off:t_off+size]
    
    def write_to(self, path:str)->None:
        for team in self.teams:
            team.update_in_rom()
        super().write_to(path)
        
    def replace_byte_range(self, offset:int, new_bytes:bytes):
        # Data below with 0xea(NOP) overwrite
        # 0x10000-0x12000 gets to title, freezes after
        # 0x12000-0x14000 freezes immediately
        # 0x14000-0x16000 breaks on main menu
        # 0x16000-0x18000 breaks after title screen
        # 0x18000-0x1c000 shows "Backup has failed-stats have been lost." message, names and stats messed up
        # Data below with 0xff overwrite
        # 0x8000 looked fine on start
        # 0x10000-0x18000 doesn't enter main menu
        # 0x10000-0x14000 doesn't enter main menu
        # 0x18000-0x1c000 doesn't enter main menu
        # 0x20000-0x28000 backgrounds clobbered, names fine
        # 0x28000-0x30000 looks fine
        # 0x30000-0x34000 looks fine
        # 0x34000-0x36000 looks fine
        # 0x34000-0x38000 starts, but has graphical glitches, main menu broken
        # 0x36000-0x38000 starts, but has graphical glitches, main menu broken
        # 0x38000-0x3c000 frozen on startup
        # 0x3c000-0x40000 frozen on startup
        # 0x38000-0x40000 frozen on startup
        # 0x40000-0x48000 backgrounds completely white, rest seems fine
        # 0x48000-0x50000 looks fine
        # 0x50000-0x54000 UI backgrounds (and characters?) partially white, names and stats fine
        # 0x54000-0x56000 UI backgrounds (and characters?) completely white, can't say about stats
        # 0x56000-0x58000 looks fine
        # 0x50000-0x58000 UI backgrounds (and characters?) completely white, can't say about stats
        # 0x58000-0x60000 team logos completely white when replaced with 0xff, names fine
        # 0x60000 broken graphics for sure, names fine
        # 0x68000 seems fine
        # 0x70000 seems fine
        # 0x78000 seems fine
        size = len(new_bytes)
        t_off = offset + self.base_offset
        self.data[t_off: t_off+size] = new_bytes