#byte to font mapping, not complete, just the ones I'm interested in
b_to_font = """0123456789ABCDEFGHIJKLMNOPQRSTUV0123456789..WXYZ..........................T...............HE.... ..............."""
max_val = len(b_to_font)-1

font_to_b = []
for v in range(255):
    try:
        font_to_b.append(b_to_font.index(""+chr(v)))
    except Exception:
        font_to_b.append(-1)

def sbbs_byte_to_ascii_char(b:int):
    if b>max_val:
        return " "[0]
    return b_to_font[b]

def sbbs_bytes_to_str(data:bytes):
    return "".join([sbbs_byte_to_ascii_char(b) for b in data])

def str_to_sbbs_idxs(s:str):
    s_up = s.upper()
    return [font_to_b[ord(c)] for c in s_up]