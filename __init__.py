def FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string, p1, p2):
    import re
    s = '@@ cat $$ @@dog$^'
    return re.findall(r'@@\s*([^$]*)\s*\$', s)
