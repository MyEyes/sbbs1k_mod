import PIL
import PIL.Image
import PIL.ImageColor

class SNES_Tile_4bpp:
    def __init__(self, bs:bytes, color_map:list[int]):
        assert bs
        assert len(bs) == 32
        assert len(color_map) == 16
        self.bs = bytearray(bs)
        self.color_map = color_map
        self.pixels = [None]*(8*8)
        self.__decode()

    def __decode(self):
        def __get_bit(val, bit_idx):
            return (val>>bit_idx)&0x1
        self.palette_idx = [0]*(8*8)
        for i in range(8*8):
            b_idx = i//8
            b_off = 7-i%8
            b1 = self.bs[b_idx*2]
            b2 = self.bs[b_idx*2+1]
            b3 = self.bs[b_idx*2+16]
            b4 = self.bs[b_idx*2+16+1]
            self.palette_idx[i] = 8*__get_bit(b4, b_off)+4*__get_bit(b3, b_off)+2*__get_bit(b2,b_off)+__get_bit(b1,b_off)
            self.pixels[i] = self.color_map[self.palette_idx[i]]

    def find_best_palette_color(self, col):
        min_sqr_err = 10000000
        min_err_idx = 0
        if len(col)>3:
            if col[3] != 255:
                return 0
        for idx,pal_col in enumerate(self.color_map):
            d_r = pal_col[0]-col[0]
            d_g = pal_col[1]-col[1]
            d_b = pal_col[2]-col[2]
            sqr_err = d_r*d_r+d_g*d_g+d_b*d_b
            if sqr_err <= min_sqr_err: #<0 so that transparent (0) only happens in the special case earlier
                min_err_idx = idx
                min_sqr_err = sqr_err
        return min_err_idx

    def get_pixel(self, x, y):
        return self.pixels[x+8*y]
    
    def set_pixel(self, x, y, col):
        def __get_bit(val, bit_idx):
            return (val>>bit_idx)&0x1
        def __set_bit(val, bit_idx, bit_val):
            return (val&(0xff&~(1<<bit_idx)))|bit_val<<bit_idx
        pal_idx = self.find_best_palette_color(col)
        pixel_idx = x+8*y
        b_idx = pixel_idx//8
        bit_idx = 7-pixel_idx % 8
        self.bs[b_idx*2] = __set_bit(self.bs[b_idx*2], bit_idx, __get_bit(pal_idx,0))
        self.bs[b_idx*2+1] = __set_bit(self.bs[b_idx*2+1], bit_idx, __get_bit(pal_idx,1))
        self.bs[b_idx*2+16] = __set_bit(self.bs[b_idx*2+16], bit_idx, __get_bit(pal_idx,2))
        self.bs[b_idx*2+1+16] = __set_bit(self.bs[b_idx*2+1+16], bit_idx, __get_bit(pal_idx,3))
        self.pixels[pixel_idx] = col
        
class SBBS_Team_Logo:
    TEAM_LOGO_BASE_OFF = 0x58000
    TEAM_LOGO_HIGH_SIZE = 0x60
    TEAM_LOGO_LOW_SIZE = 0x60
    TEAM_LOGO_PIXEL_DIMS = (24,16)
    TEAM_LOGO_COLOR_MAP = [0x00000000,0x000000FF,0x63ADF7FF,0x317BDEFF,0x00BD00FF,0x00EF00FF,0xB52908FF,0xEFEF00FF,0x848484FF,0xADADADFF,0xC6C6C6FF,0x18529CFF,0xA55A00FF,0xDE7B00FF,0xCE9400FF,0xF7F7F7FF]
    TEAM_LOGO_MAPPING_HIGH = {
        0:0x200*0,
        1:0x200*2,
        2:0x200*4,
        3:0x200*6,
        4:0x200*8,
        5:0x200*10,
        6:0x200*12,
        7:0x200*14,
        8:0x200*0+0x60,
        9:0x200*2+0x60,
        10:0x200*4+0x60,
        11:0x200*6+0x60,
        12:0x200*8+0x60,
        13:0x200*10+0x60,
        14:0x200*12+0x60,
        15:0x200*14+0x60,
        16:0x200*0+0x60*2,
        17:0x200*2+0x60*2,
    }

    TEAM_LOGO_MAPPING_LOW_OFF = 0x200

    def __init__(self, rom, team_idx):
        self.rom = rom
        self.high_base = SBBS_Team_Logo.TEAM_LOGO_BASE_OFF+SBBS_Team_Logo.TEAM_LOGO_MAPPING_HIGH[team_idx]
        self.low_base = self.high_base + SBBS_Team_Logo.TEAM_LOGO_MAPPING_LOW_OFF
        self.high_bytes = self.rom.read_bytes(self.high_base,SBBS_Team_Logo.TEAM_LOGO_HIGH_SIZE)
        self.low_bytes = self.rom.read_bytes(self.low_base,SBBS_Team_Logo.TEAM_LOGO_HIGH_SIZE)
        self.color_map = [PIL.ImageColor.getrgb(f"#{v:08X}") for v in SBBS_Team_Logo.TEAM_LOGO_COLOR_MAP]
        print(self.color_map)
        self.high_tiles = [SNES_Tile_4bpp(self.high_bytes[0:32], self.color_map),
                           SNES_Tile_4bpp(self.high_bytes[32:64],self.color_map),
                           SNES_Tile_4bpp(self.high_bytes[64:96],self.color_map)]
        self.low_tiles = [SNES_Tile_4bpp(self.low_bytes[0:32], self.color_map),
                           SNES_Tile_4bpp(self.low_bytes[32:64],self.color_map),
                           SNES_Tile_4bpp(self.low_bytes[64:96],self.color_map)]

    def export_to(self, path):
        image = PIL.Image.new("RGBA", size=SBBS_Team_Logo.TEAM_LOGO_PIXEL_DIMS)
        for x_t in range(3):
            high_tile = self.high_tiles[x_t]
            low_tile = self.low_tiles[x_t]
            for x in range(8):
                for y in range(8):
                    image.putpixel((x_t*8+x,y), high_tile.get_pixel(x,y))
                    image.putpixel((x_t*8+x,y+8), low_tile.get_pixel(x,y))
        image.save(path)

    def import_from(self, path):
        image = PIL.Image.open(path)
        assert image.size[0] == 24
        assert image.size[1] == 16
        for x_t in range(3):
            high_tile = self.high_tiles[x_t]
            low_tile = self.low_tiles[x_t]
            x_off = 8*x_t
            for x in range(8):
                for y in range(8):
                    high_tile.set_pixel(x,y,image.getpixel((x_off+x,y)))
                    low_tile.set_pixel(x,y,image.getpixel((x_off+x,y+8)))

    def update_in_rom(self):
        for i in range(3):
            high_tile = self.high_tiles[i]
            low_tile = self.low_tiles[i]
            self.rom.replace_byte_range(self.high_base+i*0x20, high_tile.bs)
            self.rom.replace_byte_range(self.low_base+i*0x20, low_tile.bs)