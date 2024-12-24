#from .sbbs_rom import SBBS_ROM
from .sbbs_char_map import *
from enum import Enum
import logging

class PitcherAbility(Enum):
    NOTHING = 0x00
    FIRE_BALL = 0x01
    STOPPER_BALL = 0x02
    PHANTOM_BALL = 0x03
    SNAKE_BALL = 0x04
    NINJA_BALL = 0x05
    SPARK_BALL = 0x06
    IRON_BALL = 0x07
    SPEEDER_BALL = 0x08
    PHOTON_BALL = 0x09
    ZIG_ZAG_BALL = 0x0A
    SPIRAL_BALL = 0x0B
    JUMPER_BALL = 0x0C
    TREMOR_BALL = 0x0D
    CHANGE_UP_BALL = 0x0E
    FLOATER_BALL = 0x0F
    MULTI_BALL = 0x10
    FADEOUT = 0x11
    WARP_BALL = 0x12
    LOTTA_BALL = 0x13
    QUESTIONMARK_BALL = 0x14

class HitterAbility(Enum):
    NOTHING = 0x00
    HYPER_HIT = 0x01
    MISSILE_HIT = 0x02
    TREMOR_HIT = 0x03
    BOMB_HIT = 0x04
    SHADOWLESS = 0x05
    INVISIBALL = 0x06
    METEOR = 0x07
    SQUIRREL_HIT = 0x08
    SPINNER_HIT = 0x09
    LEAF_HIT = 0x0A
    SHADOW_HIT = 0x0B
    HYPER_RUN = 0x0C
    FREAK_HIT = 0x0D
    DIZZY_BALL = 0x0E
    ORBIT_HIT = 0x0F
    INVAL_1 = 0x10
    INVAL_2 = 0x11
    INVAL_3 = 0x12
    INVAL_4 = 0x13
    INVAL_5 = 0x14
    

class SBBS_Player:
    NAME_LENGTH = 5
    BYTE_SIZE = 24
    PLAYER_BASE = 0x18252
    MAX_PLAYER_IDX = 0xa1*2 + 1

    HANDED_OFF = 0x5
    AV_OFF = 0x6
    HR_OFF = 0x8
    PITCH_R_OFF = 0xb
    PITCH_L_OFF = 0xc
    YEET_OFF = 0xb
    R_OFF = 0xc
    F_OFF = 0xd # same for pitcher
    ST_OFF = 0xf
    PITCH_ST_OFF = 0xe
    PITCHER_ABILITY_OFF = 0x10
    HITTER_ABILITY_OFF = 0x10
    def __init__(self, rom:"SBBS_ROM", idx:int):
        assert idx <= SBBS_Player.MAX_PLAYER_IDX, f"Player idx({idx}) is bigger than max player idx: {SBBS_Player.MAX_PLAYER_IDX}"
        self.rom = rom
        self.idx = idx
        self.name = ""
        self.base_off = SBBS_Player.PLAYER_BASE + SBBS_Player.BYTE_SIZE*idx
        self.__try_parse()

    def decode_hex_bdr(self, val):
        return (val&0xf)+(val>>4)*10
    
    def encode_hex_bdr(self, val):
        return (val//10)*16 + (val%10)

    def __try_parse(self):
        self.name_bytes = self.rom.read_bytes(self.base_off, SBBS_Player.NAME_LENGTH)
        self.name = sbbs_bytes_to_str(self.name_bytes)
        handed_byte = self.rom.read_bytes(self.base_off+SBBS_Player.HANDED_OFF, 1)[0]
        self.left_handed = (handed_byte & 0x01) == 1
        self.handedness = "L" if self.left_handed else "R"
        av_bytes = self.rom.read_bytes(self.base_off+SBBS_Player.AV_OFF, 2)
        self.av = av_bytes[1]*100+self.decode_hex_bdr(av_bytes[0])
        self.era = self.av/100.0
        hr_byte = self.rom.read_bytes(self.base_off+SBBS_Player.HR_OFF, 1)[0]
        self.hr = self.decode_hex_bdr(hr_byte)
        self.spd = self.hr
        r_byte = self.rom.read_bytes(self.base_off+SBBS_Player.R_OFF,1)[0]
        self.r = r_byte
        pitch_r_byte = self.rom.read_bytes(self.base_off+SBBS_Player.PITCH_R_OFF,1)[0]
        self.pitch_r = pitch_r_byte
        pitch_l_byte = self.rom.read_bytes(self.base_off+SBBS_Player.PITCH_L_OFF,1)[0]
        self.pitch_l = pitch_l_byte
        f_byte = self.rom.read_bytes(self.base_off+SBBS_Player.F_OFF,1)[0]
        self.f = self.decode_hex_bdr(f_byte)
        self.yeet = self.rom.read_bytes(self.base_off+SBBS_Player.YEET_OFF,1)[0]
        self.pitch_f = f_byte
        st_byte = self.rom.read_bytes(self.base_off+SBBS_Player.ST_OFF,1)[0]
        self.st = st_byte
        pitch_st_byte = self.rom.read_bytes(self.base_off+SBBS_Player.PITCH_ST_OFF,1)[0]
        self.pitch_st = pitch_st_byte
        pitcher_ability_bytes = self.rom.read_bytes(self.base_off+SBBS_Player.PITCHER_ABILITY_OFF,4)
        hitter_ability_byte = self.rom.read_bytes(self.base_off+SBBS_Player.HITTER_ABILITY_OFF,1)[0]
        self.hitter_ability = HitterAbility(hitter_ability_byte)
        self.pitcher_abilities = [PitcherAbility(b) for b in pitcher_ability_bytes]

    def __repr__(self):
        return f"<{self.name} ({hex(self.base_off)})>"
    
    def update_in_rom(self):
        self.rom.replace_byte_range(self.base_off, self.to_bytes())
    
class SBBS_Fielder(SBBS_Player):
    def __init__(self, rom, idx):
        super().__init__(rom, idx)

    def __repr__(self):
        return f"<{self.name} ({hex(self.base_off)}) - ({self.handedness}) ST:{self.st} - AV:{self.av} - HR:{self.hr} - R:{self.r} - F:{self.f} - YEET:{self.yeet} - PWR:{self.hitter_ability.name}>"
    
    def to_bytes(self):
        data = bytearray(self.rom.read_bytes(self.base_off, SBBS_Player.BYTE_SIZE))
        
        name_bytes = bytes(str_to_sbbs_idxs(self.name))
        #print(name_bytes)
        assert len(name_bytes)<=SBBS_Player.NAME_LENGTH, f"name {self.name} too long"
        data[0:len(name_bytes)] = name_bytes
        data[SBBS_Player.HITTER_ABILITY_OFF] = self.hitter_ability.value
        if self.hitter_ability!= HitterAbility.NOTHING:
            data[SBBS_Player.HITTER_ABILITY_OFF+1] = 1
        if self.left_handed:
            data[SBBS_Player.HANDED_OFF] = data[SBBS_Player.HANDED_OFF] | 1
        else:
            data[SBBS_Player.HANDED_OFF] = data[SBBS_Player.HANDED_OFF] & 0xfe
        data[SBBS_Player.AV_OFF+1] = self.av//100
        data[SBBS_Player.AV_OFF] = self.encode_hex_bdr(self.av%100)
        data[SBBS_Player.HR_OFF] = self.encode_hex_bdr(self.hr)
        data[SBBS_Player.R_OFF] = self.r
        data[SBBS_Player.F_OFF] = self.f
        data[SBBS_Player.ST_OFF] = self.st
        data[SBBS_Player.YEET_OFF] = self.yeet
        return data
    
    def to_dict(self):
        data = {
            "name": self.name,
            "handedness": self.handedness,
            "st": self.st,
            "av": self.av,
            "hr": self.hr,
            "r": self.r,
            "f": self.f,
            "yeet": self.yeet,
            "pwr": self.hitter_ability.name,
        }
        return data
    
    def from_dict(self, data):
        self.name = data["name"]
        self.handedness = data["handedness"].upper()
        self.left_handed = self.handedness == "L"
        self.st = data["st"]
        self.av = data["av"]
        self.hr = data["hr"]
        self.r = data["r"]
        self.f = data["f"]
        self.yeet = data["yeet"]
        self.hitter_ability =  HitterAbility[data["pwr"]]
    
class SBBS_Pitcher(SBBS_Player):
    def __init__(self, rom, idx):
        super().__init__(rom, idx)

    def __repr__(self):
        powers_str = ", ".join([pa.name for pa in self.pitcher_abilities])
        return f"<{self.name} ({hex(self.base_off)}) - ERA:{self.era:.2f} - SPD:{self.spd} - R:{self.pitch_r} - L:{self.pitch_l} - F:{self.pitch_f} - ST:{self.pitch_st} - PWR:[{powers_str}]>"
    
    def to_dict(self):
        data = {
            "name": self.name,
            "era": int(self.era*100),
            "spd": self.spd,
            "r": self.pitch_r,
            "l": self.pitch_l,
            "f": self.pitch_f,
            "st": self.pitch_st,
            "pwr": [pa.name for pa in self.pitcher_abilities]
        }
        return data
    
    def to_bytes(self):
        data = bytearray(self.rom.read_bytes(self.base_off, SBBS_Player.BYTE_SIZE))
        name_bytes = bytes(str_to_sbbs_idxs(self.name))
        #print(name_bytes)
        assert len(name_bytes)<=SBBS_Player.NAME_LENGTH, f"name {self.name} too long"
        data[0:len(name_bytes)] = name_bytes
        for i in range(4):
            data[SBBS_Player.PITCHER_ABILITY_OFF+i] = self.pitcher_abilities[i].value

        # ERA and AV are encoded exactly the same
        era_int = int(self.era*100)
        data[SBBS_Player.AV_OFF+1] = (era_int)//100
        data[SBBS_Player.AV_OFF] = self.encode_hex_bdr(era_int%100)
        # HR and SPD are encoded exactly the same
        data[SBBS_Player.HR_OFF] = self.encode_hex_bdr(self.spd)
        data[SBBS_Player.PITCH_R_OFF] = self.pitch_r
        data[SBBS_Player.PITCH_L_OFF] = self.pitch_l
        data[SBBS_Player.F_OFF] = self.pitch_f
        data[SBBS_Player.PITCH_ST_OFF] = self.pitch_st
        return data
    
    def from_dict(self, data:dict):
        self.name = data["name"]
        self.era = data["era"]/100.0
        self.spd = data["spd"]
        self.pitch_r = data["r"]
        self.pitch_l = data["l"]
        self.pitch_f = data["f"]
        self.pitch_st = data["st"]
        self.pitcher_abilities = [PitcherAbility[name] for name in data["pwr"]]