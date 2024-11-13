def decode(value: int, coding: dict):
    decode_data = dict()
    
    for k, pos in coding.items():
        mask = (2 ** pos[1]) - 1
        decode_data[k] = (value >> pos[0]) & mask
    
    return decode_data


def modify(value: int, name: str, reg_val: int, coding: dict):
    pos = coding[name]
    
    mask = (2 ** pos[1]) - 1
    shift_mask = mask << pos[0]
    # mask to set reg_val to zero
    reg_val = (reg_val | shift_mask) - shift_mask
    
    # check if value is out of bounds
    if value > mask or value < 0:
        return ValueError("input value out of bounds")
    
    # add new value
    reg_val |= value << pos[0]
    
    
    return reg_val


if __name__ == "__main__":
    a = 0xAA
    c = {
        "a1" : (7,1),
        "b1" : (6,1),
        "c2" : (4,2),
        "d3" : (0,4),
    }
    
    print(decode(a, c))
    print(hex(modify(3, "c2", a, c)))