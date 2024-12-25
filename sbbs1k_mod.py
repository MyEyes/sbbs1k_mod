import argparse
from src.sbbs_rom import SBBS_ROM
from src.sbbs_team import SBBS_Team
from src.sbbs_player import SBBS_Player
from src import set_log_level
from src.sbbs_player import HitterAbility
import logging

def generate_test_roms(args, bank_size=32*1024):
    sbbs_rom = SBBS_ROM.from_file(args.base_rom_path)
    for off in range(0, sbbs_rom.header.rom_size, bank_size):
        sbbs_rom = SBBS_ROM.from_file(args.base_rom_path)
        sbbs_rom.replace_byte_range(off, bytes([0xea]*bank_size))
        if sbbs_rom and args.output:
            sbbs_rom.write_to(args.output+f"_{hex(off)}.smc")

def generate_team_test_roms(args, step_size = 0x200):
    #overwriting 0x18000 with 0x41 made everything zero and then change later, maybe team code is messed up by this
    #overwriting 0x18200 with 0x41 made some names show up wrong
    #overwriting 0x18400 with 0x41 looks basically normal
    base = 0x18000
    sbbs_rom = SBBS_ROM.from_file(args.base_rom_path)
    for off in range(base, base+8*1024, step_size):
        sbbs_rom = SBBS_ROM.from_file(args.base_rom_path)
        sbbs_rom.replace_byte_range(off, bytes([0x41]*step_size))
        if sbbs_rom and args.output:
            sbbs_rom.write_to(args.output+f"_team_{hex(off)}.smc")

def generate_guess_test_roms(args, guess_addr=0x18000, guess_size=0x252, guess_overwrite:int=0):
    #overwriting 0x18000-0x18252 seems to break names, but also changes values when displaying
    #overwriting 0x18020-0x18252 seems to break names and stats, but some names and stats remain
    #overwriting 0x18010-0x18252 seems to break names and stats, but some names and stats remain
    #overwriting just one byte at 0x18010 breaks many names, data is either compressed or this is actually code and not data
    sbbs_rom = SBBS_ROM.from_file(args.base_rom_path)
    sbbs_rom.replace_byte_range(guess_addr, bytes([guess_overwrite]*guess_size))
    sbbs_rom.write_to(args.output+f"_guess_{hex(guess_addr)}-{hex(guess_addr+guess_size)}-{hex(guess_overwrite)}.smc")

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("sbbs1k_mod.py", description="Small tool for altering teams in Super Baseball Simulator 1000")
    arg_parser.add_argument("base_rom_path")
    arg_parser.add_argument("--log_level", default="INFO")
    arg_parser.add_argument("-o", "--output", default=None)
    arg_parser.add_argument("-x", "--export", default=None)
    arg_parser.add_argument("-i", "--import", dest="import_path", default=None)
    arg_parser.add_argument("-d", "--debug_teams", action="store_true", default=False)

    logger = logging.getLogger("C.CLI")
    args = arg_parser.parse_args()

    if hasattr(args, "log_level") and args.log_level:
        set_log_level(args.log_level)

    sbbs_rom = None
    try:
        sbbs_rom = SBBS_ROM.from_file(args.base_rom_path)
        logger.info(f"Succesfully loaded SBBS 1000 ROM from {args.base_rom_path}")
    except Exception as e:
        logger.error(f"Error loading ROM from {args.base_rom_path}: {e}")

    #generate_test_roms(args, bank_size=8*1024)
    #generate_team_test_roms(args, step_size=0x200)
    #generate_guess_test_roms(args, 0x18203, 0x2, 0x01) #overwriting original bytes 0x24 0x95 with 0x01 0x01 turns 'GUS' into 'AMOS' and 'LANE' into 'ELI'
    #generate_guess_test_roms(args, 0x18203, 0x1, 0x01) # #overwriting original byte 0x24 with 0x01 turns 'GUS' into 'AMOS'
    # for i in range(64):
    #     generate_guess_test_roms(args, 0x58000+0x60*i, 4*8*3, i) # #overwriting original byte 0x24 with 0x12 turns 'GUS' into 'AMOS'
    
    if args.import_path:
        import_count = sbbs_rom.import_from(args.import_path)
        logger.info(f"Imported {import_count} teams from {args.import_path}")

    if args.debug_teams:
        logger.info(f"Printing teams for debugging purposes")
        for i in range(18):
            team = sbbs_rom.teams[i]
            logger.info("="*16)
            logger.info(f"{hex(i)} {hex(team.base_off)} {team.name}")
            logger.info("==Fielders==")
            for field_player in team.field_players:
                logger.info(field_player)
            logger.info("==Pitchers==")
            for pitcher in team.pitcher_players:
                logger.info(pitcher)
            # if team.name.startswith("POWERS"):
            #     for field_player in team.field_players:
            #         field_player.player.hr = 150
            #         field_player.player.av = 999
            #         field_player.player.hitter_ability = HitterAbility.INVAL_5
            #         field_player.player.update_in_rom()


    if args.export:
        logger.info(f"Exporting teams to {args.export}")
        sbbs_rom.export(args.export)

    if sbbs_rom and args.output:
        logger.info(f"Writing rom to {args.output}")
        sbbs_rom.write_to(args.output)