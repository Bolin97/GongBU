MAXIMUM_LEN_OF_RESPONSE = 20

def reduce_size(l: list) -> list:
    if len(l) <= MAXIMUM_LEN_OF_RESPONSE:
        return l
    return l[::len(l) // MAXIMUM_LEN_OF_RESPONSE]