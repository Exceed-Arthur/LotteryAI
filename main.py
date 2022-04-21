# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string, p1, p2):
    import re
    r = f'{p1}(.*?){p2}'
    s = full_string
    return re.findall(r, s)


def INJECT_URL_MODIFIERS_BETWEEN_2_STRINGS(url_prefix: str, url_suffix: str, injections: list):  # Returns a list of modified URLs
    mods = []
    for injection in injections:
        mods.append(f"{url_prefix}{injection}{url_suffix}")
    return mods


def ONE_TO_ONE_ODDS_EXTRACTOR(odds_expression: str):  # Returns Odd Ratio Expressed As Decimal, EG -> 0.2012 from [' 1 in 4.97** (']
    temp_array = ""
    for character in odds_expression.split("in ")[1]:
        if character.isdigit() or character == ".":
            temp_array = temp_array + character
    return float(temp_array)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')


f1 = "Overall odds of winning any prize in $5,000 Jackpot are 1 in 4.97** (see back of ticket for complete odds disclaimer)."
desired_output = "1 in 4.37"
print(FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=f1, p1="are", p2="see"))  # Gets odds expression for Odds extractor to extract
print(ONE_TO_ONE_ODDS_EXTRACTOR("[' 1 in 4.97** (']"))
