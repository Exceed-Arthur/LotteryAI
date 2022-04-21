def FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string, p1, p2):
    import re
    s = full_string
    return re.findall(r'@@\s*([^$]*)\s*\$', s)
