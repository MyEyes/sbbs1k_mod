#from .sbbs_rom import SBBS_ROM
from .sbbs_char_map import *
from .sbbs_player import SBBS_Player, SBBS_Fielder, SBBS_Pitcher
from enum import Enum

class SBBS_FIELD_POSITION(Enum):
    MASK = 0xF0
    PINCH_HITTER = 0x00
    CATCHER = 0x20
    FIRST_BASE = 0x30
    SECOND_BASE = 0x40
    THIRD_BASE = 0x50
    SHORT_STOP = 0x60
    LEFT_FIELD = 0x70
    CENTER_FIELD = 0x80
    RIGHT_FIELD = 0x90

class FieldPlayerAssignment:
    FIELD_PLAYER_IDX_STEP = 12
    def __init__(self, rom:"SBBS_ROM", team:"SBBS_Team", idx:int):
        self.rom = rom
        self.team = team
        self.idx = idx
        self.team_idx_base = self.team.idx*FieldPlayerAssignment.FIELD_PLAYER_IDX_STEP
        self.byte = self.team.field_player_map_bytes[self.idx]
        self.position = SBBS_FIELD_POSITION(self.byte & SBBS_FIELD_POSITION.MASK.value)
        self.number = self.byte & 0xf
        self.player = SBBS_Fielder(self.rom, self.team_idx_base+self.idx)

    def __repr__(self):
        return f"{self.idx+1}: {self.player} - {self.position.name}"
    
    def update_in_rom(self):
        self.byte = self.number | self.position.value
        self.rom.replace_byte_range(self.team.base_off+self.team.PLAYER_MAP_OFFSET+self.idx, bytes([self.byte]))
        self.player.update_in_rom()
    
    def to_dict(self):
        data = {
            "field_position": self.position.name,
            "number": self.number,
            "player": self.player.to_dict()
        }
        return data
    
    def from_dict(self, data:dict):
        self.number = data["number"]
        self.player.from_dict(data["player"])
        self.position = SBBS_FIELD_POSITION[data["field_position"]]

class PitcherPlayerAssignment:
    PITCHER_PLAYER_IDX_STEP = 6
    PITCHER_PLAYER_IDX_OFFSET = FieldPlayerAssignment.FIELD_PLAYER_IDX_STEP*18 #Max Team Number

    def __init__(self, rom:"SBBS_ROM", team:"SBBS_Team", idx:int):
        self.rom = rom
        self.team = team
        self.idx = idx
        self.team_idx_base = self.team.idx*PitcherPlayerAssignment.PITCHER_PLAYER_IDX_STEP + PitcherPlayerAssignment.PITCHER_PLAYER_IDX_OFFSET
        self.byte = self.team.pitcher_bytes[self.idx]
        self.number = self.byte & 0xf
        self.player = SBBS_Pitcher(self.rom, self.team_idx_base+self.idx)

    def to_dict(self):
        data = {
            "number": self.number,
            "player": self.player.to_dict()
        }
        return data
    
    def update_in_rom(self):
        self.rom.replace_byte_range(self.team.base_off+self.team.PITCHER_MAP_OFFSET+self.idx, bytes([self.byte]))
        self.player.update_in_rom()
    
    def from_dict(self, data:dict):
        self.number = data["number"]
        self.player.from_dict(data["player"])

    def __repr__(self):
        return f"{self.idx+1}: {self.player}"


class SBBS_Team:
    MAX_TEAM_IDX = 17
    TEAM_BASE = 0x18012
    NAME_OFFSET = 0x03
    NAME_LENGTH = 0x0a
    PLAYER_MAP_OFFSET = 0x0e
    PLAYER_MAP_SIZE = 12
    PITCHER_MAP_OFFSET = 0x1a
    PITCHER_MAP_SIZE = 6
    def __init__(self, rom:"SBBS_ROM", idx:int):
        assert idx <= SBBS_Team.MAX_TEAM_IDX, f"Team idx({idx}) is bigger than max team idx: {SBBS_Team.MAX_TEAM_IDX}"
        self.rom = rom
        self.idx = idx
        self.name = ""
        self.base_off = SBBS_Team.TEAM_BASE + self.idx*0x20
        self.__try_parse()

    def __try_parse(self):
        self.name_bytes = self.rom.read_bytes(self.base_off + SBBS_Team.NAME_OFFSET, SBBS_Team.NAME_LENGTH)
        self.name = sbbs_bytes_to_str(self.name_bytes)

        self.field_player_map_bytes = self.rom.read_bytes(self.base_off+SBBS_Team.PLAYER_MAP_OFFSET, SBBS_Team.PLAYER_MAP_SIZE)
        self.field_players = [FieldPlayerAssignment(self.rom, self, idx) for idx in range(SBBS_Team.PLAYER_MAP_SIZE)]
        self.pitcher_bytes = self.rom.read_bytes(self.base_off + SBBS_Team.PITCHER_MAP_OFFSET, SBBS_Team.PITCHER_MAP_SIZE)
        self.pitcher_players = [PitcherPlayerAssignment(self.rom, self, idx) for idx in range(SBBS_Team.PITCHER_MAP_SIZE)]

    def to_dict(self):
        data = {
            "name": self.name,
            "fielders": [assignment.to_dict() for assignment in self.field_players],
            "pitchers": [assignment.to_dict() for assignment in self.pitcher_players]
        }
        return data
    
    def from_dict(self, data:dict):
        self.name = data["name"]
        for i in range(SBBS_Team.PLAYER_MAP_SIZE):
            self.field_players[i].from_dict(data["fielders"][i])
        for i in range(SBBS_Team.PITCHER_MAP_SIZE):
            self.pitcher_players[i].from_dict(data["pitchers"][i])

    def update_in_rom(self):
        self.rom.replace_byte_range(self.base_off+SBBS_Team.NAME_OFFSET, bytes(str_to_sbbs_idxs(self.name)))
        for assignment in self.field_players:
            assignment.update_in_rom()
        for assignment in self.pitcher_players:
            assignment.update_in_rom()