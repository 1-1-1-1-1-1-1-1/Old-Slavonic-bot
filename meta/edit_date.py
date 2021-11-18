"""get the full date, short date, short copyright, full cright"""

import re


__all__ = ['full_date', 'short_date', 'short_cright', 'full_cright']


mdash = chr(8212)  # m-dash: "—"

# full date form --- begin
full_start = '27.01.2021'  # const
_full_till = (
    "28.02.2021", "06.03.2021", "07.03.2021", "12.05.2021", "13.05.2021",
    f"16.06.2021{mdash}31.08.2021", "17.11.2021"
)  # const
full_till = ", ".join(_full_till)
full_date = f'{full_start}{mdash}{full_till}'
# full date form --- end


# short date form --- begin
def get_year(string: str) -> str:
    pattern = r'\d+\.\d+\.(\d+)'
    try:
        return re.fullmatch(pattern, string).group(1)
    except:
        pattern = f'{pattern}{mdash}{pattern}'
        _result = re.fullmatch(pattern, string)
        gs = sorted(set(_result.groups()))
        if len(gs) == 1:
            return gs[0]
        return '{0}{dash}{1}'.format(*gs, dash=mdash)


short_start = get_year(full_start)
_short_date = sorted(
    set(
        map(get_year, full_date.split(', '))
    )
)
short_date = ', '.join(_short_date)
# short date form --- end

# copyrights: short and full --
short_cright = f'© Anonym, {short_date}'  # const: author
full_cright = f'© Anonym, {full_date}'


del re

# test
if __name__ == '__main__':
    test_objects = [
        short_cright, full_cright
    ]
    for item in test_objects:
        print(item)
